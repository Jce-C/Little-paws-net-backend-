import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/auth/public_avatar.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/explore/help_program.dart';
import 'package:little_paws_net/explore/help_management.dart';
import 'package:little_paws_net/explore/explore_screens.dart';
import 'package:little_paws_net/rescue/rescue_api.dart';
import 'package:little_paws_net/rescue/rescue_screens.dart';
import 'package:little_paws_net/rescue/sponsorship_screen.dart';

void main() {
  late ApiClient api;
  late Session session;
  var writes = 0;
  setUpAll(() async {
    for (final font in {
      'Inter': 'assets/fonts/Inter.ttf',
      'MaterialIcons': 'fonts/MaterialIcons-Regular.otf',
    }.entries) {
      await (FontLoader(font.key)..addFont(rootBundle.load(font.value))).load();
    }
  });
  setUp(() async {
    writes = 0;
    api = ApiClient(
      base: Uri.parse('https://qa.example.invalid'),
      client: MockClient((r) async {
        Object data;
        switch (r.url.path) {
          case '/api/auth/token/':
            data = {'access': 'synthetic', 'refresh': 'synthetic-refresh'};
          case '/api/auth/perfil/':
            data = {'email': 'qa@example.invalid', 'nombre': 'Persona QA'};
          case '/api/auth/foto-publica/':
            data = {'foto_publica': null};
          case '/api/ayudas/organizaciones/1/':
            data = {
              'id': 1,
              'nombre': 'Red QA',
              'version': 'v1',
              'acepta_voluntarios': true,
              'necesidades_ayuda': 'Insumos',
              'ofrecimientos': [],
            };
          case '/api/ayudas/organizaciones/1/programa/':
            data = {
              'version': 'v1',
              'publicada': false,
              'actividades': [
                {
                  'titulo': 'Paseos',
                  'descripcion': 'Acompañar animales',
                  'horario': 'Sábados',
                  'requisitos': 'Inducción',
                },
              ],
              'canales': [],
            };
          default:
            throw StateError('Unexpected synthetic route: ${r.url.path}');
        }
        if (r.method != 'GET' && r.url.path != '/api/auth/token/') writes++;
        return http.Response(
          jsonEncode(data),
          200,
          headers: {'content-type': 'application/json'},
        );
      }),
    );
    session = Session(api);
    await session.restore();
    await session.login(
      'qa@example.invalid',
      'synthetic-password',
      remember: false,
    );
  });
  tearDown(() {
    session.dispose();
    api.close();
  });
  const product = {
    'id_producto': 1,
    'id_tienda': 1,
    'nombre': 'Producto QA',
    'precio': '2000.00',
    'existencias': 3,
  };
  Widget screen(String name) => switch (name) {
    'convocatoria' => HelpProgramEditor(api: api, session: session, id: 1),
    'organización' => OrganizationHelpScreen(api: api, session: session, id: 1),
    'producto' => ProductScreen(api: api, session: session, row: product),
    'pedido' => OrderScreen(api: api, session: session, row: product),
    'aporte' => ContributionScreen(
      api: api,
      session: session,
      row: const {'id_fondo_externo': 1, 'nombre': 'Fondo QA'},
    ),
    'avatar' => AvatarScreen(session: session),
    'apadrinamiento' => SponsorshipScreen(session: session, reportId: 1),
    _ => ReportDetailScreen(
      api: RescueApi(api, session),
      report: const AnimalReport(
        id: 1,
        type: 'Rescate',
        status: 'aceptado',
        description: 'Animal atendido por el equipo',
        rescueCase: RescueCase(1, 'activo', 'Red QA'),
      ),
    ),
  };
  const names = [
    'convocatoria',
    'organización',
    'producto',
    'pedido',
    'aporte',
    'avatar',
    'apadrinamiento',
    'reporte',
  ];
  Widget app(Widget child, double scale) => MaterialApp(
    theme: lpnTheme(),
    locale: const Locale('es'),
    supportedLocales: const [Locale('es')],
    localizationsDelegates: GlobalMaterialLocalizations.delegates,
    builder: (context, child) => MediaQuery(
      data: MediaQuery.of(context)
          .copyWith(textScaler: TextScaler.linear(scale)),
      child: child!,
    ),
    home: child,
  );
  for (final name in names) {
    for (final view in [
      (size: const Size(320, 640), scale: 2.0, inset: 200.0),
      (size: const Size(800, 360), scale: 1.0, inset: 120.0),
      (size: const Size(800, 1280), scale: 2.0, inset: 320.0),
    ]) {
      testWidgets('$name actions fit with enlarged text / insets: $view', (
        tester,
      ) async {
        tester.view.devicePixelRatio = 1;
        tester.view.physicalSize = view.size;
        addTearDown(tester.view.resetDevicePixelRatio);
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetViewInsets);
        await tester.pumpWidget(app(screen(name), view.scale));
        await tester.pumpAndSettle();
        tester.view.viewInsets = FakeViewPadding(bottom: view.inset);
        await tester.pumpAndSettle();
        final scaffold = tester.widget<Scaffold>(find.byType(Scaffold).first);
        expect(scaffold.bottomNavigationBar, isNotNull);
        final actions = find.descendant(
          of: find.byWidget(scaffold.bottomNavigationBar!),
          matching: find.bySubtype<ButtonStyleButton>(),
        );
        expect(actions.evaluate(), isNotEmpty);
        for (final element in actions.evaluate()) {
          final rect = tester.getRect(find.byWidget(element.widget));
          expect(rect.top, greaterThanOrEqualTo(0));
          expect(rect.bottom, lessThanOrEqualTo(view.size.height - view.inset));
          expect(rect.width, lessThanOrEqualTo(view.size.width));
        }
        expect(tester.takeException(), isNull);
        expect(writes, 0);
      });
    }
    testWidgets('$name exposed actions have names and usable touch targets', (
      tester,
    ) async {
      tester.view.devicePixelRatio = 1;
      tester.view.physicalSize = const Size(393, 852);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.view.resetPhysicalSize);
      final semantics = tester.ensureSemantics();
      try {
        await tester.pumpWidget(app(screen(name), 1));
        await tester.pumpAndSettle();
        await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
        await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
        await expectLater(tester, meetsGuideline(textContrastGuideline));
        expect(tester.takeException(), isNull);
        expect(writes, 0);
      } finally {
        semantics.dispose();
      }
    });
  }
  testWidgets(
    'Order quantity is operable with Tab and Space without submitting',
    (tester) async {
      await tester.pumpWidget(app(screen('pedido'), 1));
      await tester.pumpAndSettle();
      var reached = false;
      for (var i = 0; i < 30; i++) {
        await tester.sendKeyEvent(LogicalKeyboardKey.tab);
        await tester.pumpAndSettle();
        final context = FocusManager.instance.primaryFocus?.context;
        if (context?.findAncestorWidgetOfExactType<IconButton>()?.tooltip ==
            'Aumentar cantidad') {
          reached = true;
          break;
        }
      }
      expect(
        reached,
        isTrue,
        reason: 'Quantity control must be reachable with Tab.',
      );
      await tester.sendKeyEvent(LogicalKeyboardKey.space);
      await tester.pumpAndSettle();
      expect(find.text('Cantidad: 2'), findsOneWidget);
      expect(writes, 0);
    },
  );
  testWidgets(
    'Organization actions appear after loading, before any interaction',
    (tester) async {
      await tester.pumpWidget(app(screen('organización'), 1));
      await tester.pumpAndSettle();
      expect(find.text('Cancelar'), findsOneWidget);
      expect(find.text('Sin cambios pendientes'), findsOneWidget);
      expect(writes, 0);
    },
  );
}
