import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';

void main() {
  late ApiClient client;
  late Session session;
  late AdoptionApi adoption;
  Object? payload;
  var submissions = 0;

  setUp(() async {
    submissions = 0;
    client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        if (request.url.path == '/api/auth/token/') {
          return http.Response(
            jsonEncode({'access': 'access', 'refresh': 'refresh'}),
            200,
          );
        }
        if (request.url.path == '/api/auth/perfil/') {
          return http.Response(
            jsonEncode({'nombre': 'Ana', 'email': 'ana@example.invalid'}),
            200,
          );
        }
        if (request.method == 'POST') submissions++;
        return http.Response(jsonEncode(payload), 200);
      }),
    );
    session = Session(client);
    adoption = AdoptionApi(client, session);
    await session.login('ana@example.invalid', 'test-password');
  });

  tearDown(() {
    session.dispose();
    client.close();
  });

  test(
    'Catalog rejects malformed documents and rows with a recoverable error',
    () async {
      for (final invalid in [
        null,
        {},
        [null],
        [
          {'id_mascota': '1', 'nombre': 'Luna'},
        ],
        [
          {'id_mascota': 1, 'nombre': 5},
        ],
      ]) {
        payload = invalid;
        await expectLater(adoption.catalog(), throwsA(isA<ApiException>()));
      }
    },
  );

  test('Catalog accepts empty results and missing optional breed', () async {
    payload = [];
    expect(await adoption.catalog(), isEmpty);
    payload = [
      {'id_mascota': 1, 'nombre': 'Luna', 'especie': 'Perro'},
    ];
    final pet = (await adoption.catalog()).single;
    expect(pet.name, 'Luna');
    expect(pet.summary, 'Perro');
  });

  test('Own requests reject malformed status without a cast error', () async {
    payload = {
      'adopciones': [
        {'id_solicitud_adopcion': 2, 'estado_adopcion__nombre': null},
      ],
    };
    await expectLater(adoption.mine(), throwsA(isA<ApiException>()));
  });

  test(
    'Own requests remain compatible with the older tracking response',
    () async {
      payload = {
        'adopciones': [
          {'id_solicitud_adopcion': 2, 'estado_adopcion__nombre': 'Pendiente'},
        ],
      };
      final request = (await adoption.mine()).single;
      expect(request.id, 2);
      expect(request.petName, isNull);
    },
  );

  test('Ambiguous confirmation is not reported as success or automatically repeated', () async {
    payload = {};
    await expectLater(
      adoption.request(1, 'Quiero adoptar'),
      throwsA(
        isA<ApiException>().having(
          (e) => e.message,
          'guidance',
          contains('Mis solicitudes'),
        ),
      ),
    );
    expect(submissions, 1);
  });
}
