import 'dart:typed_data';

import '../core/inline_webp.dart';
import '../auth/session.dart';
import '../core/api_client.dart';

class Pet {
  const Pet({
    required this.id,
    required this.name,
    required this.species,
    this.breed,
    this.photo,
    this.sex,
    this.size,
    this.ageMonths,
    this.presentation,
  });

  final int id;
  final String name;
  final String species;
  final String? breed;
  final PublicPetPhoto? photo;
  final String? sex, size;
  final int? ageMonths;
  final PetPresentation? presentation;
  String get description => presentation?.description ?? '';

  factory Pet.fromJson(Map<String, dynamic> json) {
    final id = _id(json['id_mascota']);
    return Pet(
      id: id,
      name: _petName(json['nombre']),
      species: _optionalText(json['especie']) ?? '',
      breed: _optionalText(json['raza']),
      photo: PublicPetPhoto.fromJson(json['foto'], id),
      presentation: PetPresentation.fromJson(json['presentacion']),
      sex: _optionalText(json['sexo']),
      size: _optionalText(json['tamano']),
      ageMonths: json['edad_meses'] is int && (json['edad_meses'] as int) >= 0
          ? json['edad_meses'] as int
          : null,
    );
  }

  String get summary => [
    if (species.trim().isNotEmpty) species,
    if (breed != null && breed!.trim().isNotEmpty && breed != species) breed!,
  ].join(', ');
  String get attributes => [
    if (ageMonths != null)
      ageMonths! < 12
          ? '$ageMonths ${ageMonths == 1 ? 'mes' : 'meses'}'
          : '${ageMonths! ~/ 12} ${ageMonths! ~/ 12 == 1 ? 'año' : 'años'}',
    ?sex,
    ?size,
  ].join(', ');
}

class PetPresentation {
  const PetPresentation({
    required this.description,
    this.care = '',
    this.space = '',
  });
  final String description, care, space;
  static PetPresentation? fromJson(Object? value) {
    if (value == null) return null;
    final row = _object(value);
    String field(String key, int limit) {
      final text = row[key];
      if (text is! String || text.runes.length > limit) throw _invalidResponse;
      return text.trim();
    }

    final description = field('descripcion', 1000);
    if (description.isEmpty) throw _invalidResponse;
    return PetPresentation(
      description: description,
      care: field('cuidados', 2000),
      space: field('espacio', 600),
    );
  }
}

class PublicPetPhoto {
  const PublicPetPhoto._(this.path, this.width, this.height, this.bytes);
  final Uri path;
  final int width;
  final int height;
  final int bytes;

  static PublicPetPhoto? fromJson(Object? value, int petId) {
    if (value == null) return null;
    final data = _object(value);
    final url = data['url'];
    final width = data['ancho'];
    final height = data['alto'];
    final bytes = data['bytes'];
    if (url is! String ||
        width is! int ||
        height is! int ||
        bytes is! int ||
        width <= 0 ||
        height <= 0 ||
        width > 1280 ||
        height > 1280 ||
        bytes <= 0 ||
        bytes > 512 * 1024) {
      throw _invalidResponse;
    }
    final uri = Uri.tryParse(url);
    if (uri == null ||
        uri.hasScheme ||
        uri.hasAuthority ||
        uri.hasFragment ||
        (uri.path != '/api/adopcion/mascotas/$petId/foto/' &&
            !RegExp('^/api/adopcion/mascotas/$petId/fotos/[1-9][0-9]*/\$')
                .hasMatch(uri.path)) ||
        uri.queryParametersAll.length != 1 ||
        uri.queryParametersAll['v']?.length != 1 ||
        !RegExp(r'^\d{1,20}$').hasMatch(uri.queryParameters['v'] ?? '')) {
      throw _invalidResponse;
    }
    return PublicPetPhoto._(uri, width, height, bytes);
  }
}

class AdoptionRequest {
  const AdoptionRequest(
    this.id,
    this.status, {
    this.petId,
    this.petName,
    this.createdAt,
    this.photo,
  });

  final int id;
  final String status;
  final int? petId;
  final String? petName;
  final DateTime? createdAt;
  final Uint8List? photo;

