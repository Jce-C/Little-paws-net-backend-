import 'dart:typed_data';

import '../auth/session.dart';
import '../core/api_client.dart';

class ReportChoice {
  const ReportChoice(this.id, this.name);
  final int id;
  final String name;
}

class ReportCity extends ReportChoice {
  const ReportCity(super.id, super.name, this.department);
  final String department;
  String get label => '$name, $department';
}

class ReportOptions {
  const ReportOptions(this.types, this.cities);
  final List<ReportChoice> types;
  final List<ReportCity> cities;
}

class RescueCase {
  const RescueCase(this.id, this.status, this.organization);
  final int id;
  final String status;
  final String organization;
}

class AnimalReport {
  const AnimalReport({
    required this.id,
    required this.type,
    required this.status,
    required this.description,
    this.photo,
    this.city = '',
    this.rescueCase,
  });
  final int id;
  final String type;
  final String status;
  final String description;
  final String city;
  final Object? photo;
  final RescueCase? rescueCase;
}

class ReportReceipt {
  const ReportReceipt(this.id, this.status, this.privateCode);
  final int id;
  final String status;
  final String? privateCode;
}

class PublicReportPage {
  const PublicReportPage(this.reports, this.nextCursor);
  final List<AnimalReport> reports;
  final String? nextCursor;
}

class RescueApi {
  const RescueApi(this.api, this.session);
  final ApiClient api;
  final Session session;

  Future<ReportReceipt> manageAnonymous({
    required int reportId,
    required String code,
    String description = '',
    String contact = '',
    bool clearContact = false,
    bool close = false,
  }) async {
    final body = <String, Object?>{
      'codigo_gestion': code.trim(),
      'cerrar': close,
    };
    if (!close && description.trim().isNotEmpty) {
      body['descripcion'] = description.trim();
    }
    if (!close && (clearContact || contact.trim().isNotEmpty)) {
      body['contacto_reportante'] = clearContact ? '' : contact.trim();
    }
    final Map<String, dynamic> row;
    try {
      row = _map(
        await api.post('/api/reportes/$reportId/gestion-anonima/', body),
      );
    } on ApiException catch (error) {
      if (error.status == 403 || error.status == 404) {
        throw ApiException(
          'Revisa el número de reporte y la clave privada.',
          status: error.status,
        );
      }
      if (error.status == 409) {
        throw const ApiException(
          'El reporte ya fue aceptado o cerrado y no admite estos cambios.',
          status: 409,
        );
      }
      rethrow;
    }
    return ReportReceipt(_id(row['id_reporte']), _text(row['estado']), null);
  }

  Future<ReportOptions> options([String cityQuery = '']) async {
    final query = Uri(queryParameters: {'ciudad': cityQuery.trim()}).query;
    final data = _map(await api.get('/api/reportes/opciones/?$query'));
    return ReportOptions(
      _list(data['tipos']).map((value) {
        final row = _map(value);
        return ReportChoice(_id(row['id_valor_maestro']), _text(row['nombre']));
      }).toList(),
      _list(data['ciudades']).map((value) {
        final row = _map(value);
        return ReportCity(
          _id(row['id_ciudad']),
          _text(row['nombre']),
          _text(row['departamento']),
        );
      }).toList(),
    );
  }

