import '../design/form_surfaces.dart';
import '../design/readable_text.dart';

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../auth/session.dart';
import '../core/api_client.dart';
import '../adoption/adoption_screens.dart' show StatusPanel, messageFor;
import '../design/refined_surfaces.dart';
import '../design/lpn_app_bar.dart';

const _activityFields = {
  'titulo': ('Actividad', 100),
  'descripcion': ('Qué harás', 500),
  'horario': ('Horario', 160),
  'requisitos': ('Requisitos', 300),
};
const _channelFields = {
  'titulo': ('Nombre del canal', 100),
  'descripcion': ('Para qué sirve y cómo confirmar el aporte', 300),
  'url': ('Enlace oficial HTTPS', 300),
};

List<Map<String, String>> programRows(Object? value, {bool channels = false}) {
  final fields = channels ? _channelFields : _activityFields;
  if (value is! List || value.length > (channels ? 4 : 8)) {
    throw const FormatException('Listado de convocatoria no válido.');
  }
  return value.map((row) {
    if (row is! Map ||
        fields.keys.any(
          (key) =>
              row[key] is! String ||
              (row[key] as String).trim().isEmpty ||
              (row[key] as String).runes.length > fields[key]!.$2,
        )) {
      throw const FormatException('Información de convocatoria incompleta.');
    }
    final clean = {for (final key in fields.keys) key: row[key] as String};
    if (channels) {
      final uri = Uri.tryParse(clean['url']!);
      if (uri == null ||
          uri.scheme != 'https' ||
          uri.host.isEmpty ||
          uri.userInfo.isNotEmpty) {
        throw const FormatException(
          'El canal no tiene un enlace HTTPS válido.',
        );
      }
    }
    return clean;
  }).toList();
}

/// Only explicit public fields. Reading and copying a channel never fetches it.
class HelpProgramInfo extends StatelessWidget {
  const HelpProgramInfo({
    super.key,
    required this.row,
    this.onActivity,
    this.showActivities = true,
  });
  final Map<String, dynamic> row;
  final ValueChanged<String>? onActivity;
  final bool showActivities;
  @override
  Widget build(BuildContext context) {
    final value = row['programa_ayuda'];
    if (value is! Map) return const SizedBox.shrink();
    late List<Map<String, String>> activities, channels;
    try {
      activities = programRows(value['actividades']);
      channels = programRows(value['canales'], channels: true);
    } on FormatException {
      return const Text(
        'La convocatoria no está disponible. Consulta con la organización.',
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (showActivities && activities.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text(
            'Actividades de voluntariado',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          for (final activity in activities)
            ExpansionTile(
              tilePadding: EdgeInsets.zero,
              title: Text(activity['titulo']!),
              subtitle: Text(activity['horario']!),
              childrenPadding: const EdgeInsets.only(bottom: 16),
              expandedCrossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(activity['descripcion']!),
                const SizedBox(height: 8),
                Text('Requisitos: ${activity['requisitos']}'),
                if (onActivity != null)
                  Align(
                    alignment: AlignmentDirectional.centerStart,
                    child: TextButton(
                      onPressed: () => onActivity!(activity['titulo']!),
                      child: const Text('Me interesa esta actividad'),
                    ),
                  ),
                const SizedBox(height: 8),
                const Text(
                  'Manifestar interés no reserva una plaza. La organización acuerda contigo la participación.',
                ),
              ],
            ),
        ],
        if (channels.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text(
            'Canales publicados por la organización',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          for (final channel in channels) ...[
            const SizedBox(height: 12),
            Text(
              channel['titulo']!,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 4),
            Text(channel['descripcion']!),
            const SizedBox(height: 4),
            ReadableText(channel['url']!),
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: TextButton.icon(
                icon: const Icon(Icons.copy_outlined, size: 18),
                label: Text('Copiar enlace de ${channel['titulo']}'),
                onPressed: () async {
                  await Clipboard.setData(ClipboardData(text: channel['url']!));
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Enlace copiado.')),
                    );
                  }
                },
              ),
            ),
          ],
          const Text(
            'La organización declara estos canales como propios. Little Paws Net no verifica su titularidad ni procesa o confirma pagos.',
          ),
        ],
      ],
    );
  }
}

