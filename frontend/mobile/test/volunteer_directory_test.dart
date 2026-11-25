import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/explore/explore_screens.dart';

void main() {
  for (final accepts in [true, false]) {
    testWidgets(
      'Volunteer directory only offers accepting foundations: $accepts',
      (tester) async {
        var reads = 0;
        final api = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((request) async {
            expect(request.method, 'GET');
            expect(request.url.path, '/api/red/organizaciones/');
            reads++;
            return http.Response(
              jsonEncode([
                {
                  'id': 1,
                  'nombre': 'Fundación abierta QA',
                  'tipo': 'Fundación',
                  'acepta_voluntarios': accepts,
                },
                {
                  'id': 2,
                  'nombre': 'Fundación cerrada QA',
                  'tipo': 'Fundación',
                  'acepta_voluntarios': false,
                },
                {
                  'id': 3,
                  'nombre': 'Fundación sin publicar QA',
                  'tipo': 'Fundación',
                },
                {
                  'id': 4,
                  'nombre': 'Veterinaria QA',
                  'tipo': 'Veterinaria',
                  'acepta_voluntarios': true,
                },
              ]),
              200,
              headers: {'content-type': 'application/json; charset=utf-8'},
            );
          }),
        );
        final session = Session(api);
        addTearDown(() {
          session.dispose();
          api.close();
        });
        await session.restore();
        await tester.pumpWidget(
          MaterialApp(
            home: PublicListScreen(
              api: api,
              session: session,
              path: '/api/red/organizaciones/',
              title: 'Tiempo y voluntariado',
              kind: 'help',
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(
          find.text('Fundación abierta QA'),
          accepts ? findsOneWidget : findsNothing,
        );
        expect(find.text('Fundación cerrada QA'), findsNothing);
        expect(find.text('Fundación sin publicar QA'), findsNothing);
        expect(find.text('Veterinaria QA'), findsNothing);
        if (!accepts) {
          expect(
            find.text(
              'Todavía no hay información publicada en esta categoría.',
            ),
            findsOneWidget,
          );
        }
        expect(reads, 1);
        expect(tester.takeException(), isNull);
      },
    );
  }
}
