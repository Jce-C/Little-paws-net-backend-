import '../design/form_surfaces.dart';

import 'package:flutter/material.dart';

import '../adoption/adoption_screens.dart' show StatusPanel, messageFor;
import '../auth/account_screen.dart';
import '../auth/session.dart';
import '../core/api_client.dart';
import '../design/lpn_app_bar.dart';
import '../design/community_surface.dart';
import '../auth/public_avatar.dart';
import 'message_composer.dart';

class CommunityScreen extends StatelessWidget {
  const CommunityScreen({super.key, required this.api, required this.session});
  final ApiClient api;
  final Session session;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Comunidad'),
    body: ListenableBuilder(
      listenable: session,
      builder: (context, _) => _Conversation(
        key: ValueKey((session.identityRevision, session.account?.email)),
        api: api,
        session: session,
      ),
    ),
  );
}

class _Conversation extends StatefulWidget {
  const _Conversation({
    super.key,
    required this.api,
    required this.session,
    this.post,
  });
  final ApiClient api;
  final Session session;
  final Map<String, dynamic>? post;
  @override
  State<_Conversation> createState() => _ConversationState();
}

class _ConversationState extends State<_Conversation> {
  final _rows = <Map<String, dynamic>>[];
  final _busyRows = <int>{};
  final _expanded = <int>{};
  bool _loading = true,
      _more = false,
      _canWrite = false,
      _canModerate = false,
      _inFlight = false;
  int? _cursor;
  Object? _error;
  bool get _thread => widget.post != null;
  String get _path => _thread
      ? '/api/comunidad/publicaciones/${widget.post!['id']}/comentarios/'
      : '/api/comunidad/publicaciones/';
  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load({bool more = false}) async {
    if (_inFlight || (more && (_loading || _cursor == null))) return;
    _inFlight = true;
    setState(() {
      if (more) {
        _more = true;
      } else {
        _loading = true;
      }
      _error = null;
    });
    try {
      final path = more
          ? '$_path?${_thread ? 'despues' : 'antes'}=$_cursor'
          : _path;
      final value = widget.session.signedIn
          ? await widget.session.authorized(
              (token) => widget.api.get(path, token: token),
            )
          : await widget.api.get(path);
      if (value is! Map ||
          value['results'] is! List ||
          (value['results'] as List).length > 20) {
        throw const ApiException('No pudimos interpretar la conversación.');
      }
      final next = value[_thread ? 'despues' : 'antes'];
      if (next != null &&
          (next is! int || next <= 0 || (more && next == _cursor))) {
        throw const ApiException('No pudimos continuar la conversación.');
      }
      final rows = (value['results'] as List)
          .map((row) => Map<String, dynamic>.from(row as Map))
          .toList();
      if (rows.any((row) => row['id'] is! int || row['contenido'] is! String)) {
        throw const ApiException('No pudimos interpretar los mensajes.');
      }
      if (mounted) {
        setState(() {
          if (!more) _rows.clear();
          final ids = _rows.map((row) => row['id']).toSet();
          _rows.addAll(rows.where((row) => ids.add(row['id'])));
          _cursor = next as int?;
          _canWrite = value['puede_publicar'] == true;
          _canModerate = value['puede_moderar'] == true;
        });
      }
    } on Exception catch (e) {
      if (mounted) setState(() => _error = e);
    } finally {
      _inFlight = false;
      if (mounted) {
        setState(() {
          _loading = false;
          _more = false;
        });
      }
    }
  }