  factory AdoptionRequest.fromJson(Map<String, dynamic> json) =>
      AdoptionRequest(
        _id(json['id_solicitud_adopcion']),
        _text(json['estado_adopcion__nombre']),
        petId: json['mascota_id'] == null ? null : _id(json['mascota_id']),
        petName: _optionalText(json['mascota__nombre']),
        createdAt: json['fecha_solicitud'] is String
            ? DateTime.tryParse(json['fecha_solicitud'] as String)
            : null,
        photo: inlineWebp(json['foto_miniatura']),
      );
}

class PetDetail {
  const PetDetail({
    required this.pet,
    required this.organization,
    required this.city,
    required this.custodySince,
    required this.estimated,
    this.ageMonths,
    this.size,
    this.sex,
    this.photos = const [],
  });
  final Pet pet;
  final String organization;
  final String city;
  final DateTime custodySince;
  final int? ageMonths;
  final bool estimated;
  final String? size;
  final String? sex;
  final List<PublicPetPhoto> photos;

  factory PetDetail.fromJson(Object? value) {
    final row = _object(value);
    final months = row['edad_meses'];
    final approximate = row['edad_estimada'];
    final since = row['custodia_desde'];
    if ((months != null && (months is! int || months < 0)) ||
        approximate is! bool ||
        since is! String) {
      throw _invalidResponse;
    }
    final parsed = DateTime.tryParse(since);
    if (parsed == null) throw _invalidResponse;
    final pet = Pet.fromJson(row);
    final rawPhotos = row['fotos'];
    if (rawPhotos != null && (rawPhotos is! List || rawPhotos.length > 6)) {
      throw _invalidResponse;
    }
    final photos = rawPhotos is List
        ? rawPhotos
              .map(
                (value) =>
                    PublicPetPhoto.fromJson(value, pet.id) ??
                    (throw _invalidResponse),
              )
              .toList()
        : [if (pet.photo != null) pet.photo!];
    return PetDetail(
      pet: pet,
      photos: photos,
      organization: _text(row['organizacion']),
      city: _text(row['ciudad']),
      custodySince: parsed,
      estimated: approximate,
      ageMonths: months as int?,
      size: _optionalText(row['tamano']),
      sex: _optionalText(row['sexo']),
    );
  }

  String get ageLabel {
    final months = ageMonths;
    if (months == null) return 'Sin registrar';
    final String age;
    if (months < 1) {
      age = 'Menos de 1 mes';
    } else if (months < 12) {
      age = '$months ${months == 1 ? 'mes' : 'meses'}';
    } else {
      final years = months ~/ 12;
      final remainder = months % 12;
      age =
          '$years ${years == 1 ? 'año' : 'años'}${remainder == 0 ? '' : ' y $remainder ${remainder == 1 ? 'mes' : 'meses'}'}';
    }
    return estimated ? '$age (aprox.)' : age;
  }
}

class PetPage {
  const PetPage({required this.pets, required this.species, this.nextCursor});
  final List<Pet> pets;
  final List<String> species;
  final String? nextCursor;
}

class AdoptionApi {
  const AdoptionApi(this.api, this.session);

  final ApiClient api;
  final Session session;

  Future<PetDetail> detail(int id) async {
    try {
      return PetDetail.fromJson(await api.get('/api/adopcion/mascotas/$id/'));
    } on ApiException catch (error) {
      if (error.status == 404) {
        throw const ApiException(
          'Esta mascota ya no está disponible para adopción.',
          status: 404,
        );
      }
      rethrow;
    }
  }

  Future<PetPage> catalogPage({String? cursor, String species = ''}) async {
    const path = '/api/adopcion/catalogo/';
    final parameters = {
      'cursor': ?cursor,
      if (species.isNotEmpty) 'especie': species,
    };
    final query = Uri(
      path: path,
      queryParameters: parameters.isEmpty ? null : parameters,
    );
    final row = _object(await api.get(query.toString()));
    final pets = _rows(row['results'])
        .map((value) => Pet.fromJson(_object(value)))
        .toList();
    if (pets.length > 24) throw _invalidResponse;
    final choices = _rows(row['species']).map(_text).toSet().toList();
    final next = row['next'];
    String? nextCursor;
    if (next != null) {
      if (next is! String) throw _invalidResponse;
      final uri = Uri.tryParse(next);
      if (uri == null) throw _invalidResponse;
      final target = api.base.resolveUri(uri);
      final allowed = {'cursor', 'especie'};
      nextCursor = target.queryParameters['cursor'];
      if (target.scheme != api.base.scheme ||
          target.host != api.base.host ||
          target.port != api.base.port ||
          target.userInfo.isNotEmpty ||
          target.path != path ||
          target.hasFragment ||
          target.queryParametersAll.values.any(
            (values) => values.length != 1,
          ) ||
          target.queryParameters.keys.any((key) => !allowed.contains(key)) ||
          (target.queryParameters['especie'] ?? '') != species ||
          nextCursor == null ||
          nextCursor.isEmpty ||
          nextCursor.length > 2048 ||
          nextCursor == cursor) {
        throw _invalidResponse;
      }
    }
    return PetPage(pets: pets, species: choices, nextCursor: nextCursor);
  }

