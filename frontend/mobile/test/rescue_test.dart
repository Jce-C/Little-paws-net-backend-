import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/rescue/rescue_api.dart';
import 'package:little_paws_net/rescue/rescue_screens.dart';

void main() {
  for (final anonymous in [false, true]) {
    testWidgets(
      'Report form searches city and confirms ${anonymous ? 'anonymous' : 'account'} submission',
      (tester) async {
        tester.view.physicalSize = const Size(393, 852);
        tester.view.devicePixelRatio = 1;
        if (anonymous) {
          tester.platformDispatcher.textScaleFactorTestValue = 2;
          addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
        }
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);
        var submissions = 0;
        final client = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((request) async {
            Object result;
            switch (request.url.path) {
              case '/api/auth/token/':
                result = {'access': 'access', 'refresh': 'refresh'};
              case '/api/auth/perfil/':
                result = {'nombre': 'Ana', 'email': 'ana@example.invalid'};
              case '/api/reportes/publicos/':
                result = {'results': [], 'next_cursor': null};
              case '/api/reportes/opciones/':
                result = {
                  'tipos': [
                    {'id_valor_maestro': 4, 'nombre': 'Encontrado'},
                  ],
                  'ciudades':
                      request.url.queryParameters['ciudad']!
                          .toLowerCase()
                          .startsWith('rio')
                      ? [
                          {
                            'id_ciudad': 7,
                            'nombre': 'Riohacha',
                            'departamento': 'La Guajira',
                          },
                        ]
                      : [],
                };
              case '/api/reportes/':
                submissions++;
                final data = jsonDecode(request.body) as Map;
                expect(data['ciudad_id'], 7);
                expect(data['tipo_reporte'], 4);
                expect(data['descripcion'], 'Animal encontrado de prueba');
                expect(
                  request.headers['authorization'],
                  anonymous ? isNull : 'Bearer access',
                );
                result = {
                  'id_reporte': 12,
                  'estado': 'Pendiente',
                  if (anonymous)
                    'codigo_gestion': 'clave-sintetica-solo-prueba',
                };
              case '/api/reportes/mios/':
                result = [
                  {
                    'id_reporte': 12,
                    'tipo': 'Encontrado',
                    'estado': 'Aceptado',
                    'descripcion': 'Animal encontrado de prueba',
                    'ciudad': 'Riohacha',
                    'caso': {
                      'id_caso': 8,
                      'estado': 'En proceso',
                      'fundacion': 'Fundación QA',
                    },
                  },
                ];
              default:
                throw StateError('Unexpected route ${request.url.path}');
            }
            return http.Response(
              jsonEncode(result),
              200,
              headers: {'content-type': 'application/json; charset=utf-8'},
            );
          }),
        );
        final session = Session(client);
        addTearDown(client.close);
        addTearDown(session.dispose);
        if (!anonymous) {
          await session.login('ana@example.invalid', 'test-password');
        }
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(body: RescueScreen(api: RescueApi(client, session))),
          ),
        );
        await tester.pumpAndSettle();
        await tester.ensureVisible(find.byTooltip('Reportar un animal'));
        await tester.tap(find.byTooltip('Reportar un animal'));
        await tester.pumpAndSettle();

        await tester.pumpAndSettle();
        Future<void> reveal(Finder target) async {
          await tester.scrollUntilVisible(
            target,
            140,
            scrollable: find
                .byWidgetPredicate(
                  (widget) =>
                      widget is Scrollable &&
                      widget.axisDirection == AxisDirection.down,
                )
                .first,
          );
          await tester.pumpAndSettle();
        }

        await reveal(find.text('Encontrado').last);
        await tester.tap(find.text('Encontrado').last);
        await tester.pumpAndSettle();
        await reveal(find.byKey(const Key('report-description')));
        await tester.enterText(
          find.byKey(const Key('report-description')),
          'Animal encontrado de prueba',
        );
        await tester.tap(find.byKey(const Key('report-next')));
        await tester.pumpAndSettle();
        await reveal(find.byKey(const Key('report-city')));
        await tester.enterText(find.byKey(const Key('report-city')), 'Rio');
        await tester.pump(const Duration(milliseconds: 400));
        await tester.pumpAndSettle();
        await tester.tap(find.text('Riohacha, La Guajira').last);
        await tester.pumpAndSettle();
        for (final entry in {
          'report-neighborhood': 'Barrio QA',
          'report-address': 'Referencia QA',
        }.entries) {
          await tester.scrollUntilVisible(
            find.byKey(Key(entry.key)),
            150,
            scrollable: find
                .byWidgetPredicate(
                  (widget) =>
                      widget is Scrollable &&
                      widget.axisDirection == AxisDirection.down,
                )
                .first,
          );
          await tester.enterText(find.byKey(Key(entry.key)), entry.value);
        }
        await tester.tap(find.byKey(const Key('report-next')));
        await tester.pumpAndSettle();
        await tester.tap(find.byKey(const Key('report-submit')));
        await tester.pumpAndSettle();
        expect(find.text('¡Reporte enviado!'), findsOneWidget);
        expect(submissions, 1);
        expect(tester.takeException(), isNull);
        if (anonymous) {
          await tester.scrollUntilVisible(
            find.text('clave-sintetica-solo-prueba'),
            150,
            scrollable: find
                .byWidgetPredicate(
                  (widget) =>
                      widget is Scrollable &&
                      widget.axisDirection == AxisDirection.down,
                )
                .first,
          );
          expect(find.text('clave-sintetica-solo-prueba'), findsOneWidget);
          expect(find.text('Ver mis reportes'), findsNothing);
        } else {
          expect(find.text('Copiar clave privada'), findsNothing);
          await tester.tap(find.text('Ver mis reportes'));
          await tester.pumpAndSettle();
          expect(
            find.text('Encontrado'),
            findsOneWidget,
            reason: find
                .byType(Text)
                .evaluate()
                .map((element) => (element.widget as Text).data)
                .join(' | '),
          );
          await tester.tap(find.text('Encontrado'));
          await tester.pumpAndSettle();
          expect(find.text('Aceptado por Fundación QA'), findsOneWidget);
          expect(find.text('Caso #8'), findsOneWidget);
          expect(find.text('En proceso'), findsOneWidget);
        }
      },
    );
  }

  test('Malformed rescue data produces a recoverable error', () async {
    final client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((_) async => http.Response('{}', 200)),
    );
    final session = Session(client);
    addTearDown(client.close);
    addTearDown(session.dispose);
    final api = RescueApi(client, session);
    await expectLater(api.options(), throwsA(isA<ApiException>()));
    await expectLater(api.publicReportPage(), throwsA(isA<ApiException>()));
  });
}