  Future<void> _write({int? reply}) async {
    if (!widget.session.signedIn && !await openLogin(context, widget.session)) {
      return;
    }
    if (!mounted) return;
    await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => PublicMessageScreen(
          api: widget.api,
          session: widget.session,
          path: _path,
          title: _thread ? 'Escribir comentario' : 'Crear publicación',
          extra: reply == null ? const {} : {'respuesta_a': reply},
        ),
      ),
    );
    if (mounted) _load();
  }

  Future<void> _react(Map<String, dynamic> row) async {
    final id = row['id'] as int;
    if (_busyRows.contains(id)) return;
    if (!widget.session.signedIn && !await openLogin(context, widget.session)) {
      return;
    }
    if (!mounted) return;
    setState(() => _busyRows.add(id));
    try {
      final active = row['reaccion_propia'] == true;
      final path = '/api/comunidad/publicaciones/$id/reaccion/';
      final result = await widget.session.authorized(
        (token) => active
            ? widget.api.delete(path, token: token)
            : widget.api.post(path, {}, token: token),
      );
      if (result is! Map ||
          result['total'] is! int ||
          result['activa'] is! bool) {
        throw const ApiException('No pudimos confirmar la reacción.');
      }
      if (mounted) {
        setState(() {
          row['reacciones'] = result['total'];
          row['reaccion_propia'] = result['activa'];
        });
      }
    } on Exception catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(messageFor(e, 'No pudimos actualizar la reacción.')),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _busyRows.remove(id));
    }
  }

  Future<void> _withdraw(Map<String, dynamic> row) async {
    final own = row['propia'] == true && _canWrite;
    var explanation = '';
    final form = GlobalKey<FormState>();
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        scrollable: true,
        backgroundColor: LpnFormPalette.tones[3],
        title: Text(own ? '¿Retirar publicación?' : 'Moderar publicación'),
        content: Form(
          key: form,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Dejará de aparecer en la comunidad. El registro se conserva para trazabilidad.',
              ),
              if (!own) ...[
                const SizedBox(height: 16),
                TextFormField(
                  onChanged: (value) => explanation = value.trim(),
                  maxLength: 500,
                  decoration: const InputDecoration(
                    labelText: 'Motivo de moderación',
                  ),
                  validator: (value) => (value ?? '').trim().length < 5
                      ? 'Explica el motivo con al menos cinco caracteres.'
                      : null,
                ),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () {
              if (own || validateLpnForm(form)) {
                Navigator.pop(context, true);
              }
            },
            child: const Text('Retirar'),
          ),
        ],
      ),
    );
    if (confirm != true || !mounted) return;
    try {
      await widget.session.authorized(
        (token) => widget.api.post(
          '/api/comunidad/publicaciones/${row['id']}/retirar/',
          own ? {} : {'motivo': explanation},
          token: token,
        ),
      );
      if (mounted) _load();
    } on Exception catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(messageFor(e, 'No pudimos retirar la publicación.')),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null && _rows.isEmpty) {
      return SingleChildScrollView(
        child: StatusPanel(
          message: messageFor(_error, 'No pudimos consultar la comunidad.'),
          action: _load,
          actionLabel: 'Reintentar',
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(20),
        children: [
          if (!_thread)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Historias que nos conectan',
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        const SizedBox(height: 8),
                        const Text('Experiencias de una comunidad que cuida.'),
                      ],
                    ),
                  ),
                  if (widget.session.signedIn)
                    IconButton.filledTonal(
                      tooltip: 'Cambiar foto de perfil',
                      icon: const Icon(Icons.add_a_photo_outlined),
                      onPressed: () async {
                        await Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) =>
                                AvatarScreen(session: widget.session),
                          ),
                        );
                        if (mounted) await _load();
                      },
                    ),
                ],
              ),
            )
          else
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Text('${widget.post!['contenido']}'),
              ),
            ),
          const SizedBox(height: 16),
          if (_canWrite || !widget.session.signedIn)
            FilledButton.icon(
              onPressed: _write,
              icon: const Icon(Icons.edit_outlined),
              label: Text(
                _thread ? 'Escribir comentario' : 'Crear publicación',
              ),
            )
          else
            Text(
              _canModerate
                  ? 'Puedes moderar las conversaciones de la comunidad.'
                  : 'Tu cuenta tiene acceso de lectura a la comunidad.',
            ),
          const SizedBox(height: 16),
          if (_rows.isEmpty)
            const StatusPanel(
              message:
                  'Todavía no hay mensajes. Puedes iniciar la conversación.',
            ),
          for (final row in _rows)
            Container(
              key: ValueKey('community-post-${row['id']}'),
              margin: const EdgeInsets.only(bottom: 12),
              decoration: CommunitySurface.decoration(
                context,
                row['id'] as int,
              ),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        PublicAvatar(
                          value: row['foto_autor'],
                          name: '${row['autor'] ?? ''}',
                          origin: widget.api.base,
                          radius: 20,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                '${row['autor']}',
                                style: Theme.of(context).textTheme.titleMedium,
                              ),
                              Text(
                                _date(row['fecha']),
                                style: Theme.of(context).textTheme.bodySmall,
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    if (row['respuesta_a'] != null)
                      const Text(
                        'Respuesta a un comentario',
                        style: TextStyle(fontSize: 14),
                      ),
                    Text(
                      '${row['contenido']}',
                      maxLines:
                          _thread ||
                              '${row['contenido']}'.length <= 160 ||
                              _expanded.contains(row['id'])
                          ? null
                          : 4,
                      overflow:
                          _thread ||
                              '${row['contenido']}'.length <= 160 ||
                              _expanded.contains(row['id'])
                          ? TextOverflow.visible
                          : TextOverflow.ellipsis,
                      style: const TextStyle(height: 1.5),
                    ),
                    if (!_thread && '${row['contenido']}'.length > 160)
                      Align(
                        alignment: AlignmentDirectional.centerStart,
                        child: TextButton(
                          onPressed: () => setState(() {
                            if (!_expanded.add(row['id'] as int)) {
                              _expanded.remove(row['id']);
                            }
                          }),
                          child: Text(
                            _expanded.contains(row['id'])
                                ? 'Ver menos'
                                : 'Leer más',
                          ),
                        ),
                      ),
                    const SizedBox(height: 12),
                    if (!_thread)
                      Wrap(
                        spacing: 8,
                        children: [
                          TextButton.icon(
                            onPressed:
                                (_canWrite || !widget.session.signedIn) &&
                                    !_busyRows.contains(row['id'])
                                ? () => _react(row)
                                : null,
                            icon: Icon(
                              row['reaccion_propia'] == true
                                  ? Icons.favorite
                                  : Icons.favorite_border,
                            ),
                            label: Text('${row['reacciones']} Me gusta'),
                          ),
                          TextButton.icon(
                            onPressed: () => Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => Scaffold(
                                  appBar: lpnAppBar(context, 'Conversación'),
                                  body: _Conversation(
                                    api: widget.api,
                                    session: widget.session,
                                    post: row,
                                  ),
                                ),
                              ),
                            ),
                            icon: const Icon(
                              Icons.chat_bubble_outline,
                              size: 18,
                            ),
                            label: Text('${row['comentarios']} comentarios'),
                          ),
                          if ((row['propia'] == true && _canWrite) ||
                              _canModerate)
                            TextButton(
                              onPressed: () => _withdraw(row),
                              child: Text(
                                row['propia'] == true && _canWrite
                                    ? 'Retirar publicación'
                                    : 'Moderar publicación',
                              ),
                            ),
                        ],
                      )
                    else if (_canWrite && row['respuesta_a'] == null)
                      TextButton(
                        onPressed: () => _write(reply: row['id'] as int),
                        child: const Text('Responder'),
                      ),
                  ],
                ),
              ),
            ),
          if (_error != null)
            StatusPanel(
              message: messageFor(_error, 'No pudimos continuar.'),
              action: () => _load(more: true),
              actionLabel: 'Reintentar',
            ),
          if (_more)
            const Center(child: CircularProgressIndicator())
          else if (_cursor != null)
            OutlinedButton(
              onPressed: () => _load(more: true),
              child: const Text('Cargar más'),
            ),
        ],
      ),
    );
  }

  String _date(Object? value) {
    final date = DateTime.tryParse('$value')?.toLocal();
    return date == null
        ? 'Fecha no disponible'
        : MaterialLocalizations.of(context).formatMediumDate(date);
  }
}
