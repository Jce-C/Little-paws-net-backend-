import '../design/form_surfaces.dart';

import 'package:flutter/material.dart';

import 'help_program.dart';
import 'help_offer_card.dart';
import '../design/refined_surfaces.dart';

import '../auth/session.dart';
import '../auth/account_screen.dart';
import '../core/api_client.dart';
import '../design/lpn_app_bar.dart';
import '../adoption/adoption_screens.dart' show StatusPanel, messageFor;

class HelpManagementShortcut extends StatelessWidget {
  const HelpManagementShortcut({
    super.key,
    required this.api,
    required this.session,
  });
  final ApiClient api;
  final Session session;
  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: session,
    builder: (context, _) => session.signedIn
        ? _ManagementAccess(
            key: ValueKey((session.identityRevision, session.account!.email)),
            api: api,
            session: session,
          )
        : const SizedBox.shrink(),
  );
}

class _ManagementAccess extends StatefulWidget {
  const _ManagementAccess({
    super.key,
    required this.api,
    required this.session,
  });
  final ApiClient api;
  final Session session;
  @override
  State<_ManagementAccess> createState() => _ManagementAccessState();
}

class _ManagementAccessState extends State<_ManagementAccess> {
  late Future<Object?> _data = _load();
  Future<Object?> _load() {
    final next = widget.session.authorized(
      (token) => widget.api.get('/api/ayudas/organizaciones/', token: token),
    );
    // A retry can fail before the next frame attaches FutureBuilder's listener.
    // Keep the original failure for the builder while observing it immediately.
    next.ignore();
    return next;
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<Object?>(
    future: _data,
    builder: (context, snapshot) {
      if (snapshot.hasError) {
        final error = snapshot.error;
        if (error is ApiException &&
            (error.status == 401 || error.status == 403)) {
          return const SizedBox.shrink();
        }
        return TextButton(
          onPressed: () {
            final next = _load();
            setState(() {
              _data = next;
            });
          },
          child: const Text('Comprobar acceso de gestión'),
        );
      }
      if (snapshot.data is! List || (snapshot.data as List).isEmpty) {
        return const SizedBox.shrink();
      }
      return OutlinedButton.icon(
        icon: const Icon(Icons.business_outlined),
        label: const Text('Gestionar ayudas de mi organización'),
        onPressed: () => Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) =>
                ManageHelpScreen(api: widget.api, session: widget.session),
          ),
        ),
      );
    },
  );
}

class ManageHelpScreen extends StatelessWidget {
  const ManageHelpScreen({super.key, required this.api, required this.session});
  final ApiClient api;
  final Session session;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Mis organizaciones'),
    body: ListenableBuilder(
      listenable: session,
      builder: (context, _) => !session.signedIn
          ? StatusPanel(
              message: 'Inicia sesión para consultar las organizaciones que puedes gestionar.',
              action: () => openLogin(context, session),
              actionLabel: 'Iniciar sesión',
            )
          : _Organizations(
              key: ValueKey((session.identityRevision, session.account!.email)),
              api: api,
              session: session,
            ),
    ),
  );
}

class _Organizations extends StatefulWidget {
  const _Organizations({super.key, required this.api, required this.session});
  final ApiClient api;
  final Session session;
  @override
  State<_Organizations> createState() => _OrganizationsState();
}

class _OrganizationsState extends State<_Organizations> {
  late Future<Object?> _data = _load();
  Future<Object?> _load() => widget.session.authorized(
    (token) => widget.api.get('/api/ayudas/organizaciones/', token: token),
  );
  @override
  Widget build(BuildContext context) => FutureBuilder<Object?>(
    future: _data,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return const Center(child: CircularProgressIndicator());
      }
      if (snapshot.hasError) {
        return StatusPanel(
          message: messageFor(
            snapshot.error,
            'No pudimos consultar tus organizaciones.',
          ),
          action: () => setState(() => _data = _load()),
          actionLabel: 'Reintentar',
        );
      }
      final value = snapshot.data;
      if (value is! List ||
          value.any(
            (row) =>
                row is! Map || row['id'] is! int || row['nombre'] is! String,
          )) {
        return const StatusPanel(
          message: 'La respuesta de organizaciones no es válida.',
        );
      }
      return ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Convocatorias y ofrecimientos de organizaciones donde tienes permiso para gestionar ayudas.',
          ),
          const SizedBox(height: 16),
          if (value.isEmpty)
            const StatusPanel(
              message: 'Tu cuenta no tiene organizaciones con permiso para gestionar ayudas.',
            ),
          for (final row in value)
            Card(
              child: ListTile(
                title: Text('${row['nombre']}'),
                subtitle: const Text('Convocatoria y ofrecimientos recibidos'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => OrganizationHelpScreen(
                      api: widget.api,
                      session: widget.session,
                      id: row['id'] as int,
                    ),
                  ),
                ),
              ),
            ),
        ],
      );
    },
  );
}