class HelpProgramEditor extends StatelessWidget {
  const HelpProgramEditor({
    super.key,
    required this.api,
    required this.session,
    required this.id,
  });
  final ApiClient api;
  final Session session;
  final int id;
  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: session,
    builder: (context, _) => session.signedIn
        ? _ProgramForm(
            key: ValueKey((
              session.identityRevision,
              session.account!.email,
              id,
            )),
            api: api,
            session: session,
            id: id,
          )
        : Scaffold(
            appBar: lpnAppBar(context, 'Convocatoria pública'),
            body: const StatusPanel(
              message: 'La sesión terminó. Vuelve a iniciar sesión.',
            ),
          ),
  );
}

class _ProgramForm extends StatefulWidget {
  const _ProgramForm({
    super.key,
    required this.api,
    required this.session,
    required this.id,
  });
  final ApiClient api;
  final Session session;
  final int id;
  @override
  State<_ProgramForm> createState() => _ProgramFormState();
}

class _ProgramFormState extends State<_ProgramForm> {
  final _form = GlobalKey<FormState>();
  final List<Map<String, TextEditingController>> _activities = [],
      _channels = [];
  String _version = '', _saved = '';
  bool _published = false,
      _consent = false,
      _loaded = false,
      _busy = false,
      _leave = false,
      _denied = false,
      _uncertain = false;
  String? _error;
  late Future<void> _data = _load();
  String get _path => '/api/ayudas/organizaciones/${widget.id}/programa/';
  Map<String, Object?> get _payload => {
    'actividades': [
      for (final row in _activities)
        {for (final field in row.entries) field.key: field.value.text.trim()},
    ],
    'canales': [
      for (final row in _channels)
        {for (final field in row.entries) field.key: field.value.text.trim()},
    ],
    'publicada': _published,
  };
  bool get _dirty => _loaded && jsonEncode(_payload) != _saved;

  Future<void> _load() async {
    final raw = await widget.session.authorized(
      (token) => widget.api.get(_path, token: token),
    );
    if (raw is! Map || raw['version'] is! String || raw['publicada'] is! bool) {
      throw const ApiException('Respuesta de convocatoria no válida.');
    }
    final activities = programRows(raw['actividades']);
    final channels = programRows(raw['canales'], channels: true);
    if (!mounted) return;
    setState(() {
      final previous = [..._activities, ..._channels];
      _activities.clear();
      _channels.clear();
      WidgetsBinding.instance.addPostFrameCallback((_) {
        for (final row in previous) {
          for (final controller in row.values) {
            controller.dispose();
          }
        }
      });
      _consent = false;
      _version = raw['version'] as String;
      _published = raw['publicada'] as bool;
      for (final row in activities) {
        _activities.add(_controllers(row));
      }
      for (final row in channels) {
        _channels.add(_controllers(row));
      }
      _saved = jsonEncode(_payload);
      _loaded = true;
    });
  }

  Map<String, TextEditingController> _controllers(Map<String, String> values) =>
      {
        for (final field in values.entries)
          field.key: TextEditingController(text: field.value),
      };
  @override
  void dispose() {
    for (final row in [..._activities, ..._channels]) {
      for (final controller in row.values) {
        controller.dispose();
      }
    }
    super.dispose();
  }

