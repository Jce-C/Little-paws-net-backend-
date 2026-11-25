import 'dart:convert';
import 'dart:io';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/io_client.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/core/operation_key.dart';
import 'package:little_paws_net/pets/owned_pets_api.dart';

class _LocalHttp extends HttpOverrides {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  const credentials = String.fromEnvironment('LPN_REAL_QA_CREDENTIALS');
  const evidence = String.fromEnvironment('LPN_REAL_QA_EVIDENCE');
  test('Real MySQL account profile and private pet creation integrate without duplicate or public exposure', () async {
    final data = jsonDecode(
      File(credentials).readAsStringSync(),
    ) as Map<String, dynamic>;
    expect((data['email'] as String).endsWith('@example.invalid'), isTrue);
    final api = ApiClient(
      base: Uri.parse('http://127.0.0.1:8018'),
      client: IOClient(_LocalHttp().createHttpClient(null)),
    );
    final own = Session(api), other = Session(api);
    addTearDown(api.close);
    addTearDown(own.dispose);
    addTearDown(other.dispose);
    await own.restore();
    await other.restore();
    await own.login(
      data['email'] as String,
      data['password'] as String,
      remember: false,
    );
    final original = own.account!;
    await own.updateProfile(
      name: 'Cuenta QA integración',
      phone: '+57 300 000 0000',
    );
    final profile = await own.authorized(
      (token) => api.get('/api/auth/perfil/', token: token),
    ) as Map;
    expect(profile['nombre'], 'Cuenta QA integración');
    expect(profile['telefono'], '+57 300 000 0000');
    expect(profile['email'], original.email);
    final body = <String, Object?>{
      'nombre': 'Moka QA ${DateTime.now().microsecondsSinceEpoch}',
      'especie': 'Especie libre QA',
      'raza': 'Raza no catalogada QA',
      'edad_meses': 0,
      'color': 'Gris',
      'descripcion': 'Ficha privada sintética',
    };
    final bytes = (await rootBundle.load('assets/access/login-pets.webp'))
        .buffer
        .asUint8List();
    final key = newOperationKey();
    Future<Object?> send() => own.authorized(
      (token) => api.uploadImage(
        '/api/mascotas/personales/',
        body,
        bytes,
        token: token,
        operationKey: key,
      ),
    );
    final first = await send() as Map;
    final second = await send() as Map;
    expect(second['id_mascota'], first['id_mascota']);
    final id = first['id_mascota'] as int;
    final pets = await OwnedPetsApi(api, own).page(limit: 3);
    final created = pets.rows.singleWhere((p) => p.pet.id == id);
    expect(created.status, 'Con dueño');
    expect(created.activeCustody, isFalse);
    final detail = await own.authorized(
      (token) => api.get('/api/mascotas/personales/$id/', token: token),
    ) as Map;
    expect(detail['especie'], body['especie']);
    expect(detail['raza'], body['raza']);
    final photo = detail['foto_miniatura'] as Map;
    final stored = base64Decode(photo['datos'] as String);
    expect(stored.length, lessThanOrEqualTo(16 * 1024));
    expect(photo['ancho'] as int, lessThanOrEqualTo(160));
    expect(photo['alto'] as int, lessThanOrEqualTo(160));
    await expectLater(
      api.get('/api/mascotas/personales/$id/'),
      throwsA(isA<ApiException>().having((e) => e.status, 'status', 401)),
    );
    await expectLater(
      api.get('/api/adopcion/mascotas/$id/'),
      throwsA(isA<ApiException>().having((e) => e.status, 'status', 404)),
    );
    await other.login(
      data['operator'] as String,
      data['password'] as String,
      remember: false,
    );
    await expectLater(
      other.authorized(
        (token) => api.get('/api/mascotas/personales/$id/', token: token),
      ),
      throwsA(
        isA<ApiException>().having((e) => e.status, 'status', anyOf(403, 404)),
      ),
    );
    await own.updateProfile(name: original.name, phone: original.phone);
    if (evidence.isNotEmpty) {
      File(evidence).writeAsStringSync(
        jsonEncode({
          'solo_loopback_QA': true,
          'pet_id': id,
          'perfil_actualizado_y_restaurado': true,
          'reintento_mismo_id': true,
          'limite_preview': 3,
          'foto_privada_bytes': stored.length,
          'especie_raza_libres_conservadas': true,
          'acceso_ajeno_denegado': true,
          'sin_acceso_anonimo': true,
          'fuera_de_adopcion_publica': true,
        }),
      );
    }
  }, skip: credentials.isEmpty);
}
