import '../design/lpn_theme.dart';
import '../design/form_surfaces.dart';
import '../adoption/request_detail_screen.dart';
import '../design/lpn_app_bar.dart';

import 'package:flutter/material.dart';

import '../adoption/adoption_screens.dart' show StatusPanel, messageFor;
import '../auth/account_screen.dart';
import 'notifications_api.dart';

class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key, required this.api});
  final NotificationsApi api;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Notificaciones'),
    body: ListenableBuilder(
      listenable: api.session,
      builder: (context, _) {
        if (api.session.restoring) {
          return const Center(child: CircularProgressIndicator());
        }
        if (!api.session.signedIn) {
          return SingleChildScrollView(
            child: StatusPanel(
              message: 'Inicia sesión para consultar tus notificaciones.',
              action: () => openLogin(context, api.session),
              actionLabel: 'Iniciar sesión',
            ),
          );
        }
        return _NotificationList(
          key: ValueKey((
            api.session.identityRevision,
            api.session.account!.email,
          )),
          api: api,
        );
      },
    ),
  );
}

class _NotificationList extends StatefulWidget {
  const _NotificationList({super.key, required this.api});
  final NotificationsApi api;
  @override
  State<_NotificationList> createState() => _NotificationListState();
}

class _NotificationListState extends State<_NotificationList> {
  List<AccountNotification>? _items;
  String? _error;
  bool _loading = false;
  bool _loadingMore = false;
  bool _opening = false;
  String? _next;
  bool _onlyUnread = false;
  final _reading = <int>{};

  @override
  void initState() {
    super.initState();
    _reload();
  }

  Future<void> _reload() async {
    if (_loading || _loadingMore || _reading.isNotEmpty) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final result = await widget.api.page();
      if (mounted) {
        setState(() {
          _items = result.items;
          _next = result.next;
        });
      }
    } on Exception catch (error) {
      if (mounted) {
        setState(
          () => _error = messageFor(
            error,
            'No pudimos consultar las notificaciones.',
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _markRead(AccountNotification item) async {
    if (_loading || _loadingMore || _reading.contains(item.id)) return;
    setState(() => _reading.add(item.id));
    try {
      final readAt = await widget.api.markRead(item.id);
      if (mounted) {
        setState(
          () => _items = _items!
              .map(
                (current) =>
                    current.id == item.id ? current.read(readAt) : current,
              )
              .toList(),
        );
      }
    } on Exception catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              messageFor(
                error,
                'No pudimos marcar la notificación. Intenta de nuevo.',
              ),
            ),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _reading.remove(item.id));
    }
  }

  Future<void> _more() async {
    if (_loading || _loadingMore || _next == null || _reading.isNotEmpty) {
      return;
    }
    setState(() => _loadingMore = true);
    try {
      final page = await widget.api.page(before: _next);
      if (mounted) {
        setState(() {
          final ids = (_items ?? []).map((n) => n.id).toSet();
          _items = [
            ...?_items,
            ...page.items.where((n) => !ids.contains(n.id)),
          ];
          _next = page.next;
        });
      }
    } on Exception catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(messageFor(error, 'No pudimos cargar más avisos.')),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _loadingMore = false);
    }
  }

  IconData _icon(AccountNotification item) {
    final kind = item.kind.toLowerCase();
    return kind.contains('adopci')
        ? Icons.pets_outlined
        : kind.contains('ayuda')
        ? Icons.volunteer_activism_outlined
        : kind.contains('publicidad')
        ? Icons.campaign_outlined
        : Icons.notifications_none;
  }

  Future<void> _open(AccountNotification item) async {
    if (item.requestId == null || _loading || _loadingMore || _opening) return;
    setState(() => _opening = true);
    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => RequestDetailScreen(
          session: widget.api.session,
          id: item.requestId!,
        ),
      ),
    );
    if (mounted) {
      setState(() => _opening = false);
      await _reload();
    }
  }

  @override
  Widget build(BuildContext context) {
    final unread = (_items ?? const <AccountNotification>[])
        .where((item) => item.unread)
        .length;
    final items = (_items ?? const <AccountNotification>[]).where(
      (item) => !_onlyUnread || item.unread,
    );
    return RefreshIndicator(
      onRefresh: _reload,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: EdgeInsets.symmetric(
          vertical: 16,
          horizontal: ((MediaQuery.sizeOf(context).width - 640) / 2).clamp(
            16.0,
            double.infinity,
          ),
        ),
        children: [
          const Text(
            'Novedades de tus procesos. Abre el detalle o marca cada aviso como leído.',
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Semantics(
                  liveRegion: true,
                  child: Text('$unread sin leer en esta lista'),
                ),
              ),
              IconButton(
                tooltip: 'Actualizar notificaciones',
                onPressed: _loading || _loadingMore || _reading.isNotEmpty
                    ? null
                    : _reload,
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
          Align(
            alignment: Alignment.centerLeft,
            child: FilterChip(
              label: const Text('Solo sin leer'),
              selected: _onlyUnread,
              onSelected: (selected) => setState(() => _onlyUnread = selected),
            ),
          ),
          const SizedBox(height: 12),
          if (_loading)
            const LinearProgressIndicator(
              semanticsLabel: 'Cargando notificaciones',
            ),
          if (_error != null)
            StatusPanel(
              message: _error!,
              action: _reload,
              actionLabel: 'Reintentar',
            )
          else if (!_loading && items.isEmpty)
            StatusPanel(
              message: _onlyUnread
                  ? 'No hay avisos sin leer en esta lista.'
                  : 'Todavía no tienes notificaciones.',
            )
          else
            for (final item in items)
              Card(
                color: item.unread ? LpnFormPalette.tones[0] : LpnColors.paper,
                elevation: 0,
                margin: const EdgeInsets.only(bottom: 12),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          Icon(
                            _icon(item),
                            color: Theme.of(context).colorScheme.primary,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              item.unread ? 'Sin leer' : 'Leída',
                              style: const TextStyle(
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        item.kind,
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                      const SizedBox(height: 8),
                      Text(item.content),
                      const SizedBox(height: 8),
                      Text(
                        '${MaterialLocalizations.of(context).formatMediumDate(item.createdAt.toLocal())}, ${TimeOfDay.fromDateTime(item.createdAt.toLocal()).format(context)}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      if (item.requestId != null)
                        Align(
                          alignment: AlignmentDirectional.centerEnd,
                          child: OutlinedButton.icon(
                            key: Key('notification-open-${item.id}'),
                            onPressed: _loading || _loadingMore
                                ? null
                                : () => _open(item),
                            icon: const Icon(Icons.arrow_forward, size: 16),
                            label: const Text('Ver solicitud'),
                          ),
                        ),
                      if (item.unread)
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton.icon(
                            key: Key('notification-read-${item.id}'),
                            onPressed:
                                _loading ||
                                    _loadingMore ||
                                    _reading.contains(item.id)
                                ? null
                                : () => _markRead(item),
                            icon: const Icon(Icons.done),
                            label: Text(
                              _reading.contains(item.id)
                                  ? 'Guardando…'
                                  : 'Marcar como leída',
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
          if (_next != null)
            Align(
              alignment: AlignmentDirectional.center,
              child: TextButton(
                onPressed: _loading || _loadingMore ? null : _more,
                child: Text(_loadingMore ? 'Cargando…' : 'Ver más avisos'),
              ),
            ),
        ],
      ),
    );
  }
}
