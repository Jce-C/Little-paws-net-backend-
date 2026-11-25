import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/design/decision_card.dart';
import 'package:little_paws_net/explore/help_program.dart';
import 'package:little_paws_net/explore/explore_screens.dart';

Map<String, Object?> program() => {
  'version': 'v1',
  'publicada': false,
  'actividades': [
    {
      'titulo': 'Paseos QA',
      'descripcion': 'Paseos acompañados de ejemplo.',
      'horario': 'Horario por acordar',
      'requisitos': 'Inducción supervisada',
    },
  ],
  'canales': [
    {
      'titulo': 'Sitio QA',
      'descripcion': 'Canal ficticio de prueba',
      'url': 'https://example.invalid/ayuda',
    },
  ],
};
http.Response reply(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

void main() {
  testWidgets(
    'Official channels open anonymously only on explicit navigation',
    (tester) async {
      var requests = 0;
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          requests++;
          expect(request.headers.containsKey('authorization'), isFalse);
          expect(request.url.path, '/api/red/organizaciones/');
          return reply([
            {
              'id': 1,
              'nombre': 'Fundación QA',
              'tipo': 'Fundación',
              'ciudad': 'Riohacha',
              'programa_ayuda': program(),
            },
            {
              'id': 2,
              'nombre': 'Sin canales publicados',
              'tipo': 'Fundación',
              'programa_ayuda': null,
            },
          ]);
        }),
      );
      final session = Session(api);
      addTearDown(() {
        session.dispose();
        api.close();
      });
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: HelpScreen(api: api, session: session),
        ),
      );
      await tester.pumpAndSettle();
      expect(requests, 0);
      final link = find.text('Canales publicados por las organizaciones');
      await tester.scrollUntilVisible(link, 150);
      await tester.tap(link);
      await tester.pumpAndSettle();
      expect(requests, 1);
      expect(find.text('Sitio QA'), findsOneWidget);
      expect(find.text('Sin canales publicados'), findsNothing);
      expect(find.text('Manifestar mi interés'), findsNothing);
      expect(find.text('Paseos QA'), findsNothing);
      expect(tester.takeException(), isNull);
    },
  );

  test('Public program validates HTTPS, nested fields and limits', () {
    expect(programRows(program()['actividades']).single['titulo'], 'Paseos QA');
    expect(
      () => programRows([
        {'titulo': 'Solo título'},
      ]),
      throwsFormatException,
    );
    expect(
      () =>
          programRows(List.filled(9, (program()['actividades'] as List).first)),
      throwsFormatException,
    );
    expect(
      () => programRows([
        {'titulo': 'QA', 'descripcion': 'QA', 'url': 'javascript:alert(1)'},
      ], channels: true),
      throwsFormatException,
    );
    expect(
      () => programRows([
        {
          'titulo': 'QA',
          'descripcion': 'QA',
          'url': 'https://user:secret@example.invalid',
        },
      ], channels: true),
      throwsFormatException,
    );
  });

  testWidgets(
    'Activity reveals requirements and passes exact title without a request',
    (tester) async {
      String? selected;
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Scaffold(
            body: ListView(
              children: [
                HelpProgramInfo(
                  row: {'programa_ayuda': program()},
                  onActivity: (title) => selected = title,
                ),
              ],
            ),
          ),
        ),
      );
      await tester.tap(find.text('Paseos QA'));
      await tester.pumpAndSettle();
      expect(find.text('Requisitos: Inducción supervisada'), findsOneWidget);
      await tester.tap(find.text('Me interesa esta actividad'));
      expect(selected, 'Paseos QA');
      expect(tester.takeException(), isNull);
    },
  );

  for (final code in [200, 403, 409]) {
    testWidgets(
      'Editor save $code confirms success or preserves a denied/conflicting draft',
      (tester) async {
        Map<String, dynamic>? sent;
        var saves = 0;
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
            if (request.method == 'PATCH') {
              saves++;
              sent = jsonDecode(request.body) as Map<String, dynamic>;
              return code == 200
                  ? reply({...sent!, 'version': 'v2'})
                  : reply({
                      'detalle': code == 403
                          ? 'Permiso revocado'
                          : 'La convocatoria cambió',
                    }, code);
            }
            return reply(program());
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
            theme: lpnTheme(),
            home: HelpProgramEditor(api: api, session: session, id: 1),
          ),
        );
        await tester.pumpAndSettle();
        await tester.enterText(
          find.byType(TextFormField).first,
          'Paseos editados QA',
        );
        await tester.pump();
        expect(saves, 0);
        // The save action stays in the bottom bar even with a long editor.
        await tester.tap(find.text('Guardar convocatoria'));
        await tester.pumpAndSettle();
        expect(saves, 1);
        expect(sent!['version'], 'v1');
        expect(
          (sent!['actividades'] as List).first['titulo'],
          'Paseos editados QA',
        );
        if (code == 200) {
          expect(
            find.text('Convocatoria guardada sin publicar.'),
            findsOneWidget,
          );
        } else if (code == 403) {
          expect(
            find.text('Tu cuenta no tiene acceso para realizar esta acción.'),
            findsOneWidget,
          );
          expect(find.byType(TextFormField), findsNothing);
        } else {
          expect(find.text('La convocatoria cambió'), findsOneWidget);
          expect(find.text('Paseos editados QA'), findsOneWidget);
        }
        expect(tester.takeException(), isNull);
      },
    );
  }

  testWidgets(
    'Decision hierarchy fits a small viewport with double text scale',
    (tester) async {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: MediaQuery(
            data: const MediaQueryData(
              size: Size(320, 640),
              textScaler: TextScaler.linear(2),
            ),
            child: Scaffold(
              body: ListView(
                children: [
                  DecisionCard(
                    onTap: () {},
                    child: const Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        DecisionHeading(
                          title: 'Organización de ejemplo',
                          contextLine: 'Fundación, Riohacha',
                        ),
                        SizedBox(height: 16),
                        Text('Información secundaria agrupada por proximidad.'),
                        SizedBox(height: 16),
                        DecisionAction('Conocer las actividades'),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text('Conocer las actividades'),
        150,
      );
      expect(tester.takeException(), isNull);
    },
  );
}
