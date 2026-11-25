import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/explore/help_management.dart';

http.Response reply(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

void main() {
  for (final denied in [false, true]) {
    testWidgets(
      'Help management ${denied ? 'hides private content after revocation' : 'saves the loaded version and confirms discard'}',
      (tester) async {
        Map<String, dynamic>? sent;
        final api = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((request) async {
            if (request.url.path == '/api/auth/token/') {
              return reply({
                'access': 'synthetic',
                'refresh': 'synthetic-refresh',
              });
            }
            if (request.url.path == '/api/auth/perfil/') {
              return reply({
                'nombre': 'Responsable QA',
                'email': 'qa@example.invalid',
              });
            }
            final data = {
              'id': 1,
              'nombre': 'Organización QA',
              'version': 'v1',
              'acepta_voluntarios': false,
              'necesidades_ayuda': 'Alimentos QA',
              'ofrecimientos': [
                {
                  'id': 1,
                  'nombre': 'Persona QA',
                  'mensaje': 'Ofrecimiento privado QA',
                  'modalidad': 'especie',
                  'fecha': '2026-11-20T12:00:00Z',
                },
              ],
            };
            if (request.method == 'PATCH') {
              sent = jsonDecode(request.body) as Map<String, dynamic>;
              return denied
                  ? reply({'detalle': 'Permiso revocado'}, 403)
                  : reply({...data, ...sent!, 'version': 'v2'});
            }
            return reply(data);
          }),
        );
        final session = Session(api);
        addTearDown(() {
          session.dispose();
          api.close();
        });
        await session.restore();
        await session.login('qa@example.invalid', 'synthetic-password');
        await tester.pumpWidget(
          MaterialApp(
            home: Builder(
              builder: (context) => TextButton(
                onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => OrganizationHelpScreen(
                      api: api,
                      session: session,
                      id: 1,
                    ),
                  ),
                ),
                child: const Text('Abrir'),
              ),
            ),
          ),
        );
        await tester.tap(find.text('Abrir'));
        await tester.pumpAndSettle();
        await tester.scrollUntilVisible(
          find.text('Ofrecimiento privado QA'),
          200,
          scrollable: find.byType(Scrollable).first,
        );
        expect(find.text('Ofrecimiento privado QA'), findsOneWidget);
        await tester.scrollUntilVisible(
          find.byType(TextField),
          -200,
          scrollable: find.byType(Scrollable).first,
        );
        await tester.enterText(find.byType(TextField), 'Nueva necesidad QA');
        await tester.pump();
        await tester.tap(find.text('Guardar convocatoria'));
        await tester.pumpAndSettle();
        expect(sent?['version'], 'v1');
        expect(sent?['necesidades_ayuda'], 'Nueva necesidad QA');
        if (denied) {
          expect(find.text('Ofrecimiento privado QA'), findsNothing);
          expect(find.text('Guardar convocatoria'), findsNothing);
        } else {
          expect(find.text('Sin cambios pendientes'), findsOneWidget);
          await tester.enterText(find.byType(TextField), 'Borrador pendiente');
          await tester.pump();
          await tester.pageBack();
          await tester.pumpAndSettle();
          expect(find.text('¿Descartar cambios?'), findsOneWidget);
          await tester.tap(find.text('Seguir editando'));
          await tester.pumpAndSettle();
          expect(find.text('Borrador pendiente'), findsOneWidget);
        }
        expect(tester.takeException(), isNull);
      },
    );
  }
}
