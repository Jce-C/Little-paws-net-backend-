import '../core/operation_key.dart';
import 'owned_pets_api.dart';
import 'owned_pets_screens.dart';
import '../design/readable_text.dart';
import '../core/inline_webp.dart';
import '../adoption/adoption_screens.dart' show StatusPanel, messageFor;

import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart' show ImageSource;

import '../auth/session.dart';
import '../core/api_client.dart';
import '../design/lpn_app_bar.dart';
import '../design/form_surfaces.dart';
import '../design/photo_attachment.dart';
import '../explore/session_action_gate.dart';

Future<bool> openPersonalPet(BuildContext context, Session session) async =>
    await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => PersonalPetScreen(session: session)),
    ) ??
    false;

class PersonalPetScreen extends StatelessWidget {
  const PersonalPetScreen({super.key, required this.session, this.choosePhoto});
  final Session session;
  final Future<Uint8List?> Function(ImageSource)? choosePhoto;
  @override
  Widget build(BuildContext context) => SessionActionGate(
    session: session,
    title: 'Agregar mascota',
    message: 'Inicia sesión para registrar tu mascota personal.',
    form: (identity) => _PersonalPetForm(
      key: identity,
      session: session,
      choosePhoto: choosePhoto,
    ),
  );
}

class _PersonalPetForm extends StatefulWidget {
  const _PersonalPetForm({super.key, required this.session, this.choosePhoto});
  final Session session;
  final Future<Uint8List?> Function(ImageSource)? choosePhoto;
  @override
  State<_PersonalPetForm> createState() => _PersonalPetFormState();
}

class _PersonalPetFormState extends State<_PersonalPetForm> {
  final _form = GlobalKey<FormState>();
  final fields = {
    for (final key in [
      'nombre',
      'especie',
      'raza',
      'edad_meses',
      'sexo',
      'tamano',
      'color',
      'descripcion',
    ])
      key: TextEditingController(),
  };
  Uint8List? _photo;
  bool _pickingPhoto = false;
  bool _busy = false, _uncertain = false, _leaving = false, _confirming = false;
  String? _error;
  String? _operationKey;
  bool get _dirty =>
      _photo != null || fields.values.any((c) => c.text.isNotEmpty);
  @override
  void dispose() {
    for (final field in fields.values) {
      field.dispose();
    }
    super.dispose();
  }

