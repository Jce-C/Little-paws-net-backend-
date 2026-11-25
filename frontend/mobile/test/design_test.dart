import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'support/catalog_client.dart';

import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/design/lpn_navigation.dart';
import 'package:little_paws_net/adoption/adoption_screens.dart';
import 'package:little_paws_net/main.dart';

void main() {
  late ApiClient api;
  var calls = 0;
  setUp(() {
    FlutterSecureStorage.setMockInitialValues({});
    calls = 0;
    api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: catalogClient((request) async {
        calls++;
        expect(request.url.path, '/api/adopcion/catalogo/');
        return http.Response('[]', 200);
      }),
    );
  });

  testWidgets(
    'Welcome uses brand cream and does not fetch the catalog until exploring',
    (tester) async {
      await tester.pumpWidget(LittlePawsApp(api: api));
      await tester.pumpAndSettle();
      expect(calls, 0);
      expect(
        tester
            .widget<Scaffold>(find.byKey(const Key('welcome-screen')))
            .backgroundColor,
        const Color(0xfff2c778),
      );
      await tester.ensureVisible(find.byKey(const Key('welcome-explore')));
      await tester.tap(find.byKey(const Key('welcome-explore')));
      await tester.pumpAndSettle();
      expect(
        Theme.of(tester.element(find.byType(Home)))
            .extension<LpnMaterials>()!
            .reduceTransparency,
        isFalse,
      );
      expect(calls, 1);
      expect(
        Theme.of(tester.element(find.text('Adoptar').first))
            .scaffoldBackgroundColor,
        const Color(0xfffff8f3),
      );
    },
  );

  testWidgets(
    'Floating bar preserves viewport width, content inset and keyboard access',
    (tester) async {
      tester.view.physicalSize = const Size(393, 852);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.view.resetViewInsets);
      await tester.pumpWidget(LittlePawsApp(showWelcome: false, api: api));
      await tester.pumpAndSettle();
      final rect = tester.getRect(find.byType(LpnNavigation));
      expect(rect.left, 0);
      expect(rect.right, 393);
      expect(tester.getRect(find.byType(CatalogScreen)).bottom, 852);
      expect(
        MediaQuery.paddingOf(tester.element(find.byType(CatalogScreen))).bottom,
        greaterThanOrEqualTo(rect.height),
      );
      tester.view.viewInsets = const FakeViewPadding(bottom: 280);
      await tester.pumpAndSettle();
      expect(find.byType(LpnNavigation), findsNothing);
      tester.view.resetViewInsets();
      await tester.pumpAndSettle();
      expect(find.bySemanticsLabel('Adoptar\nPestaña 2 de 4'), findsOneWidget);
      expect(calls, 1);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'Welcome links directly to login and registration without data requests',
    (tester) async {
      await tester.pumpWidget(LittlePawsApp(api: api));
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.text('Iniciar sesión'));
      await tester.tap(find.text('Iniciar sesión'));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('account-email')), findsOneWidget);
      expect(find.byKey(const Key('account-name')), findsNothing);
      expect(
        Theme.of(tester.element(find.byKey(const Key('account-email'))))
            .scaffoldBackgroundColor,
        const Color(0xfff7db9f),
      );
      await tester.tap(find.byType(BackButton));
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.text('Crear cuenta'));
      await tester.tap(find.text('Crear cuenta'));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('account-name')), findsOneWidget);
      expect(calls, 0);
    },
  );

  testWidgets(
    'Appearance control applies solid surfaces without reloading account or catalog',
    (tester) async {
      await tester.pumpWidget(LittlePawsApp(showWelcome: false, api: api));
      await tester.pumpAndSettle();
      expect(
        Theme.of(tester.element(find.byType(Home)))
            .extension<LpnMaterials>()!
            .reduceTransparency,
        isFalse,
      );
      await tester.tap(find.byTooltip('Apariencia'));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(CheckedPopupMenuItem<String>));
      await tester.pumpAndSettle();
      expect(find.byType(BackdropFilter), findsNothing);
      expect(
        Theme.of(tester.element(find.byType(Home)))
            .extension<LpnMaterials>()!
            .reduceTransparency,
        isTrue,
      );
      expect(calls, 1);
    },
  );

  testWidgets('High contrast uses a solid material automatically', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        builder: (context, child) => MediaQuery(
          data: MediaQuery.of(context).copyWith(highContrast: true),
          child: child!,
        ),
        home: const Scaffold(
          body: GlassSurface(child: Text('Contenido legible')),
        ),
      ),
    );
    expect(find.byType(BackdropFilter), findsNothing);
  });

  testWidgets('A saved transparency preference restores and can be changed', (
    tester,
  ) async {
    FlutterSecureStorage.setMockInitialValues({'lpn_reduce_transparency': '1'});
    await tester.pumpWidget(LittlePawsApp(showWelcome: false, api: api));
    await tester.pumpAndSettle();
    expect(find.byType(BackdropFilter), findsNothing);
    await tester.tap(find.byTooltip('Apariencia'));
    await tester.pumpAndSettle();
    await tester.tap(find.byType(CheckedPopupMenuItem<String>));
    await tester.pumpAndSettle();
    expect(
      Theme.of(tester.element(find.byType(Home)))
          .extension<LpnMaterials>()!
          .reduceTransparency,
      isFalse,
    );
    expect(
      await const FlutterSecureStorage().read(key: 'lpn_reduce_transparency'),
      '0',
    );
  });

  for (final size in [const Size(320, 640), const Size(800, 360)]) {
    testWidgets('Welcome and its actions support 200 percent text at $size', (
      tester,
    ) async {
      tester.view.physicalSize = size;
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      await tester.pumpWidget(LittlePawsApp(api: api));
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.byKey(const Key('welcome-explore')));
      expect(
        find.byKey(const Key('welcome-explore')).hitTestable(),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
      expect(calls, 0);
    });
  }
}
