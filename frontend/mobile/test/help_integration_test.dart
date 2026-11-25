import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/explore/help_program.dart';
import 'package:little_paws_net/explore/help_management.dart';
import 'package:little_paws_net/explore/explore_screens.dart';

http.Response json(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);
Map<String, Object?> program(String version) => {
  'version': version,
  'publicada': false,
  'actividades': [
    {
      'titulo': 'Paseos acompañados',
      'descripcion': 'Acompaña a un perro con orientación del equipo.',
      'horario': 'Sábados por la mañana',
      'requisitos': 'Inducción de la organización',
    },
  ],
  'canales': [],
};
void main() {
  const directory = String.fromEnvironment('LPN_VISUAL_QA_DIR');
  setUpAll(() async {
    for (final font in {
      'Inter': 'assets/fonts/Inter.ttf',
      'MaterialIcons': 'fonts/MaterialIcons-Regular.otf',
    }.entries) {
      await (FontLoader(font.key)..addFont(rootBundle.load(font.value))).load();
    }
  });
  late ApiClient api;
  late Session session;
  late Future<http.Response> Function(http.Request) respond;
  var reads = 0;
  var writes = 0;
  setUp(() async {
    reads = 0;
    writes = 0;
    api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((r) async {
        if (r.url.path == '/api/auth/token/') {
          return json({'access': 'qa-token', 'refresh': 'qa-refresh'});
        }
        if (r.url.path == '/api/auth/perfil/') {
          return json({'nombre': 'Persona QA', 'email': 'qa@example.invalid'});
        }
        if (r.url.path == '/api/auth/token/revoke/') return json({});
        if (r.method == 'GET') {
          reads++;
        } else {
          writes++;
        }
        return respond(r);
      }),
    );
    session = Session(api);
    await session.restore();
    await session.login('qa@example.invalid', 'synthetic', remember: false);
  });
  tearDown(() {
    session.dispose();
    api.close();
  });
  Future<void> open(
    WidgetTester tester,
    Widget child, {
    bool large = false,
  }) async {
    tester.view.physicalSize = large
        ? const Size(320, 640)
        : const Size(393, 852);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      RepaintBoundary(
        key: const Key('help-capture'),
        child: MaterialApp(
          theme: lpnTheme(),
          locale: const Locale('es'),
          supportedLocales: const [Locale('es')],
          localizationsDelegates: GlobalMaterialLocalizations.delegates,
          debugShowCheckedModeBanner: false,
          builder: (context, child) => MediaQuery(
            data: MediaQuery.of(context)
                .copyWith(textScaler: TextScaler.linear(large ? 2 : 1)),
            child: child!,
          ),
          home: child,
        ),
      ),
    );
    await tester.pumpAndSettle();
  }

  Future<void> capture(WidgetTester tester, String name) async {
    if (directory.isEmpty) return;
    await tester.pumpAndSettle();
    await expectLater(
      find.byKey(const Key('help-capture')),
      matchesGoldenFile('$directory/$name.png'),
    );
  }

  testWidgets(
    'Program conflict reloads fresh version without duplicate fields and can save again',
    (tester) async {
      var version = 'v1';
      respond = (r) async {
        if (r.method == 'GET') return json(program(version));
        final body = jsonDecode(r.body) as Map;
        if (writes == 1) {
          version = 'v2';
          return json({
            'detalle': 'Otra persona actualizó la convocatoria.',
          }, 409);
        }
        expect(body['version'], 'v2');
        return json({...body, 'version': 'v3'});
      };
      await open(tester, HelpProgramEditor(api: api, session: session, id: 1));
      await capture(tester, '01-convocatoria');
      await tester.enterText(
        find.byType(TextFormField).first,
        'Borrador local',
      );
      await tester.pump();
      await tester.tap(find.text('Guardar convocatoria'));
      await tester.pumpAndSettle();
      expect(writes, 1);
      expect(find.text('No se confirmó el guardado'), findsOneWidget);
      await tester.tap(find.text('Entendido'));
      await tester.pumpAndSettle();
      expect(
        tester
            .widget<FilledButton>(
              find.widgetWithText(FilledButton, 'Guardar convocatoria'),
            )
            .onPressed,
        isNull,
      );
      await tester.tap(find.text('Consultar servidor'));
      await tester.pumpAndSettle();
      await tester.tap(find.widgetWithText(FilledButton, 'Consultar servidor'));
      await tester.pumpAndSettle();
      expect(reads, 2);
      expect(find.byType(TextFormField), findsNWidgets(4));
      expect(find.text('Borrador local'), findsNothing);
      await tester.enterText(find.byType(TextFormField).first, 'Nueva versión');
      await tester.pump();
      await tester.tap(find.text('Guardar convocatoria'));
      await tester.pumpAndSettle();
      expect(writes, 2);
      expect(find.text('Convocatoria guardada sin publicar.'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Management refresh receives new offers and same-account reauthentication clears draft',
    (tester) async {
      respond = (r) async => json({
        'id': 1,
        'nombre': 'Red de cuidado QA',
        'version': 'v1',
        'acepta_voluntarios': true,
        'necesidades_ayuda': 'Alimentos sellados',
        'ofrecimientos': reads == 1
            ? []
            : [
                {
                  'id': 1,
                  'nombre': 'Persona colaboradora',
                  'modalidad': 'voluntariado',
                  'actividad': 'Paseos acompañados',
                  'mensaje': 'Puedo ayudar los sábados.',
                  'fecha': '2026-11-24T12:00:00Z',
                },
              ],
      });
      await open(
        tester,
        OrganizationHelpScreen(api: api, session: session, id: 1),
      );
      expect(
        find.text('Todavía no hay ofrecimientos registrados.'),
        findsOneWidget,
      );
      await tester.tap(find.byTooltip('Actualizar convocatoria'));
      await tester.pumpAndSettle();
      expect(reads, 2);
      expect(find.text('Paseos acompañados'), findsOneWidget);
      await capture(tester, '02-gestion');
      await tester.enterText(find.byType(TextField), 'Borrador privado');
      await session.login('qa@example.invalid', 'synthetic', remember: false);
      await tester.pumpAndSettle();
      expect(find.text('Borrador privado'), findsNothing);
      expect(reads, 3);
      expect(writes, 0);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets('My offers preserve activity and date with shared hierarchy', (
    tester,
  ) async {
    respond = (r) async => json([
      {
        'id': 1,
        'organizacion': 'Red de cuidado QA',
        'modalidad': 'voluntariado',
        'actividad': 'Paseos acompañados',
        'mensaje': 'Puedo ayudar los sábados.',
        'fecha': '2026-11-24T12:00:00Z',
      },
    ]);
    await open(
      tester,
      PublicListScreen(
        api: api,
        session: session,
        path: '/api/ayudas/intereses/',
        title: 'Mis ofrecimientos',
        kind: 'offers',
      ),
    );
    expect(find.text('Paseos acompañados'), findsOneWidget);
    expect(find.textContaining('nov'), findsOneWidget);
    await capture(tester, '03-mis-ofrecimientos');
    await session.login('qa@example.invalid', 'synthetic', remember: false);
    await tester.pumpAndSettle();
    expect(reads, 2);
    expect(writes, 0);
    expect(tester.takeException(), isNull);
  });
  testWidgets(
    'Monetary commitment keeps actions reachable and asks before discarding at 200 percent',
    (tester) async {
      respond = (r) async => json({'detalle': 'No disponible'}, 404);
      await open(
        tester,
        ContributionScreen(
          api: api,
          session: session,
          row: const {'id_fondo_externo': 1, 'nombre': 'Fondo QA'},
        ),
        large: true,
      );
      final field = find.byType(TextField);
      await tester.scrollUntilVisible(field, 180);
      await tester.enterText(field, '10000');
      await tester.pumpAndSettle();
      expect(find.text('Registrar compromiso').hitTestable(), findsOneWidget);
      await tester.tap(find.text('Cancelar'));
      await tester.pumpAndSettle();
      expect(find.text('¿Salir del compromiso?'), findsOneWidget);
      await tester.tap(find.text('Seguir aquí'));
      await tester.pumpAndSettle();
      expect(tester.widget<TextField>(field).controller!.text, '10000');
      expect(writes, 0);
      expect(tester.takeException(), isNull);
    },
  );
}