  Future<void> _leave() async {
    if (_busy || _pickingPhoto || _confirming) return;
    if (_dirty) {
      _confirming = true;
      final discard = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('¿Descartar esta mascota?'),
          content: Text(
            _uncertain
                ? 'El registro podría haberse guardado. Salir no lo cancela; compruébalo en Mis mascotas antes de repetirlo.'
                : 'Todavía no se ha registrado.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Seguir editando'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Descartar'),
            ),
          ],
        ),
      );
      _confirming = false;
      if (discard != true || !mounted) return;
    }
    setState(() => _leaving = true);
    await WidgetsBinding.instance.endOfFrame;
    if (mounted) Navigator.pop(context);
  }

  Future<void> _save({bool recover = false}) async {
    if (_busy ||
        _pickingPhoto ||
        (_uncertain && !recover) ||
        !validateLpnForm(_form)) {
      return;
    }
    if (recover && widget.session.account?.safeRetries != true) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    final body = <String, Object?>{
      for (final e in fields.entries)
        if (e.value.text.trim().isNotEmpty) e.key: e.value.text.trim(),
    };
    if (body.containsKey('edad_meses')) {
      body['edad_meses'] = int.parse(body['edad_meses'] as String);
    }
    _operationKey ??= newOperationKey();
    try {
      final result = await widget.session.authorized(
        (token) => _photo == null
            ? widget.session.api.post(
                '/api/mascotas/personales/',
                body,
                token: token,
                operationKey: _operationKey,
              )
            : widget.session.api.uploadImage(
                '/api/mascotas/personales/',
                body,
                _photo!,
                token: token,
                operationKey: _operationKey,
              ),
      );
      if (result is! Map ||
          result['id_mascota'] is! int ||
          (result['id_mascota'] as int) <= 0) {
        throw const ApiException(
          'No pudimos confirmar el registro. Revisa Mis mascotas antes de repetirlo.',
        );
      }
      if (mounted) {
        setState(() => _leaving = true);
        await WidgetsBinding.instance.endOfFrame;
        if (mounted) Navigator.pop(context, true);
      }
    } on Exception catch (e) {
      if (mounted) {
        setState(() {
          _busy = false;
          _uncertain =
              e is! ApiException || e.status == null || e.status! >= 500;
          if (!_uncertain) _operationKey = null;
          _error = _uncertain
              ? (widget.session.account?.safeRetries == true
                    ? 'No se confirmó el registro. Puedes comprobar y completar la misma operación sin duplicarla.'
                    : 'No se confirmó el registro y este servidor no admite reintentos seguros. Revisa Mis mascotas antes de registrar de nuevo.')
              : (e is ApiException
                    ? e.message
                    : 'No pudimos registrar esta mascota.');
        });
        await showDialog<void>(
          context: context,
          builder: (context) => AlertDialog(
            scrollable: true,
            title: Text(
              _uncertain ? 'Comprueba el registro' : 'Revisa los datos',
            ),
            content: Text(_error!),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Cerrar'),
              ),
            ],
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Widget _field(
    String key,
    String label, {
    bool required = false,
    bool numeric = false,
    int lines = 1,
  }) => Padding(
    padding: const EdgeInsets.only(bottom: 16),
    child: TextFormField(
      key: Key('personal-$key'),
      controller: fields[key],
      autovalidateMode: AutovalidateMode.onUserInteraction,
      enabled: !_busy && !_uncertain,
      keyboardType: numeric ? TextInputType.number : TextInputType.text,
      maxLines: lines,
      maxLength: const {
        'nombre': 120,
        'especie': 100,
        'raza': 120,
        'edad_meses': 3,
        'sexo': 60,
        'tamano': 60,
        'color': 100,
        'descripcion': 2000,
      }[key],
      decoration: InputDecoration(labelText: label, counterText: ''),
      validator: (v) {
        if (required && (v ?? '').trim().isEmpty) return 'Completa este dato.';
        if (numeric &&
            (v ?? '').trim().isNotEmpty &&
            (int.tryParse(v!.trim()) == null ||
                int.parse(v.trim()) < 0 ||
                int.parse(v.trim()) > 600)) {
          return 'Usa entre 0 y 600 meses.';
        }
        return null;
      },
    ),
  );
  @override
  Widget build(BuildContext context) => PopScope(
    canPop: _leaving,
    onPopInvokedWithResult: (didPop, _) {
      if (!didPop) _leave();
    },
    child: Scaffold(
      appBar: lpnAppBar(
        context,
        'Agregar mascota',
        leading: BackButton(onPressed: _leave),
      ),
      bottomNavigationBar: LpnActionBar(
        avoidKeyboard: true,
        child: Wrap(
          alignment: WrapAlignment.end,
          spacing: 8,
          runSpacing: 4,
          children: [
            TextButton(
              key: const Key('personal-cancel'),
              onPressed: _busy || _pickingPhoto ? null : _leave,
              child: const Text('Cancelar'),
            ),
            if (_uncertain) ...[
              if (widget.session.account?.safeRetries == true)
                FilledButton(
                  onPressed: _busy ? null : () => _save(recover: true),
                  child: const Text('Comprobar registro'),
                ),
              TextButton(
                onPressed: _busy
                    ? null
                    : () => Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => OwnedPetsScreen(
                            api: OwnedPetsApi(
                              widget.session.api,
                              widget.session,
                            ),
                          ),
                        ),
                      ),
                child: const Text('Ver mis mascotas'),
              ),
            ] else
              FilledButton(
                key: const Key('personal-save'),
                onPressed: _busy || _pickingPhoto ? null : _save,
                child: Text(_busy ? 'Guardando…' : 'Registrar mascota'),
              ),
          ],
        ),
      ),
      body: Form(
        key: _form,
        child: LpnFormScrollView(
          padding: EdgeInsets.symmetric(
            vertical: 16,
            horizontal: ((MediaQuery.sizeOf(context).width - 640) / 2).clamp(
              16.0,
              double.infinity,
            ),
          ),
          children: [
            const Text(
              'Tu mascota personal',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            const Text(
              'Quedará asociada a tu cuenta. No se publicará en adopciones.',
            ),
            const SizedBox(height: 20),
            LpnFormSection(
              title: 'Datos de tu mascota',
              icon: Icons.pets_outlined,
              tone: 1,
              children: [
                _field('nombre', 'Nombre', required: true),
                _field('especie', 'Especie', required: true),
              ],
            ),
            const SizedBox(height: 16),
            LpnFormSection(
              title: 'Más detalles (opcionales)',
              icon: Icons.info_outline,
              tone: 2,
              children: [
                _field('raza', 'Raza (opcional)'),
                _field('edad_meses', 'Edad aproximada en meses', numeric: true),
                _field('sexo', 'Sexo'),
                _field('tamano', 'Tamaño'),
                _field('color', 'Color'),
                _field('descripcion', 'Descripción', lines: 3),
              ],
            ),
            const SizedBox(height: 16),
            LpnFormSection(
              title: 'Fotografía de tu mascota',
              description: 'Se guarda en tu ficha privada. No se publica en el catálogo de adopciones.',
              icon: Icons.camera_alt_outlined,
              children: [
                PhotoAttachment(
                  value: _photo,
                  choose: widget.choosePhoto,
                  onBusyChanged: (busy) {
                    if (mounted) setState(() => _pickingPhoto = busy);
                  },
                  onChanged: (v) => setState(() => _photo = v),
                  enabled: !_busy && !_uncertain,
                ),
              ],
            ),
          ],
        ),
      ),
    ),
  );
}

class PersonalPetDetailsScreen extends StatelessWidget {
  const PersonalPetDetailsScreen({
    super.key,
    required this.session,
    required this.id,
  });
  final Session session;
  final int id;
  @override
  Widget build(BuildContext context) => SessionActionGate(
    session: session,
    title: 'Ficha de tu mascota',
    message: 'Inicia sesión para consultar tu mascota.',
    form: (identity) =>
        _PersonalDetails(key: identity, session: session, id: id),
  );
}

class _PersonalDetails extends StatefulWidget {
  const _PersonalDetails({super.key, required this.session, required this.id});
  final Session session;
  final int id;
  @override
  State<_PersonalDetails> createState() => _PersonalDetailsState();
}

class _PersonalDetailsState extends State<_PersonalDetails> {
  late Future<Object?> _data = _load();
  bool _refreshing = true;
  Future<Object?> _load() => widget.session
      .authorized(
        (token) => widget.session.api.get(
          '/api/mascotas/personales/${widget.id}/',
          token: token,
        ),
      )
      .whenComplete(() {
        if (mounted) setState(() => _refreshing = false);
      });
  Future<void> _refresh() async {
    if (_refreshing) return;
    _refreshing = true;
    final next = _load();
    setState(() {
      _data = next;
    });
    try {
      await next;
    } on Exception {
      /* The panel offers retry. */
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(
      context,
      'Ficha de tu mascota',
      actions: [
        IconButton(
          tooltip: 'Actualizar ficha',
          onPressed: _refreshing ? null : _refresh,
          icon: const Icon(Icons.refresh),
        ),
      ],
    ),
    body: FutureBuilder<Object?>(
      future: _data,
      builder: (context, state) {
        if (state.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (state.hasError || state.data is! Map) {
          return StatusPanel(
            message: messageFor(
              state.error,
              'No pudimos consultar esta mascota.',
            ),
            action: _refresh,
            actionLabel: 'Reintentar',
          );
        }
        final row = state.data as Map;
        if (row['id_mascota'] != widget.id) {
          return const StatusPanel(message: 'No pudimos verificar esta ficha.');
        }
        final photo = inlineWebp(row['foto_miniatura']);
        return ListView(
          padding: EdgeInsets.symmetric(
            vertical: 16,
            horizontal: ((MediaQuery.sizeOf(context).width - 640) / 2).clamp(
              16.0,
              double.infinity,
            ),
          ),
          children: [
            LpnFormSection(
              title: row['nombre']?.toString() ?? 'Tu mascota',
              icon: Icons.pets_outlined,
              tone: 1,
              children: [
                if (photo != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: Image.memory(
                        photo,
                        height: 160,
                        fit: BoxFit.contain,
                        semanticLabel: 'Fotografía privada de tu mascota',
                      ),
                    ),
                  ),
                for (final key in {
                  'especie': 'Especie',
                  'raza': 'Raza',
                  'fecha_nacimiento': 'Nacimiento aproximado',
                  'sexo': 'Sexo',
                  'tamano': 'Tamaño',
                  'color': 'Color',
                  'descripcion': 'Descripción',
                }.entries)
                  if (row[key.key] is String &&
                      (row[key.key] as String).isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            key.value,
                            style: const TextStyle(fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 4),
                          ReadableText(
                            key.key == 'fecha_nacimiento' &&
                                    DateTime.tryParse(row[key.key] as String) !=
                                        null
                                ? MaterialLocalizations.of(context)
                                      .formatMediumDate(
                                        DateTime.parse(row[key.key] as String),
                                      )
                                : row[key.key] as String,
                          ),
                        ],
                      ),
                    ),
              ],
            ),
          ],
        );
      },
    ),
  );
}
