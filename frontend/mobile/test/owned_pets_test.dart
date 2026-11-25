import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/pets/owned_pets_api.dart';
import 'package:little_paws_net/pets/owned_pets_screens.dart';

http.Response json(Object value, {int status = 200}) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

Map<String, Object?> medicalRecord() => {
  'id': 8,
  'nombre': 'Luna QA',
  'atenciones_recientes_maximo_50': [
    {
      'id': 3,
      'detalle': 'Atención sintética original QA',
      'autor': 'Profesional QA',
      'fecha': '2026-11-18T12:00:00Z',
      'enmiendas': [
        {
          'detalle': 'Corrección sintética QA',
          'motivo': 'Aclaración de prueba',
          'fecha': '2026-11-18T13:00:00Z',
        },
      ],
    },
  ],
};

void main() {
  late ApiClient client;
  late Session session;
  var denied = false;

  setUp(() async {
    denied = false;
    client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        switch (request.url.path) {
          case '/api/auth/token/':
            return json({'access': 'access', 'refresh': 'refresh'});
          case '/api/auth/perfil/':
            return json({'nombre': 'Ana QA', 'email': 'ana@example.invalid'});
          case '/api/auth/token/revoke/':
            return json({});
          case '/api/mascotas/mias/':
            expect(request.headers['authorization'], 'Bearer access');
            return json([
              {
                'id_mascota': 8,
                'nombre': 'Luna QA',
                'especie': 'Perro',
                'raza': null,
                'estado': 'Con dueño',
                'custodia_vigente': false,
              },
            ]);
          case '/api/seguridad/operaciones/registros/expediente/8/':
            expect(request.headers['authorization'], 'Bearer access');
            return denied ? json({}, status: 403) : json(medicalRecord());
          default:
            throw StateError('Unexpected route');
        }
      }),
    );
    session = Session(client);
    await session.restore();
    await session.login('ana@example.invalid', 'test-password');
  });

  tearDown(() {
    session.dispose();
    client.close();
  });

  testWidgets('Own pet opens the real record with original and amendment', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(home: OwnedPetsScreen(api: OwnedPetsApi(client, session))),
    );
    await tester.pumpAndSettle();
    expect(find.text('Luna QA'), findsOneWidget);
    await tester.tap(find.text('Ver expediente'));
    await tester.pumpAndSettle();
    expect(find.text('Atención sintética original QA'), findsOneWidget);
    expect(find.text('Corrección sintética QA'), findsOneWidget);
    expect(find.text('Motivo: Aclaración de prueba'), findsOneWidget);
  });

  testWidgets(
    'Permission rejection on refresh removes previously loaded clinical data',
    (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: PetMedicalRecordScreen(
            api: OwnedPetsApi(client, session),
            petId: 8,
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Atención sintética original QA'), findsOneWidget);
      denied = true;
      await tester.tap(find.byTooltip('Actualizar expediente'));
      await tester.pumpAndSettle();
      expect(find.text('Atención sintética original QA'), findsNothing);
      expect(find.text('Corrección sintética QA'), findsNothing);
      expect(
        find.text('Tu cuenta no tiene acceso para realizar esta acción.'),
        findsOneWidget,
      );
    },
  );

  testWidgets('Signing out clears clinical view and offers sign in', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: PetMedicalRecordScreen(
          api: OwnedPetsApi(client, session),
          petId: 8,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await session.logout();
    await tester.pumpAndSettle();
    expect(find.text('Atención sintética original QA'), findsNothing);
    expect(find.text('Iniciar sesión'), findsOneWidget);
  });

  test(
    'Malformed clinical document does not become an empty medical history',
    () async {
      final broken = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          if (request.url.path == '/api/auth/token/') {
            return json({'access': 'access', 'refresh': 'refresh'});
          }
          if (request.url.path == '/api/auth/perfil/') {
            return json({'nombre': 'Ana', 'email': 'ana@example.invalid'});
          }
          return json({
            'id': 8,
            'nombre': 'Luna QA',
            'atenciones_recientes_maximo_50': null,
          });
        }),
      );
      final brokenSession = Session(broken);
      addTearDown(broken.close);
      addTearDown(brokenSession.dispose);
      await brokenSession.login('ana@example.invalid', 'test-password');
      await expectLater(
        OwnedPetsApi(broken, brokenSession).record(8),
        throwsA(isA<ApiException>()),
      );
    },
  );
}
