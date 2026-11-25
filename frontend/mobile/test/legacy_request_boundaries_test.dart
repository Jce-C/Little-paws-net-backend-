import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/adoption/adoption_screens.dart';

void main() {
  late ApiClient client;
  late Session session;
  var writes = 0;
  setUp(() async {
    writes = 0;
    client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((r) async {
        Object body = {};
        if (r.url.path == '/api/auth/token/') {
          body = {'access': 'synthetic', 'refresh': 'synthetic-refresh'};
        } else if (r.url.path == '/api/auth/perfil/') {
          body = {'nombre': 'Persona QA', 'email': 'qa@example.invalid'};
        } else if (r.url.path == '/api/adopcion/solicitudes/') {
          writes++;
          body = {'id_solicitud_adopcion': 1};
        }
        return http.Response(
          jsonEncode(body),
          200,
          headers: {'content-type': 'application/json'},
        );
      }),
    );
    session = Session(client);
    await session.restore();
    await session.login('qa@example.invalid', 'synthetic', remember: false);
  });
  tearDown(() {
    session.dispose();
    client.close();
  });
  Future<void> open(WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (context) => Scaffold(
            body: TextButton(
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => RequestDialog(
                    pet: const Pet(id: 1, name: 'Luna QA', species: 'Perro'),
                    api: AdoptionApi(client, session),
                    fullPage: true,
                  ),
                ),
              ),
              child: const Text('Abrir'),
            ),
          ),
        ),
      ),
    );
    await tester.tap(find.text('Abrir'));
    await tester.pumpAndSettle();
  }

  testWidgets(
    'Legacy compatibility draft can be kept or explicitly discarded without sending',
    (tester) async {
      await open(tester);
      final field = find.byKey(const Key('adoption-note'));
      await tester.ensureVisible(field);
      await tester.enterText(field, 'Borrador de adopción');
      await tester.pump();
      await tester.tap(find.text('Cancelar'));
      await tester.pumpAndSettle();
      expect(find.text('¿Descartar la solicitud?'), findsOneWidget);
      await tester.tap(find.text('Seguir editando'));
      await tester.pumpAndSettle();
      expect(
        tester.widget<TextField>(field).controller!.text,
        'Borrador de adopción',
      );
      await tester.tap(find.text('Cancelar'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Descartar'));
      await tester.pumpAndSettle();
      expect(find.text('Abrir'), findsOneWidget);
      expect(writes, 0);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Legacy compatibility clears its draft on same-account reauthentication',
    (tester) async {
      await open(tester);
      final field = find.byKey(const Key('adoption-note'));
      await tester.ensureVisible(field);
      await tester.enterText(field, 'Borrador de sesión anterior');
      await tester.pump();
      await session.updateProfile(name: 'Nombre editado');
      await tester.pumpAndSettle();
      expect(
        tester.widget<TextField>(field).controller!.text,
        'Borrador de sesión anterior',
      );
      await session.login('qa@example.invalid', 'synthetic', remember: false);
      await tester.pumpAndSettle();
      await tester.ensureVisible(field);
      expect(tester.widget<TextField>(field).controller!.text, isEmpty);
      expect(writes, 0);
      expect(tester.takeException(), isNull);
    },
  );
}
