import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/adoption/questionnaire_screen.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

http.Response json(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

void main() {
  late ApiClient api;
  late Session session;
  late Future<http.Response> Function() response;
  var posts = 0;
  Map<String, dynamic>? submitted;
  bool? returned;
  const visualDirectory = String.fromEnvironment('LPN_VISUAL_QA_DIR');
  setUpAll(() async {
    for (final entry in {
      'Inter': 'assets/fonts/Inter.ttf',
      'MaterialIcons': 'fonts/MaterialIcons-Regular.otf',
    }.entries) {
      await (FontLoader(
        entry.key,
      )..addFont(rootBundle.load(entry.value))).load();
    }
  });
  setUp(() async {
    posts = 0;
    submitted = null;
    returned = null;
    response = () async => json({'id_solicitud_adopcion': 76}, 201);
    api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        switch (request.url.path) {
          case '/api/auth/token/':
            return json({'access': 'qa', 'refresh': 'qa-refresh'});
          case '/api/auth/token/revoke/':
            return json({});
          case '/api/auth/perfil/':
            return json({
              'nombre': 'Persona QA',
              'email': 'qa@example.invalid',
              'telefono': '0000000',
              'evaluacion_adopcion': true,
            });
          case '/api/adopcion/solicitudes/evaluacion/':
            posts++;
            submitted = jsonDecode(request.body) as Map<String, dynamic>;
            expect(request.headers['authorization'], 'Bearer qa');
            return response();
          default:
            throw StateError('Petición inesperada: ${request.url.path}');
        }
      }),
    );
    session = Session(api);
    await session.restore();
    await session.login('qa@example.invalid', 'synthetic');
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
              child: const Text('Abrir evaluación'),
              onPressed: () async {
                returned = await Navigator.of(context).push<bool>(
                  MaterialPageRoute(
                    builder: (_) => RepaintBoundary(
                      key: const Key('evaluation-visual'),
                      child: AdoptionQuestionnaireScreen(
                        pet: const Pet(
                          id: 14,
                          name: 'Luna QA',
                          species: 'Perro',
                        ),
                        api: AdoptionApi(api, session),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ),
      ),
    );
    await tester.tap(find.text('Abrir evaluación'));
    await tester.pumpAndSettle();
  }

  Future<void> visible(WidgetTester tester, Finder finder) async {
    if (finder.evaluate().isEmpty) {
      await tester.scrollUntilVisible(
        finder,
        200,
        scrollable: find.byType(Scrollable).first,
      );
    }
    await tester.ensureVisible(finder);
    await tester.pumpAndSettle();
  }

  Future<void> text(WidgetTester tester, String id, String value) async {
    final field = find.byKey(ValueKey('evaluation-$id'));
    await visible(tester, field);
    await tester.enterText(field, value);
    tester.testTextInput.hide();
    await tester.pumpAndSettle();
  }

  Future<void> choose(WidgetTester tester, String id, String label) async {
    final field = find.byKey(ValueKey('evaluation-$id'));
    await visible(tester, field);
    final option = find.descendant(
      of: field,
      matching: find.widgetWithText(OutlinedButton, label),
    );
    if (option.evaluate().isNotEmpty) {
      await visible(tester, option);
      await tester.tap(option);
    } else {
      await tester.tap(field);
      await tester.pumpAndSettle();
      await tester.tap(find.text(label).last);
    }
    await tester.pumpAndSettle();
  }

  Future<void> next(WidgetTester tester) async {
    await tester.tap(find.byKey(const Key('evaluation-next')));
    await tester.pumpAndSettle();
  }

  Future<void> capture(WidgetTester tester, String name) async {
    if (visualDirectory.isEmpty) return;
    tester
        .state<ScrollableState>(find.byType(Scrollable).first)
        .position
        .jumpTo(0);
    await tester.pumpAndSettle();
    await expectLater(
      find.byKey(const Key('evaluation-visual')),
      matchesGoldenFile(Uri.file('$visualDirectory/$name.png')),
    );
  }

  Future<void> fill(WidgetTester tester, {bool snapshots = false}) async {
    await text(tester, 'documento', 'QA-000');
    await text(tester, 'direccion', 'Dirección ficticia');
    if (snapshots) await capture(tester, '01-contacto');
    await next(tester);
    await choose(tester, 'vivienda', 'Casa');
    await choose(tester, 'tenencia', 'Arrendada');
    expect(
      find.byKey(const ValueKey('evaluation-autorizacion_propietario')),
      findsOneWidget,
    );
    await choose(tester, 'autorizacion_propietario', 'Debo confirmarlo');
    await text(tester, 'seguridad_espacio', 'Ventanas con mallas');
    await text(tester, 'personas_hogar', '2');
    await choose(tester, 'acuerdo_hogar', 'Sí');
    if (snapshots) await capture(tester, '02-hogar');
    await next(tester);
    await choose(tester, 'tiempo_cuidado', 'Tengo tiempo cada día');
    await choose(tester, 'recursos_cuidado', 'Puedo cubrirlas');
    await choose(tester, 'cuidados_especiales', 'Necesito orientación');
    await choose(tester, 'seguimiento', 'Quiero conocer las condiciones');
    if (snapshots) await capture(tester, '03-cuidados');
    await next(tester);
    await choose(tester, 'mascotas_actuales', 'Sí');
    await text(tester, 'cantidad_mascotas', '1');
    await text(tester, 'otras_mascotas', 'Gato adulto');
    await choose(tester, 'esterilizacion', 'Todas');
    await choose(tester, 'mascotas_actuales', 'No');
    expect(
      find.byKey(const ValueKey('evaluation-otras_mascotas')),
      findsNothing,
    );
    await choose(tester, 'experiencia_previa', 'No');
    await text(tester, 'motivo', 'Quiero ofrecer un hogar responsable a Luna.');
    if (snapshots) await capture(tester, '04-experiencia');
    await next(tester);
    if (snapshots) await capture(tester, '05-revision');
    expect(find.text('Revisa tu solicitud'), findsOneWidget);
    expect(posts, 0);
  }

  Future<void> confirm(WidgetTester tester) async {
    for (final id in ['correct', 'consent']) {
      final checkbox = find.byKey(Key('evaluation-$id'));
      await visible(tester, checkbox);
      expect(tester.widget<CheckboxListTile>(checkbox).value, isFalse);
      await tester.tap(
        find.descendant(of: checkbox, matching: find.byType(Checkbox)),
      );
      await tester.pumpAndSettle();
      expect(tester.widget<CheckboxListTile>(checkbox).value, isTrue);
    }
  }

  testWidgets(
    'Five steps preserve answers, validate and send one private structured request',
    (tester) async {
      if (visualDirectory.isNotEmpty) {
        tester.view.physicalSize = const Size(393, 852);
        tester.view.devicePixelRatio = 1;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);
      }
      await open(tester);
      await next(tester);
      expect(find.text('Paso 1 de 5'), findsOneWidget);
      expect(posts, 0);
      await fill(tester, snapshots: true);
      await tester.tap(find.widgetWithText(TextButton, 'Regresar'));
      await tester.pumpAndSettle();
      expect(
        find.text('Quiero ofrecer un hogar responsable a Luna.'),
        findsOneWidget,
      );
      await next(tester);
      await confirm(tester);
      await next(tester);
      expect(returned, isTrue);
      expect(posts, 1);
      expect(submitted!['id_mascota'], 14);
      final answers = submitted!['evaluacion'] as Map;
      expect(answers['nombre'], 'Persona QA');
      expect(answers['autorizacion_propietario'], 'pendiente');
      expect(answers['datos_correctos'], isTrue);
      expect(answers['autoriza_evaluacion'], isTrue);
      expect(answers['version'], evaluationVersion);
      expect(answers.containsKey('otras_mascotas'), isFalse);
      expect(answers.containsKey('cantidad_mascotas'), isFalse);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'Lost response offers verification without resending the questionnaire',
    (tester) async {
      response = () async => json({}, 503);
      await open(tester);
      await fill(tester);
      await confirm(tester);
      await next(tester);
      expect(find.text('Verifica el envío'), findsOneWidget);
      await tester.tap(find.widgetWithText(TextButton, 'Cerrar'));
      await tester.pumpAndSettle();
      expect(find.text('Ver mis solicitudes'), findsOneWidget);
      expect(posts, 1);
      await tester.tap(find.text('Ver mis solicitudes'));
      await tester.pumpAndSettle();
      expect(returned, isTrue);
      expect(posts, 1);
    },
  );

  testWidgets('Cancel confirms discard and never submits the draft', (
    tester,
  ) async {
    await open(tester);
    await text(tester, 'documento', 'Borrador QA');
    await tester.tap(find.text('Cancelar'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Seguir completando'));
    await tester.pumpAndSettle();
    expect(find.text('Borrador QA'), findsOneWidget);
    await tester.tap(find.text('Cancelar'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Descartar'));
    await tester.pumpAndSettle();
    expect(returned, isFalse);
    expect(posts, 0);
  });

  testWidgets(
    'Logout destroys the private draft and relogin starts a fresh form',
    (tester) async {
      await open(tester);
      await text(tester, 'documento', 'BORRADOR-PRIVADO');
      await session.logout();
      await tester.pumpAndSettle();
      expect(find.text('BORRADOR-PRIVADO'), findsNothing);
      await session.login('qa@example.invalid', 'synthetic');
      await tester.pumpAndSettle();
      expect(find.text('BORRADOR-PRIVADO'), findsNothing);
      expect(find.text('Paso 1 de 5'), findsOneWidget);
      expect(posts, 0);
    },
  );

  testWidgets(
    'Late response after logout cannot close or populate a fresh questionnaire',
    (tester) async {
      final pending = Completer<http.Response>();
      response = () => pending.future;
      await open(tester);
      await fill(tester);
      await confirm(tester);
      await tester.tap(find.byKey(const Key('evaluation-next')));
      await tester.pump();
      expect(posts, 1);
      expect(find.text('Enviando…'), findsOneWidget);
      await session.logout();
      await tester.pumpAndSettle();
      await session.login('qa@example.invalid', 'synthetic');
      await tester.pumpAndSettle();
      pending.complete(json({'id_solicitud_adopcion': 76}, 201));
      await tester.pumpAndSettle();
      expect(find.text('Paso 1 de 5'), findsOneWidget);
      expect(find.text('Solicitud #76 enviada.'), findsNothing);
      expect(returned, isNull);
      expect(posts, 1);
    },
  );

  testWidgets('Complete questionnaire works at 320 px and 200 percent text', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(320, 640);
    tester.view.devicePixelRatio = 1;
    tester.platformDispatcher.textScaleFactorTestValue = 2;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    await open(tester);
    await fill(tester);
    await confirm(tester);
    await next(tester);
    expect(returned, isTrue);
    expect(posts, 1);
    expect(tester.takeException(), isNull);
  });

  for (final size in [const Size(320, 640), const Size(800, 360)]) {
    testWidgets('Actions remain reachable with 200 percent text at $size', (
      tester,
    ) async {
      tester.view.physicalSize = size;
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      await open(tester);
      expect(
        find.byKey(const Key('evaluation-next')).hitTestable(),
        findsOneWidget,
      );
      expect(
        find.widgetWithText(TextButton, 'Cancelar').hitTestable(),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    });
  }
  testWidgets('Housing tenure choices fit one row at 393px with full labels', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(393, 852);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await open(tester);
    await text(tester, 'documento', 'QA-000');
    await text(tester, 'direccion', 'Dirección ficticia');
    await next(tester);
    final keys = ['propia', 'arrendada', 'otra']
        .map(
          (value) => find.byKey(ValueKey('evaluation-option-tenencia-$value')),
        )
        .toList();
    await visible(tester, keys.first);
    final top = tester.getTopLeft(keys.first).dy;
    for (final key in keys) {
      expect(tester.getTopLeft(key).dy, closeTo(top, 1));
      expect(tester.getSize(key).height, greaterThanOrEqualTo(48));
    }
    expect(find.text('Otra situación'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