  Future<void> _cancel() async {
    if (_busy) return;
    if (_dirty && !_denied) {
      final discard = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('¿Descartar cambios?'),
          content: Text(
            _uncertain
                ? 'El guardado podría haberse completado. Salir no lo revierte; consulta la convocatoria antes de repetir.'
                : 'La publicación guardada no se modificará.',
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
      if (discard != true || !mounted) return;
    }
    if (!mounted) return;
    setState(() => _leave = true);
    await Future<void>.delayed(Duration.zero);
    if (mounted) Navigator.pop(context);
  }

  Future<void> _reload() async {
    if (_busy) return;
    if (_dirty) {
      final replace = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          scrollable: true,
          title: const Text('¿Volver a consultar?'),
          content: const Text(
            'Se reemplazará el borrador por la versión guardada. Si hubo un fallo de conexión, el guardado puede haberse completado.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Seguir editando'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Consultar servidor'),
            ),
          ],
        ),
      );
      if (replace != true || !mounted) return;
    }
    setState(() {
      _loaded = false;
      _denied = false;
      _uncertain = false;
      _error = null;
      _data = _load();
    });
  }

  Future<void> _save() async {
    if (_busy || _uncertain || !_dirty || !validateLpnForm(_form)) {
      return;
    }
    if (_published && !_consent) {
      await showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          scrollable: true,
          title: const Text('Autoriza la publicación'),
          content: const Text(
            'Marca la autorización de la organización antes de publicar.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Entendido'),
            ),
          ],
        ),
      );
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final response = await widget.session.authorized(
        (token) => widget.api.patch(_path, {
          ..._payload,
          'version': _version,
          'confirmar_publicacion': _consent,
        }, token: token),
      );
      if (response is! Map ||
          response['version'] is! String ||
          jsonEncode({
                'actividades': response['actividades'],
                'canales': response['canales'],
                'publicada': response['publicada'],
              }) !=
              jsonEncode(_payload)) {
        throw const ApiException(
          'No pudimos confirmar lo guardado. Vuelve a consultar antes de reintentar.',
        );
      }
      if (!mounted) return;
      setState(() {
        _version = response['version'] as String;
        _saved = jsonEncode(_payload);
        _consent = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            _published
                ? 'Convocatoria publicada.'
                : 'Convocatoria guardada sin publicar.',
          ),
        ),
      );
    } on Exception catch (e) {
      if (!mounted) return;
      setState(() {
        _error = messageFor(
          e,
          'No pudimos confirmar el guardado. Vuelve a consultar antes de reintentar.',
        );
        _denied = e is ApiException && (e.status == 401 || e.status == 403);
        _uncertain =
            e is! ApiException ||
            e.status == null ||
            e.status == 409 ||
            e.status! >= 500;
      });
      if (!_denied) {
        setState(() => _busy = false);
        await showDialog<void>(
          context: context,
          builder: (context) => AlertDialog(
            scrollable: true,
            title: const Text('No se confirmó el guardado'),
            content: Text(_error!),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Entendido'),
              ),
            ],
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Widget _group(bool channels) {
    final rows = channels ? _channels : _activities;
    final fields = channels ? _channelFields : _activityFields;
    final limit = channels ? 4 : 8;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          channels
              ? 'Canales oficiales de aporte'
              : 'Actividades de voluntariado',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 8),
        for (var i = 0; i < rows.length; i++)
          FormCard(
            title: '${channels ? 'Canal' : 'Actividad'} ${i + 1}',
            icon: channels ? Icons.link : Icons.volunteer_activism_outlined,
            tone: channels ? 0 : 1,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (final field in fields.entries) ...[
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: rows[i][field.key],
                    enabled: !_busy && !_uncertain,
                    maxLength: field.value.$2,
                    buildCounter: (
                      _, {
                      required currentLength,
                      required isFocused,
                      maxLength,
                    }) => null,
                    minLines: field.key == 'descripcion' ? 2 : 1,
                    maxLines: field.key == 'descripcion'
                        ? 4
                        : field.key == 'requisitos'
                        ? 3
                        : 1,
                    keyboardType: field.key == 'url'
                        ? TextInputType.url
                        : TextInputType.multiline,
                    autocorrect: field.key != 'url',
                    decoration: InputDecoration(
                      labelText: field.value.$1,
                      alignLabelWithHint: true,
                    ),
                    onChanged: (_) => setState(() {}),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Completa este dato o quita la entrada.';
                      }
                      if (field.key == 'url') {
                        final uri = Uri.tryParse(value.trim());
                        if (uri == null ||
                            uri.scheme != 'https' ||
                            uri.host.isEmpty ||
                            uri.userInfo.isNotEmpty) {
                          return 'Usa un enlace HTTPS sin credenciales.';
                        }
                      }
                      return null;
                    },
                  ),
                ],
                Align(
                  alignment: AlignmentDirectional.centerStart,
                  child: TextButton.icon(
                    onPressed: _busy || _uncertain
                        ? null
                        : () {
                            final removed = rows.removeAt(i);
                            // Dispose after the fields using these controllers unmount.
                            WidgetsBinding.instance.addPostFrameCallback((_) {
                              for (final c in removed.values) {
                                c.dispose();
                              }
                            });
                            setState(() {});
                          },
                    icon: const Icon(Icons.remove_circle_outline, size: 18),
                    label: Text(
                      'Quitar ${channels ? 'canal' : 'actividad'} ${i + 1}',
                    ),
                  ),
                ),
              ],
            ),
          ),
        if (rows.length < limit)
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: TextButton.icon(
              onPressed: _busy || _uncertain
                  ? null
                  : () => setState(
                      () => rows.add(
                        _controllers({for (final key in fields.keys) key: ''}),
                      ),
                    ),
              icon: const Icon(Icons.add),
              label: Text(channels ? 'Añadir canal' : 'Añadir actividad'),
            ),
          ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) => PopScope(
    canPop: _leave || (!_dirty && !_busy),
    onPopInvokedWithResult: (didPop, _) {
      if (!didPop) _cancel();
    },
    child: Scaffold(
      appBar: AppBar(
        title: const Text('Convocatoria pública'),
        actions: [
          IconButton(
            tooltip: 'Actualizar convocatoria pública',
            onPressed: _busy || !_loaded ? null : _reload,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      bottomNavigationBar: _loaded
          ? LpnKeyboardSafeArea(
              top: false,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Wrap(
                      alignment: WrapAlignment.end,
                      spacing: 12,
                      runSpacing: 8,
                      children: [
                        if (_uncertain)
                          TextButton.icon(
                            onPressed: _busy ? null : _reload,
                            icon: const Icon(Icons.refresh),
                            label: const Text('Consultar servidor'),
                          ),
                        TextButton(
                          onPressed: _busy ? null : _cancel,
                          child: const Text('Cancelar'),
                        ),
                        if (!_denied)
                          FilledButton(
                            onPressed: _busy || !_dirty || _uncertain
                                ? null
                                : _save,
                            child: Text(
                              _busy ? 'Guardando…' : 'Guardar convocatoria',
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            )
          : null,
      body: _denied
          ? StatusPanel(
              message:
                  _error ??
                  'Permiso revocado. No puedes editar esta convocatoria.',
            )
          : FutureBuilder<void>(
              future: _data,
              builder: (context, snapshot) {
                if (snapshot.hasError) {
                  return StatusPanel(
                    message: messageFor(
                      snapshot.error,
                      'No pudimos consultar la convocatoria.',
                    ),
                    action: _reload,
                    actionLabel: 'Reintentar',
                  );
                }
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }
                return Form(
                  key: _form,
                  child: LpnFormScrollView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      const Text(
                        'Define actividades y canales autorizados. La plataforma no procesa pagos ni verifica la titularidad de los enlaces.',
                      ),
                      const SizedBox(height: 24),
                      _group(false),
                      const SizedBox(height: 24),
                      _group(true),
                      const SizedBox(height: 16),
                      SwitchListTile.adaptive(
                        contentPadding: EdgeInsets.zero,
                        title: const Text('Publicar convocatoria'),
                        value: _published,
                        subtitle: const Text(
                          'Desactiva y guarda para retirar actividades y canales.',
                        ),
                        onChanged: _busy || _uncertain
                            ? null
                            : (value) => setState(() {
                                _published = value;
                                _consent = false;
                              }),
                      ),
                      if (_published)
                        CheckboxListTile(
                          contentPadding: EdgeInsets.zero,
                          title: const Text(
                            'La organización autoriza publicar esta información y declara estos canales como propios.',
                          ),
                          value: _consent,
                          onChanged: _busy || _uncertain
                              ? null
                              : (value) =>
                                    setState(() => _consent = value == true),
                        ),
                    ],
                  ),
                );
              },
            ),
    ),
  );
}
