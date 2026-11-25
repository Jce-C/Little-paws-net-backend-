import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/design/lpn_navigation.dart';
import 'package:little_paws_net/rescue/rescue_api.dart';
import 'package:little_paws_net/rescue/rescue_screens.dart';

void main() {
  late ApiClient api;
  late Session session;
  var reads = 0;
  var failed = false;
  setUp(() async {
    reads = 0;
    failed = false;
    api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        expect(request.method, 'GET');
        expect(request.url.path, '/api/reportes/publicos/');
        reads++;
        final query = (request.url.queryParameters['buscar'] ?? '')
            .toLowerCase();
        final rows =
            [
                  {
                    'id_reporte': 1,
                    'tipo_reporte__nombre': 'Rescate',
                    'estado_reporte__nombre': 'Pendiente',
                    'descripcion': 'Animal que necesita ayuda en Bogotá',
                  },
                  {
                    'id_reporte': 2,
                    'tipo_reporte__nombre': 'Encontrado',
                    'estado_reporte__nombre': 'Publicado',
                    'descripcion': 'Animal encontrado',
                  },
                ]
                .where(
                  (row) => row.values
                      .join(' ')
                      .toLowerCase()
                      .replaceAll('á', 'a')
                      .contains(query.toLowerCase().replaceAll('á', 'a')),
                )
                .toList();
        return http.Response(
          jsonEncode(failed ? {} : {'results': rows, 'next_cursor': null}),
          failed ? 503 : 200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      }),
    );
    session = Session(api);
    await session.restore();
  });
  tearDown(() {
    session.dispose();
    api.close();
  });
  Future<void> open(WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        home: Scaffold(
          appBar: AppBar(title: const Text('LITTLE PAWS NET')),
          bottomNavigationBar: LpnNavigation(
            selected: 0,
            onSelected: (_) {},
            onPrimary: () {},
          ),
          body: RescueScreen(api: RescueApi(api, session)),
        ),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets(
    'Search is integrated into the photo and report action is initially reachable',
    (tester) async {
      tester.view.physicalSize = const Size(393, 852);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await open(tester);
      final art = tester.getRect(find.byKey(const Key('rescue-hero')));
      final search = tester.getRect(find.byKey(const Key('rescue-search')));
      expect(art.contains(search.topLeft), isTrue);
      expect(search.bottom, lessThanOrEqualTo(art.bottom));
      expect(search.height, greaterThanOrEqualTo(48));
      expect(
        tester.getSemantics(find.byKey(const Key('rescue-search'))).label,
        contains('Buscar reportes'),
      );
      expect(
        find.byTooltip('Reportar un animal').hitTestable(),
        findsOneWidget,
      );
      expect(reads, 1);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets('Description search reaches the server after the debounce', (
    tester,
  ) async {
    await open(tester);
    await tester.enterText(find.byKey(const Key('rescue-search')), 'BOGOTA');
    await tester.pumpAndSettle();
    tester.testTextInput.hide();
    await tester.pumpAndSettle();
    expect(
      tester.getSemantics(find.byKey(const Key('rescue-search'))).label,
      contains('Buscar reportes'),
    );
    final input = tester.getSemantics(find.byType(EditableText));
    expect(input.getSemanticsData().flagsCollection.isTextField, isTrue);
    expect(input.label, 'Buscar reportes');
    await tester.drag(find.byType(ListView).first, const Offset(0, -300));
    await tester.pumpAndSettle();
    expect(find.text('Rescate'), findsOneWidget);
    expect(find.text('Encontrado'), findsNothing);
    expect(reads, 2);
    await tester.scrollUntilVisible(
      find.text('Rescate'),
      120,
      scrollable: find
          .byWidgetPredicate(
            (widget) =>
                widget is Scrollable &&
                widget.axisDirection == AxisDirection.down,
          )
          .first,
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Rescate'));
    await tester.pumpAndSettle();
    expect(find.text('Animal que necesita ayuda en Bogotá'), findsOneWidget);
    expect(reads, 2);
  });
  testWidgets('Clearing a search reloads the first public page', (
    tester,
  ) async {
    await open(tester);
    await tester.enterText(find.byKey(const Key('rescue-search')), 'no existe');
    await tester.pumpAndSettle();
    await tester.drag(find.byType(ListView).first, const Offset(0, -250));
    await tester.pumpAndSettle();
    expect(
      find.text('No hay reportes que coincidan con la búsqueda.'),
      findsOneWidget,
    );
    await tester.tap(find.byTooltip('Limpiar búsqueda'));
    await tester.pumpAndSettle();
    await tester.drag(find.byType(ListView).first, const Offset(0, -300));
    await tester.pumpAndSettle();
    expect(find.text('Rescate'), findsOneWidget);
    expect(find.text('Encontrado'), findsOneWidget);
    expect(reads, 3);
  });
  for (final size in [const Size(320, 640), const Size(800, 360)]) {
    testWidgets(
      'Rescue actions remain reachable with 200 percent text at $size',
      (tester) async {
        tester.view.physicalSize = size;
        tester.view.devicePixelRatio = 1;
        tester.platformDispatcher.textScaleFactorTestValue = 2;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);
        addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
        await open(tester);
        expect(tester.takeException(), isNull);
        for (final label in [
          'Reportar un animal',
          'Mis reportes',
          'Gestionar reporte anónimo',
        ]) {
          await tester.scrollUntilVisible(
            find.byTooltip(label),
            120,
            scrollable: find
                .byWidgetPredicate(
                  (widget) =>
                      widget is Scrollable &&
                      widget.axisDirection == AxisDirection.down,
                )
                .first,
          );
          await tester.pumpAndSettle();
          expect(find.byTooltip(label).hitTestable(), findsOneWidget);
          expect(tester.takeException(), isNull);
        }
        expect(reads, 1);
      },
    );
  }
  testWidgets('Failed feed keeps an explicit retry reachable', (tester) async {
    failed = true;
    await open(tester);
    await tester.scrollUntilVisible(
      find.text('Reintentar'),
      120,
      scrollable: find
          .byWidgetPredicate(
            (widget) =>
                widget is Scrollable &&
                widget.axisDirection == AxisDirection.down,
          )
          .first,
    );
    await tester.pumpAndSettle();
    failed = false;
    await tester.tap(find.text('Reintentar'));
    await tester.pumpAndSettle();
    expect(reads, 2);
    await tester.drag(find.byType(ListView).first, const Offset(0, -300));
    await tester.pumpAndSettle();
    expect(find.text('Rescate'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
  testWidgets('Two-column cards and circular action open real report history', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(393, 852);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await open(tester);
    await tester.drag(find.byType(ListView).first, const Offset(0, -300));
    await tester.pumpAndSettle();
    final first = tester.getRect(find.text('Rescate'));
    final second = tester.getRect(find.text('Encontrado'));
    expect(second.left, greaterThan(first.right));
    expect((second.top - first.top).abs(), lessThan(2));
    final stories = find.byTooltip('Historias de rescate');
    await tester.scrollUntilVisible(
      stories,
      120,
      scrollable: find
          .byWidgetPredicate(
            (widget) =>
                widget is Scrollable &&
                widget.axisDirection == AxisDirection.down,
          )
          .first,
    );
    await tester.pumpAndSettle();
    await tester.tap(stories);
    await tester.pumpAndSettle();
    expect(find.text('Historias de rescate'), findsOneWidget);
    expect(find.byType(ReportTile), findsNWidgets(2));
    expect(reads, 1);
    expect(tester.takeException(), isNull);
  });
  testWidgets(
    'Adoption category activates its destination without another feed request',
    (tester) async {
      var opened = 0;
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Scaffold(
            body: RescueScreen(
              api: RescueApi(api, session),
              onAdopt: () => opened++,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      final adopt = find.text('Adopta ya');
      await tester.scrollUntilVisible(
        adopt,
        100,
        scrollable: find
            .byWidgetPredicate(
              (widget) =>
                  widget is Scrollable &&
                  widget.axisDirection == AxisDirection.down,
            )
            .first,
      );
      await tester.pumpAndSettle();
      await tester.tap(adopt);
      await tester.pumpAndSettle();
      expect(opened, 1);
      expect(reads, 1);
      expect(tester.takeException(), isNull);
    },
  );
}
