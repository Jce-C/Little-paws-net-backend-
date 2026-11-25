import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/adoption/adoption_screens.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/main.dart';

http.Response response(Object? value, int status) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

void main() {
  late ApiClient api;
  late Session session;
  late Future<http.Response> Function() create;
  var posts = 0;
  var saved = false;
  var reads = 0;
  bool? navigateToRequests;

  setUp(() async {
    posts = 0;
    saved = false;
    reads = 0;
    navigateToRequests = null;
    api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        switch (request.url.path) {
          case '/api/adopcion/catalogo/':
            return response({
              'next': null,
              'previous': null,
              'species': ['Perro'],
              'results': [
                {'id_mascota': 14, 'nombre': 'Mascota QA', 'especie': 'Perro'},
              ],
            }, 200);
          case '/api/adopcion/mascotas/14/':
            return response({
              'id_mascota': 14,
              'nombre': 'Mascota QA',
              'especie': 'Perro',
              'raza': null,
              'edad_meses': null,
              'edad_estimada': false,
              'tamano': null,
              'sexo': null,
              'organizacion': 'Fundacion QA',
              'ciudad': 'Riohacha',
              'custodia_desde': '2026-11-18T12:00:00Z',
            }, 200);
          case '/api/adopcion/solicitudes/mias/':
            reads++;
            return response({
              'results': saved
                  ? [
                      {
                        'id_solicitud_adopcion': 31,
                        'estado_adopcion__nombre': 'Pendiente',
                        'mascota_id': 14,
                        'mascota__nombre': 'Mascota QA',
                      },
                    ]
                  : [],
              'next_cursor': null,
            }, 200);
          case '/api/seguridad/operaciones/mis-registros/':
            reads++;
            return response({
              'adopciones': saved
                  ? [
                      {
                        'id_solicitud_adopcion': 31,
                        'mascota__nombre': 'Mascota QA',
                        'estado_adopcion__nombre': 'Pendiente',
                      },
                    ]
                  : [],
            }, 200);
          case '/api/auth/token/':
            return response({
              'access': 'test-access',
              'refresh': 'test-refresh',
            }, 200);
          case '/api/auth/perfil/':
            return response({
              'nombre': 'Persona QA',
              'email': 'persona@example.invalid',
            }, 200);
          case '/api/adopcion/solicitudes/':
            posts++;
            expect(request.method, 'POST');
            return create();
          default:
            throw StateError('Unexpected network request');
        }
      }),
    );
    session = Session(api);
    await session.restore();
    await session.login('persona@example.invalid', 'synthetic-test');
  });
  tearDown(() {
    session.dispose();
    api.close();
  });

  Future<void> open(WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        home: Builder(
          builder: (context) => Scaffold(
            body: TextButton(
              child: const Text('Abrir solicitud'),
              onPressed: () async {
                navigateToRequests = await showDialog<bool>(
                  context: context,
                  barrierDismissible: false,
                  builder: (_) => RequestDialog(
                    pet: const Pet(
                      id: 14,
                      name: 'Mascota QA',
                      species: 'Perro',
                    ),
                    api: AdoptionApi(api, session),
                  ),
                );
              },
            ),
          ),
        ),
      ),
    );
    await tester.tap(find.text('Abrir solicitud'));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('adoption-note')),
      'Mi explicación QA',
    );
  }

  for (final kind in ['timeout', 'server-error', 'malformed-success']) {
    testWidgets(
      '$kind offers checking requests without another POST or false success',
      (tester) async {
        create = () async => switch (kind) {
          'timeout' => throw TimeoutException('synthetic'),
          'server-error' => response({}, 500),
          _ => response({'unexpected': true}, 201),
        };
        await open(tester);
        await tester.tap(find.text('Enviar solicitud'));
        await tester.pumpAndSettle();
        expect(posts, 1);
        expect(find.text('Enviar solicitud'), findsNothing);
        expect(
          find.textContaining('No pudimos confirmar si se creó'),
          findsOneWidget,
        );
        expect(
          tester
              .widget<TextField>(find.byKey(const Key('adoption-note')))
              .enabled,
          isFalse,
        );
        expect(find.text('Mi explicación QA'), findsOneWidget);
        await tester.tap(find.text('Ver mis solicitudes'));
        await tester.pumpAndSettle();
        expect(navigateToRequests, isTrue);
        expect(posts, 1);
        expect(find.textContaining('enviada.'), findsNothing);
      },
    );
  }

  testWidgets(
    'Explicit rejection keeps the note editable and permits correction',
    (tester) async {
      create = () async =>
          response({'detalle': 'Revisa los datos de la solicitud.'}, 400);
      await open(tester);
      await tester.tap(find.text('Enviar solicitud'));
      await tester.pumpAndSettle();
      expect(find.text('Ver mis solicitudes'), findsNothing);
      expect(find.text('Revisa los datos de la solicitud.'), findsOneWidget);
      expect(
        tester
            .widget<TextField>(find.byKey(const Key('adoption-note')))
            .enabled,
        isTrue,
      );
      await tester.enterText(
        find.byKey(const Key('adoption-note')),
        'Nota corregida',
      );
      create = () async => response({'id_solicitud_adopcion': 22}, 201);
      await tester.tap(find.text('Enviar solicitud'));
      await tester.pumpAndSettle();
      expect(posts, 2);
      expect(navigateToRequests, isTrue);
      expect(find.text('Solicitud #22 enviada.'), findsOneWidget);
    },
  );

  testWidgets('Two rapid taps submit once while the response is pending', (
    tester,
  ) async {
    final pending = Completer<http.Response>();
    create = () => pending.future;
    await open(tester);
    await tester.tap(find.text('Enviar solicitud'));
    await tester.tap(find.text('Enviar solicitud'));
    await tester.pump();
    expect(posts, 1);
    expect(find.text('Enviando…'), findsOneWidget);
    final cancel = tester.widget<TextButton>(
      find.widgetWithText(TextButton, 'Cancelar'),
    );
    expect(cancel.onPressed, isNull);
    pending.complete(response({'id_solicitud_adopcion': 23}, 201));
    await tester.pumpAndSettle();
    expect(posts, 1);
    expect(navigateToRequests, isTrue);
  });

  testWidgets(
    'Lost creation response leads to the saved request through the real navigation',
    (tester) async {
      create = () async {
        saved = true;
        throw TimeoutException('synthetic lost response');
      };
      await tester.pumpWidget(LittlePawsApp(api: api, showWelcome: false));
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text('Mascota QA'),
        160,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Mascota QA'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Solicitar adopción'));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.byKey(const Key('account-email')),
        'persona@example.invalid',
      );
      await tester.enterText(
        find.byKey(const Key('account-password')),
        'synthetic-test',
      );
      await tester.ensureVisible(find.byKey(const Key('account-submit')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('account-submit')));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Enviar solicitud'));
      await tester.pumpAndSettle();
      expect(posts, 1);
      expect(reads, 0);
      await tester.tap(find.text('Ver mis solicitudes'));
      await tester.pumpAndSettle();
      expect(find.text('Mis solicitudes'), findsOneWidget);
      expect(find.text('Pendiente'), findsOneWidget);
      expect(posts, 1);
      expect(reads, 1);
      expect(find.text('Solicitud #31 enviada.'), findsNothing);
      expect(tester.takeException(), isNull);
    },
  );

  for (final size in [const Size(320, 640), const Size(800, 360)]) {
    testWidgets(
      'Recovery and cancel remain visible with 200 percent text at $size',
      (tester) async {
        tester.view.physicalSize = size;
        tester.view.devicePixelRatio = 1;
        tester.platformDispatcher.textScaleFactorTestValue = 2;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);
        addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
        create = () async => throw TimeoutException('synthetic');
        await open(tester);
        expect(find.text('Enviar solicitud').hitTestable(), findsOneWidget);
        await tester.tap(find.text('Enviar solicitud'));
        await tester.pumpAndSettle();
        expect(find.text('Ver mis solicitudes').hitTestable(), findsOneWidget);
        expect(find.text('Cancelar').hitTestable(), findsOneWidget);
        expect(tester.takeException(), isNull);
        await tester.tap(find.text('Cancelar'));
        await tester.pumpAndSettle();
        expect(navigateToRequests, isNull);
        expect(posts, 1);
      },
    );
  }
}