  Future<List<Pet>> catalog() async {
    final response = _rows(await api.get('/api/adopcion/mascotas/'));
    return response.map((row) => Pet.fromJson(_object(row))).toList();
  }

  Future<int> request(int petId, String description) async {
    final result = await session.authorized(
      (token) => api.post('/api/adopcion/solicitudes/', {
        'id_mascota': petId,
        'observaciones': description.trim(),
      }, token: token),
    );
    if (result is! Map<String, dynamic> ||
        result['id_solicitud_adopcion'] is! int ||
        (result['id_solicitud_adopcion'] as int) <= 0) {
      throw const ApiException(
        'No pudimos confirmar el resultado. Revisa Mis solicitudes antes de volver a enviar.',
      );
    }
    return result['id_solicitud_adopcion'] as int;
  }

  Future<int> requestEvaluation(int petId, Map<String, dynamic> answers) async {
    if (session.account?.adoptionEvaluation != true) {
      throw const ApiException(
        'El servidor todavía no admite este formulario. Actualiza tu sesión.',
      );
    }
    final result = await session.authorized(
      (token) => api.post('/api/adopcion/solicitudes/evaluacion/', {
        'id_mascota': petId,
        'evaluacion': answers,
      }, token: token),
    );
    if (result is! Map ||
        result['id_solicitud_adopcion'] is! int ||
        (result['id_solicitud_adopcion'] as int) <= 0) {
      throw const ApiException(
        'No pudimos confirmar el envío. Revisa Mis solicitudes antes de volver a enviar.',
      );
    }
    return result['id_solicitud_adopcion'] as int;
  }

  Future<AdoptionRequestPage> requestPage({String? before}) async {
    if (before != null && !RegExp(r'^[1-9][0-9]{0,9}$').hasMatch(before)) {
      throw _invalidResponse;
    }
    final value = _object(
      await session.authorized(
        (token) => api.get(
          '/api/adopcion/solicitudes/mias/${before == null ? '' : '?antes=$before'}',
          token: token,
        ),
      ),
    );
    final next = value['next_cursor'];
    if (next != null &&
        (next is! String || !RegExp(r'^[1-9][0-9]{0,18}$').hasMatch(next))) {
      throw _invalidResponse;
    }
    return AdoptionRequestPage(
      _rows(value['results'])
          .map((row) => AdoptionRequest.fromJson(_object(row)))
          .toList(),
      next as String?,
    );
  }

  Future<List<AdoptionRequest>> mine() async {
    final response = await session.authorized(
      (token) =>
          api.get('/api/seguridad/operaciones/mis-registros/', token: token),
    );
    final rows = _rows(_object(response)['adopciones']);
    return rows.map((row) => AdoptionRequest.fromJson(_object(row))).toList();
  }
}

const _invalidResponse = ApiException(
  'El servidor devolvió datos inesperados. Intenta actualizar de nuevo.',
);

Map<String, dynamic> _object(Object? value) {
  if (value is Map<String, dynamic>) return value;
  throw _invalidResponse;
}

List<dynamic> _rows(Object? value) {
  if (value is List<dynamic>) return value;
  throw _invalidResponse;
}

int _id(Object? value) {
  if (value is int && value > 0) return value;
  throw _invalidResponse;
}

String _text(Object? value) {
  if (value is String && value.trim().isNotEmpty) return value;
  throw _invalidResponse;
}

String? _optionalText(Object? value) {
  if (value == null) return null;
  if (value is String) return value.trim().isEmpty ? null : value;
  throw _invalidResponse;
}

String _petName(Object? value) {
  if (value is! String) throw _invalidResponse;
  return value.trim().isEmpty ? 'Sin nombre registrado' : value;
}

class AdoptionRequestPage {
  const AdoptionRequestPage(this.rows, this.next);
  final List<AdoptionRequest> rows;
  final String? next;
}
