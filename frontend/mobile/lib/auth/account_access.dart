import '../core/api_client.dart';
import 'session.dart';

class AssignedRole {
  const AssignedRole(this.code, this.context, this.contextId);
  final String code;
  final String context;
  final int? contextId;
}

/// Read-only projection of the existing authenticated access endpoint.
class AccountAccess {
  const AccountAccess(this.session);
  final Session session;

  Future<List<AssignedRole>> load() async {
    final result = await session.authorized(
      (token) => session.api.get('/api/seguridad/mis-accesos/', token: token),
    );
    if (result is! Map<String, dynamic>) throw _invalid;
    final globals = _codes(result['roles_globales']);
    final organizations = result['entidades'];
    if (organizations is! List) throw _invalid;
    final roles = <AssignedRole>[
      for (final code in globals) AssignedRole(code, 'Plataforma', null),
    ];
    for (final item in organizations) {
      if (item is! Map<String, dynamic> ||
          item['id'] is! int ||
          item['id'] <= 0 ||
          item['nombre'] is! String ||
          (item['nombre'] as String).trim().isEmpty) {
        throw _invalid;
      }
      for (final code in _codes(item['roles'])) {
        roles.add(
          AssignedRole(code, item['nombre'] as String, item['id'] as int),
        );
      }
    }
    final seen = <(String, int?)>{};
    return List.unmodifiable(
      roles.where((r) => seen.add((r.code, r.contextId))),
    );
  }

  static List<String> _codes(Object? value) {
    if (value is! List || value.any((x) => x is! String || x.trim().isEmpty)) {
      throw _invalid;
    }
    return value.cast<String>();
  }

  static const _invalid = ApiException(
    'No pudimos verificar los roles de tu cuenta.',
  );
}
