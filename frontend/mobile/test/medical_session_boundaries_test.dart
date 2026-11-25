import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/pets/owned_pets_api.dart';
import 'package:little_paws_net/pets/owned_pets_screens.dart';

http.Response response(Object value, {int status = 200}) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

Map<String, Object> record(String detail) => {
  'id': 8,
  'nombre': 'Mascota QA',
  'atenciones_recientes_maximo_50': [
    {
      'id': 3,
      'detalle': detail,
      'autor': 'Profesional QA',
      'fecha': '2026-11-18T12:00:00Z',
      'enmiendas': [],
    },
  ],
};

void main() {
  late ApiClient client;
  late Session session;
  var reads = 0;
  var identity = 'ana@example.invalid';
  late Future<http.Response> Function(http.Request request) readRecord;

  setUp(() async {
    reads = 0;
    identity = 'ana@example.invalid';
    readRecord = (_) async => response(record('Dato privado de Ana QA'));
    client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        switch (request.url.path) {
          case '/api/auth/token/':
            identity = (jsonDecode(request.body) as Map)['email'] as String;
            return response({
              'access': identity,
              'refresh': 'synthetic-refresh',
            });
          case '/api/auth/perfil/':
            return response({'nombre': 'Persona QA', 'email': identity});
          case '/api/auth/token/revoke/':
            return response({});
          case '/api/seguridad/operaciones/registros/expediente/8/':
            reads++;
            return readRecord(request);
          default:
            throw StateError('Unexpected request: ${request.url.path}');
        }
      }),
    );
    session = Session(client);
    await session.restore();
    await session.login(identity, 'synthetic-password');
  });

  tearDown(() {
    session.dispose();
    client.close();
  });

  Future<void> openRecord(WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: PetMedicalRecordScreen(
          api: OwnedPetsApi(client, session),
          petId: 8,
        ),
      ),
    );
    await tester.pump();
  }

  testWidgets('A late clinical response cannot restore data after logout', (
    tester,
  ) async {
    final pending = Completer<http.Response>();
    readRecord = (_) => pending.future;
    await openRecord(tester);
    expect(reads, 1);

    await session.logout();
    await tester.pumpAndSettle();
    pending.complete(response(record('Dato privado de Ana QA')));
    await tester.pumpAndSettle();

    expect(find.text('Dato privado de Ana QA'), findsNothing);
    expect(find.text('Iniciar sesión'), findsOneWidget);
    expect(find.text('QR de identificación'), findsNothing);
    expect(reads, 1);
    expect(tester.takeException(), isNull);
  });

  testWidgets('Changing account rechecks access and rejects the old response', (
    tester,
  ) async {
    final pending = Completer<http.Response>();
    readRecord = (request) {
      if (request.headers['authorization'] == 'Bearer ana@example.invalid') {
        return pending.future;
      }
      expect(request.headers['authorization'], 'Bearer carlos@example.invalid');
      return Future.value(response({}, status: 403));
    };
    await openRecord(tester);
    await session.login('carlos@example.invalid', 'synthetic-password');
    await tester.pumpAndSettle();
    pending.complete(response(record('Dato privado de Ana QA')));
    await tester.pumpAndSettle();

    expect(reads, 2);
    expect(find.text('Dato privado de Ana QA'), findsNothing);
    expect(find.text('QR de identificación'), findsNothing);
    expect(
      find.text('Tu cuenta no tiene acceso para realizar esta acción.'),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });

  testWidgets(
    'Refresh conceals the old record and 403 only retries on request',
    (tester) async {
      await openRecord(tester);
      await tester.pumpAndSettle();
      expect(find.text('Dato privado de Ana QA'), findsOneWidget);
      final pending = Completer<http.Response>();
      readRecord = (_) => pending.future;
      await tester.tap(find.byTooltip('Actualizar expediente'));
      await tester.pump();
      expect(find.text('Dato privado de Ana QA'), findsNothing);
      expect(find.text('QR de identificación'), findsNothing);
      pending.complete(response({}, status: 403));
      await tester.pumpAndSettle();
      await tester.pump(const Duration(seconds: 5));
      expect(reads, 2);

      readRecord = (_) async =>
          response(record('Registro QA autorizado de nuevo'));
      await tester.tap(find.text('Reintentar'));
      await tester.pumpAndSettle();
      expect(reads, 3);
      expect(find.text('Registro QA autorizado de nuevo'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Reauthentication of the same account hides previously loaded clinical data',
    (tester) async {
      await openRecord(tester);
      await tester.pumpAndSettle();
      expect(find.text('Dato privado de Ana QA'), findsOneWidget);
      readRecord = (_) async => response({}, status: 403);
      await session.login('ana@example.invalid', 'synthetic-password');
      await tester.pumpAndSettle();
      expect(reads, 2);
      expect(find.text('Dato privado de Ana QA'), findsNothing);
      expect(find.text('QR de identificación'), findsNothing);
      expect(tester.takeException(), isNull);
    },
  );
}
