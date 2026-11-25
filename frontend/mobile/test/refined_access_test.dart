import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/explore/help_management.dart';

void main() {
  setUp(() => FlutterSecureStorage.setMockInitialValues({}));
  for (final status in [200, 403, 503]) {
    testWidgets('Management shortcut respects permission and retry: $status', (
      tester,
    ) async {
      var reads = 0;
      final api = ApiClient(
        base: Uri.parse('https://qa.example.invalid'),
        client: MockClient((request) async {
          Object data;
          var code = 200;
          if (request.url.path == '/api/auth/token/') {
            data = {'access': 'synthetic', 'refresh': 'synthetic-refresh'};
          } else if (request.url.path == '/api/auth/perfil/') {
            data = {'nombre': 'Persona QA', 'email': 'qa@example.invalid'};
          } else {
            expect(request.url.path, '/api/ayudas/organizaciones/');
            expect(request.method, 'GET');
            reads++;
            code = status;
            data = status == 200
                ? [
                    {'id': 1, 'nombre': 'Organización QA'},
                  ]
                : {'detalle': 'No disponible'};
          }
          return http.Response(
            jsonEncode(data),
            code,
            headers: {'content-type': 'application/json'},
          );
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
          home: Scaffold(
            body: HelpManagementShortcut(api: api, session: session),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(reads, 1);
      expect(
        find.text('Gestionar ayudas de mi organización'),
        status == 200 ? findsOneWidget : findsNothing,
      );
      expect(
        find.text('Comprobar acceso de gestión'),
        status == 503 ? findsOneWidget : findsNothing,
      );
      if (status == 503) {
        await tester.tap(find.text('Comprobar acceso de gestión'));
        await tester.pumpAndSettle();
        expect(reads, 2);
      }
      expect(tester.takeException(), isNull);
    });
  }
}