class OrganizationHelpScreen extends StatelessWidget {
  const OrganizationHelpScreen({
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
        ? _OrganizationHelpBody(
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
            appBar: lpnAppBar(context, 'Convocatoria'),
            body: const StatusPanel(
              message: 'La sesión terminó. Vuelve a iniciar sesión para consultar información de tu organización.',
            ),
          ),
  );
}

class _OrganizationHelpBody extends StatefulWidget {
  const _OrganizationHelpBody({
    super.key,
    required this.api,
    required this.session,
    required this.id,
  });
  final ApiClient api;
  final Session session;
  final int id;
  @override
  State<_OrganizationHelpBody> createState() => _OrganizationHelpBodyState();
}

class _OrganizationHelpBodyState extends State<_OrganizationHelpBody> {
  final _needs = TextEditingController();
  bool _confirming = false;
  bool _accept = false,
      _savedAccept = false,
      _loaded = false,
      _busy = false,
      _denied = false,
      _allowLeave = false,
      _uncertain = false;
  String _savedNeeds = '', _version = '';
  String? _error;
  late Future<Map<String, dynamic>> _data = _load();
  bool get _dirty =>
      _loaded && (_accept != _savedAccept || _needs.text != _savedNeeds);
  String get _path => '/api/ayudas/organizaciones/${widget.id}/';
  @override
  void dispose() {
    _needs.dispose();
    super.dispose();
  }

  Future<Map<String, dynamic>> _load() async {
    final value = await widget.session.authorized(
      (token) => widget.api.get(_path, token: token),
    );
    if (value is! Map<String, dynamic> ||
        value['id'] != widget.id ||
        value['nombre'] is! String ||
        value['version'] is! String ||
        value['acepta_voluntarios'] is! bool ||
        value['necesidades_ayuda'] is! String ||
        value['ofrecimientos'] is! List ||
        (value['ofrecimientos'] as List).any(
          (row) =>
              row is! Map ||
              row['nombre'] is! String ||
              row['mensaje'] is! String ||
              row['modalidad'] is! String ||
              row['fecha'] is! String,
        )) {
      throw const ApiException('No pudimos interpretar la convocatoria.');
    }
    if (mounted) {
      setState(() {
        _version = value['version'] as String;
        _accept = _savedAccept = value['acepta_voluntarios'] as bool;
        _needs.text = _savedNeeds = value['necesidades_ayuda'] as String;
        _loaded = true;
      });
    }
    return value;
  }

