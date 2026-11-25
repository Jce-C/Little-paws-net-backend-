import '../core/inline_webp.dart';

import 'dart:typed_data';

import '../adoption/adoption_api.dart';
import '../auth/session.dart';
import '../core/api_client.dart';

class OwnedPet {
  const OwnedPet(this.pet, this.status, this.activeCustody, {this.personal});
  final Pet pet;
  final String status;
  final bool activeCustody;
  final Map<String, dynamic>? personal;
}

class MedicalAmendment {
  const MedicalAmendment(this.detail, this.reason, this.date);
  final String detail;
  final String reason;
  final DateTime date;
}

class MedicalEntry {
  const MedicalEntry(
    this.id,
    this.detail,
    this.author,
    this.date,
    this.amendments,
  );
  final int id;
  final String detail;
  final String author;
  final DateTime date;
  final List<MedicalAmendment> amendments;
}

class PetMedicalRecord {
  const PetMedicalRecord(this.id, this.name, this.entries, {this.photo});
  final Uint8List? photo;
  final int id;
  final String name;
  final List<MedicalEntry> entries;
}

class PetQr {
  const PetQr(this.code, this.expires);
  final String code;
  final DateTime expires;
}

class OwnedPetsApi {
  const OwnedPetsApi(this.api, this.session);
  final ApiClient api;
  final Session session;

  Future<PetQr> generateQr(int id) async {
    final row = _map(
      await session.authorized(
        (token) => api.post('/api/mascotas/$id/qr/', {}, token: token),
      ),
    );
    final code = _text(row['codigo']);
    final expires = _date(row['expira']);
    if (!RegExp(r'^[A-Za-z0-9_-]{32,100}$').hasMatch(code) ||
        !expires.isAfter(DateTime.now())) {
      throw _invalid;
    }
    return PetQr(code, expires);
  }

  Future<List<OwnedPet>> mine() async => (await page()).rows;
  Future<OwnedPetPage> page({String? before, int limit = 20}) async {
    if (limit < 1 ||
        limit > 20 ||
        (before != null && !RegExp(r'^[1-9][0-9]{0,9}$').hasMatch(before))) {
      throw _invalid;
    }
    final result = await session.authorized(
      (token) => api.get(
        '/api/mascotas/mias/?pagina=1${limit == 20 ? '' : '&limite=$limit'}${before == null ? '' : '&antes=$before'}',
        token: token,
      ),
    );
    final rows = _list(result is Map ? result['results'] : result);
    final next = result is Map ? result['next_cursor'] : null;
    if (next != null &&
        (next is! String || !RegExp(r'^[1-9][0-9]{0,18}$').hasMatch(next))) {
      throw _invalid;
    }
    return OwnedPetPage(
      rows.map((value) {
        final row = _map(value);
        final custody = row['custodia_vigente'];
        if (custody is! bool) throw _invalid;
        final personal = row['personal'] is Map<String, dynamic>
            ? row['personal'] as Map<String, dynamic>
            : null;
        return OwnedPet(
          Pet.fromJson({
            ...row,
            if (personal != null &&
                personal['raza'] is String &&
                personal['raza'] != '')
              'raza': personal['raza'],
          }),
          _text(row['estado']),
          custody,
          personal: personal,
        );
      }).toList(),
      next as String?,
    );
  }

  Future<PetMedicalRecord> record(int id) async {
    final row = _map(
      await session.authorized(
        (token) => api.get(
          '/api/seguridad/operaciones/registros/expediente/$id/',
          token: token,
        ),
      ),
    );
    if (_id(row['id']) != id) throw _invalid;
    final name = row['nombre'];
    if (name is! String) throw _invalid;
    final entries = _list(row['atenciones_recientes_maximo_50']).map((value) {
      final entry = _map(value);
      final amendments = _list(entry['enmiendas']).map((value) {
        final amendment = _map(value);
        return MedicalAmendment(
          _text(amendment['detalle']),
          _text(amendment['motivo']),
          _date(amendment['fecha']),
        );
      }).toList();
      return MedicalEntry(
        _id(entry['id']),
        _text(entry['detalle']),
        _text(entry['autor']),
        _date(entry['fecha']),
        amendments,
      );
    }).toList();
    return PetMedicalRecord(
      _id(row['id']),
      name.trim().isEmpty ? 'Sin nombre registrado' : name,
      entries,
      photo: medicalPhoto(row['foto_miniatura']),
    );
  }
}

const _invalid = ApiException(
  'No pudimos interpretar los datos de la mascota. Intenta actualizar de nuevo.',
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

DateTime _date(Object? value) {
  if (value is! String) throw _invalid;
  final date = DateTime.tryParse(value);
  if (date == null) throw _invalid;
  return date;
}

Uint8List? medicalPhoto(Object? value) => inlineWebp(value);

class OwnedPetPage {
  const OwnedPetPage(this.rows, this.next);
  final List<OwnedPet> rows;
  final String? next;
}
