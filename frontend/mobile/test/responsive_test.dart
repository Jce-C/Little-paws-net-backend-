import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'support/catalog_client.dart';

import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/main.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/adoption/adoption_screens.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

class _NonlinearTextScaler extends TextScaler {
  const _NonlinearTextScaler();
  @override
  double scale(double fontSize) => fontSize >= 100 ? fontSize : fontSize * 2;
  @override
  double get textScaleFactor => 2;
}

void main() {
  for (final size in [const Size(320, 640), const Size(800, 360)]) {
    testWidgets('Catalog and access support 200% text at $size', (
      tester,
    ) async {
      tester.view.physicalSize = size;
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: catalogClient(
          (request) async => http.Response(
            jsonEncode([
              {
                'id_mascota': 1,
                'nombre': 'Luna de las segundas oportunidades',
                'especie': 'Perro',
                'raza': 'Sin determinar',
              },
            ]),
            200,
          ),
        ),
      );
      await tester.pumpWidget(LittlePawsApp(showWelcome: false, api: api));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
      await tester.drag(find.byType(CustomScrollView), const Offset(0, -450));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
      await tester.tap(find.text('Mi cuenta'));
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text('Iniciar sesión'),
        120,
        scrollable: find
            .byWidgetPredicate(
              (widget) =>
                  widget is Scrollable &&
                  widget.axisDirection == AxisDirection.down,
            )
            .last,
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Iniciar sesión'));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
      await tester.scrollUntilVisible(
        find.byKey(const Key('account-submit')),
        180,
        scrollable: find
            .byWidgetPredicate(
              (widget) =>
                  widget is Scrollable &&
                  widget.axisDirection == AxisDirection.down,
            )
            .last,
      );
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('account-submit')), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  }
  testWidgets(
    'Large-text catalog uses one column and preserves two-line names',
    (tester) async {
      tester.view.physicalSize = const Size(390, 844);
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: catalogClient(
          (_) async => http.Response(
            jsonEncode([
              {
                'id_mascota': 1,
                'nombre': 'Luna de las segundas oportunidades',
                'especie': 'Perro',
                'raza': 'Sin determinar',
              },
              {
                'id_mascota': 2,
                'nombre': 'Sol',
                'especie': 'Gato',
                'raza': 'Sin determinar',
              },
            ]),
            200,
          ),
        ),
      );
      await tester.pumpWidget(LittlePawsApp(showWelcome: false, api: api));
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text('Luna de las segundas oportunidades'),
        180,
        scrollable: find.byWidgetPredicate(
          (widget) =>
              widget is Scrollable &&
              widget.axisDirection == AxisDirection.down,
        ),
      );
      await tester.pumpAndSettle();
      final grid = tester.widget<SliverGrid>(find.byType(SliverGrid));
      final delegate =
          grid.gridDelegate as SliverGridDelegateWithFixedCrossAxisCount;
      expect(delegate.crossAxisCount, 1);
      expect(
        tester
            .widget<Text>(find.text('Luna de las segundas oportunidades'))
            .maxLines,
        2,
      );
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets('Nonlinear Android text scaling keeps catalog readable', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: catalogClient(
        (_) async => http.Response(
          jsonEncode([
            {
              'id_mascota': 1,
              'nombre': 'Luna de las segundas oportunidades',
              'especie': 'Perro',
              'raza': 'Sin determinar',
            },
          ]),
          200,
        ),
      ),
    );
    final session = Session(api);
    addTearDown(session.dispose);
    addTearDown(api.close);
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        home: MediaQuery(
          data: const MediaQueryData(
            size: Size(390, 844),
            textScaler: _NonlinearTextScaler(),
          ),
          child: Scaffold(
            body: CatalogScreen(
              api: AdoptionApi(api, session),
              session: session,
              onRequested: () {},
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('Luna de las segundas oportunidades'),
      120,
      scrollable: find.byWidgetPredicate(
        (widget) =>
            widget is Scrollable && widget.axisDirection == AxisDirection.down,
      ),
    );
    await tester.pumpAndSettle();
    final grid = tester.widget<SliverGrid>(find.byType(SliverGrid));
    expect(
      (grid.gridDelegate as SliverGridDelegateWithFixedCrossAxisCount)
          .crossAxisCount,
      1,
    );
    expect(tester.takeException(), isNull);
  });
}