  Future<bool> _confirmDiscard({bool reload = false}) async =>
      await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          scrollable: true,
          title: Text(reload ? '¿Volver a consultar?' : '¿Descartar cambios?'),
          content: Text(
            _uncertain
                ? (reload
                      ? 'El guardado podría haberse completado. Se reemplazará el borrador por la versión del servidor.'
                      : 'El guardado podría haberse completado. Salir no lo revierte; vuelve a consultar la convocatoria antes de repetirlo.')
                : 'Puedes seguir editando o descartar los cambios del formulario.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Seguir editando'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: Text(reload ? 'Consultar servidor' : 'Descartar'),
            ),
          ],
        ),
      ) ??
      false;
  Future<void> _reload() async {
    if (_busy || (_dirty && !await _confirmDiscard(reload: true)) || !mounted) {
      return;
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
    if (_busy || !_dirty || _uncertain) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final value = await widget.session.authorized(
        (token) => widget.api.patch(_path, {
          'version': _version,
          'acepta_voluntarios': _accept,
          'necesidades_ayuda': _needs.text.trim(),
        }, token: token),
      );
      if (value is! Map ||
          value['id'] != widget.id ||
          value['version'] is! String ||
          value['acepta_voluntarios'] is! bool ||
          value['necesidades_ayuda'] is! String) {
        throw const ApiException('No pudimos confirmar la actualización.');
      }
      if (mounted) {
        setState(() {
          _version = value['version'] as String;
          _accept = _savedAccept = value['acepta_voluntarios'] as bool;
          _needs.text = _savedNeeds = value['necesidades_ayuda'] as String;
        });
      }
    } on Exception catch (e) {
      if (mounted) {
        setState(() {
          _error = messageFor(e, 'No pudimos guardar la convocatoria.');
          _denied = e is ApiException && (e.status == 401 || e.status == 403);
          _uncertain =
              e is! ApiException ||
              e.status == null ||
              e.status == 409 ||
              e.status! >= 500;
        });
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _cancel() async {
    if (_busy || _confirming) return;
    _confirming = true;
    final leave = !_dirty || _denied || await _confirmDiscard();
    _confirming = false;
    if (!leave || !mounted) return;
    setState(() => _allowLeave = true);
    await WidgetsBinding.instance.endOfFrame;
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) => PopScope(
    canPop: !_busy && (_allowLeave || !_dirty),
    onPopInvokedWithResult: (didPop, _) {
      if (!didPop) _cancel();
    },
    child: Scaffold(
      appBar: AppBar(
        title: const Text('Convocatoria'),
        actions: [
          IconButton(
            tooltip: 'Actualizar convocatoria',
            onPressed: _busy ? null : _reload,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      bottomNavigationBar: _loaded
          ? LpnKeyboardSafeArea(
              top: false,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Wrap(
                  alignment: WrapAlignment.end,
                  spacing: 12,
                  runSpacing: 8,
                  children: [
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
                          _busy
                              ? 'Guardando…'
                              : _dirty
                              ? 'Guardar convocatoria'
                              : 'Sin cambios pendientes',
                        ),
                      ),
                  ],
                ),
              ),
            )
          : null,
      body: _denied
          ? StatusPanel(
              message:
                  _error ?? 'Sin permiso para consultar esta organización.',
              action: _reload,
              actionLabel: 'Comprobar acceso',
            )
          : FutureBuilder<Map<String, dynamic>>(
              future: _data,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }
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
                final data = snapshot.data!;
                return ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    Text(
                      '${data['nombre']}',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'La convocatoria se muestra en la red pública cuando la organización está verificada y activa.',
                    ),
                    const SizedBox(height: 16),
                    FormCard(
                      title: 'Cómo pueden ayudar',
                      icon: Icons.volunteer_activism_outlined,
                      tone: 1,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          SwitchListTile(
                            contentPadding: EdgeInsets.zero,
                            title: const Text('Recibir voluntarios'),
                            value: _accept,
                            onChanged: _busy || _uncertain
                                ? null
                                : (value) => setState(() => _accept = value),
                          ),
                          const SizedBox(height: 16),
                          TextField(
                            controller: _needs,
                            enabled: !_busy && !_uncertain,
                            minLines: 3,
                            maxLines: 6,
                            maxLength: 1000,
                            buildCounter: (
                              _, {
                              required currentLength,
                              required isFocused,
                              maxLength,
                            }) => null,
                            onChanged: (_) => setState(() {}),
                            decoration: const InputDecoration(
                              labelText: 'Necesidades de ayuda en especie',
                            ),
                          ),
                        ],
                      ),
                    ),
                    if (_error != null)
                      Text(
                        _error!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                        ),
                      ),
                    const SizedBox(height: 24),
                    OutlinedButton.icon(
                      icon: const Icon(Icons.campaign_outlined),
                      label: const Text(
                        'Editar actividades y canales públicos',
                      ),
                      onPressed: _busy || _dirty
                          ? null
                          : () => Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => HelpProgramEditor(
                                  api: widget.api,
                                  session: widget.session,
                                  id: widget.id,
                                ),
                              ),
                            ),
                    ),
                    if (_dirty)
                      const Text(
                        'Guarda o descarta los cambios antes de editar su publicación.',
                      ),
                    const SizedBox(height: 24),
                    Text(
                      'Ofrecimientos recibidos',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 12),
                    if ((data['ofrecimientos'] as List).isEmpty)
                      const Text('Todavía no hay ofrecimientos registrados.'),
                    for (final row in data['ofrecimientos'] as List)
                      HelpOfferCard(
                        row: Map<String, dynamic>.from(row as Map),
                        received: true,
                      ),
                  ],
                );
              },
            ),
    ),
  );
}
