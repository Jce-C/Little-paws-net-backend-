import '../auth/session.dart';
import '../core/api_client.dart';

class AccountNotification {
  const AccountNotification({
    required this.id,
    required this.content,
    required this.createdAt,
    this.readAt,
    this.kind = 'Aviso',
    this.requestId,
    this.readAcknowledged = false,
  });
  final int id;
  final String content;
  final DateTime createdAt;
  final DateTime? readAt;
  final String kind;
  final int? requestId;
  final bool readAcknowledged;
  bool get unread => readAt == null && !readAcknowledged;

  factory AccountNotification.fromJson(Object? value) {
    if (value is! Map<String, dynamic>) throw _invalid;
    final id = value['id_notificacion'];
    final content = value['contenido'];
    final created = value['fecha_creacion'];
    final read = value['fecha_lectura'];
    if (id is! int ||
        id <= 0 ||
        content is! String ||
        content.trim().isEmpty ||
        created is! String ||
        (read != null && read is! String)) {
      throw _invalid;
    }
    final createdAt = DateTime.tryParse(created);
    final readAt = read == null ? null : DateTime.tryParse(read as String);
    if (createdAt == null || (read != null && readAt == null)) throw _invalid;
    return AccountNotification(
      id: id,
      content: content,
      createdAt: createdAt,
      readAt: readAt,
      kind: value['tipo'] is String ? value['tipo'] as String : 'Aviso',
      requestId: _destination(value['destino']),
    );
  }

  AccountNotification read(DateTime? at) => AccountNotification(
    id: id,
    content: content,
    createdAt: createdAt,
    readAt: at,
    kind: kind,
    requestId: requestId,
    readAcknowledged: true,
  );
}

class NotificationsApi {
  const NotificationsApi(this.api, this.session);
  final ApiClient api;
  final Session session;

  Future<List<AccountNotification>> list() async => (await page()).items;

  Future<NotificationPage> page({String? before}) async {
    if (before != null && !RegExp(r'^[1-9][0-9]{0,9}$').hasMatch(before)) {
      throw _invalid;
    }
    final result = await session.authorized(
      (token) => api.get(
        '/api/notificaciones/?paginado=1${before == null ? '' : '&antes=$before'}',
        token: token,
      ),
    );
    if (result is List) {
      if (result.length > 100) throw _invalid;
      return NotificationPage(
        result.map(AccountNotification.fromJson).toList(),
        null,
      );
    }
    if (result is! Map || result['results'] is! List) throw _invalid;
    final rows = result['results'] as List;
    final next = result['next_cursor'];
    if (rows.length > 20 ||
        (next != null &&
            (next is! String || !RegExp(r'^[1-9][0-9]{0,9}$').hasMatch(next)))) {
      throw _invalid;
    }
    return NotificationPage(
      rows.map(AccountNotification.fromJson).toList(),
      next as String?,
    );
  }

  Future<DateTime?> markRead(int id) async {
    final result = await session.authorized(
      (token) => api.post('/api/notificaciones/$id/leer/', {}, token: token),
    );
    if (result is! Map<String, dynamic> || result['leida'] != true) {
      throw _invalid;
    }
    final value = result['fecha_lectura'];
    if (value == null) {
      return null; // Older servers confirm the state but not its date.
    }
    if (value is! String || DateTime.tryParse(value) == null) throw _invalid;
    return DateTime.parse(value);
  }
}

const _invalid = ApiException(
  'No pudimos interpretar las notificaciones. Intenta actualizar de nuevo.',
);

int? _destination(Object? value) {
  if (value == null) return null;
  if (value is! Map ||
      value['tipo'] != 'solicitud_adopcion' ||
      value['id'] is! int ||
      (value['id'] as int) <= 0) {
    return null;
  }
  return value['id'] as int;
}

class NotificationPage {
  const NotificationPage(this.items, this.next);
  final List<AccountNotification> items;
  final String? next;
}