  Future<PublicReportPage> publicReportPage({
    String query = '',
    String? cursor,
  }) async {
    if (cursor != null &&
        (!RegExp(r'^[1-9][0-9]{0,18}$').hasMatch(cursor) ||
            int.tryParse(cursor) == null)) {
      throw _invalid;
    }
    if (query.length > 100) {
      throw const ApiException('Usa como máximo 100 caracteres.');
    }
    final params = Uri(
      queryParameters: {
        if (query.trim().isNotEmpty) 'buscar': query.trim(),
        'antes': ?cursor,
      },
    ).query;
    final data = _map(
      await api.get(
        '/api/reportes/publicos/${params.isEmpty ? '' : '?$params'}',
      ),
    );
    final rows = _list(data['results']);
    final next = data['next_cursor'];
    if (rows.length > 20 ||
        !data.containsKey('next_cursor') ||
        (next != null &&
            (next is! String ||
                !RegExp(r'^[1-9][0-9]{0,18}$').hasMatch(next) ||
                int.tryParse(next) == null))) {
      throw _invalid;
    }
    final reports = rows.map((value) {
      final row = _map(value);
      return AnimalReport(
        id: _id(row['id_reporte']),
        type: _text(row['tipo_reporte__nombre']),
        status: _text(row['estado_reporte__nombre']),
        description: _text(row['descripcion']),
        photo: row['foto'],
        city: row['ciudad'] is String ? row['ciudad'] as String : '',
        rescueCase: row['caso'] is Map
            ? RescueCase(
                _id((row['caso'] as Map)['id_caso']),
                _text((row['caso'] as Map)['estado']),
                _text((row['caso'] as Map)['fundacion']),
              )
            : null,
      );
    }).toList();
    if (next != null &&
        (reports.isEmpty ||
            next != reports.last.id.toString() ||
            (cursor != null &&
                int.parse(next as String) >= int.parse(cursor)))) {
      throw _invalid;
    }
    return PublicReportPage(reports, next as String?);
  }

  Future<List<AnimalReport>> mine() async {
    final rows = _list(
      await session.authorized(
        (token) => api.get('/api/reportes/mios/', token: token),
      ),
    );
    return rows.map((value) {
      final row = _map(value);
      final rawCase = row['caso'];
      final caseData = rawCase == null ? null : _map(rawCase);
      return AnimalReport(
        id: _id(row['id_reporte']),
        type: _text(row['tipo']),
        status: _text(row['estado']),
        description: _text(row['descripcion']),
        photo: row['foto'],
        city: row['ciudad'] is String ? row['ciudad'] as String : '',
        rescueCase: caseData == null
            ? null
            : RescueCase(
                _id(caseData['id_caso']),
                _text(caseData['estado']),
                _text(caseData['fundacion']),
              ),
      );
    }).toList();
  }

  Future<ReportReceipt> create({
    required int type,
    required int city,
    required String neighborhood,
    required String address,
    required String description,
    Uint8List? photo,
    bool photoPublic = false,
    String contact = '',
    String directions = '',
  }) async {
    if (photo != null && !photoPublic) {
      throw const ApiException(
        'Confirma que deseas publicar la foto con el reporte.',
      );
    }
    final body = <String, Object?>{
      'tipo_reporte': type,
      'ciudad_id': city,
      'barrio': neighborhood.trim(),
      'direccion': address.trim(),
      'descripcion': description.trim(),
      'contacto_reportante': contact.trim(),
      'indicaciones': directions.trim(),
    };
    final anonymous = !session.signedIn;
    Future<Object?> send(String? token) => photo == null
        ? api.post('/api/reportes/', body, token: token)
        : api.uploadImage(
            '/api/reportes/',
            {...body, 'confirmar_foto_publica': 'true'},
            photo,
            token: token,
          );
    final result = anonymous
        ? await send(null)
        : await session.authorized((token) => send(token));
    final row = _map(result);
    if (anonymous &&
        (row['codigo_gestion'] is! String ||
            (row['codigo_gestion'] as String).isEmpty)) {
      throw const ApiException(
        'No pudimos confirmar tu clave privada. Evita repetir el reporte y contacta al equipo de la plataforma.',
      );
    }
    return ReportReceipt(
      _id(row['id_reporte']),
      _text(row['estado']),
      anonymous ? row['codigo_gestion'] as String : null,
    );
  }
}

const _invalid = ApiException(
  'El servidor devolvió datos inesperados. Intenta actualizar de nuevo.',
);
Map<String, dynamic> _map(Object? value) {
  if (value is Map<String, dynamic>) return value;
  throw _invalid;
}

List<dynamic> _list(Object? value) {
  if (value is List<dynamic>) return value;
  throw _invalid;
}

int _id(Object? value) {
  if (value is int && value > 0) return value;
  throw _invalid;
}

String _text(Object? value) {
  if (value is String && value.trim().isNotEmpty) return value;
  throw _invalid;
}
