import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/explore/product_catalog_screen.dart';

Map<String, Object> product(int id) => {
  'id_producto': id,
  'nombre': 'Producto $id',
  'precio': '1000.00',
  'existencias': 3,
  'categoria': 'Alimentos',
  'tienda': 'Tienda QA',
};
http.Response json(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json'},
);
void main() {
  late ApiClient api;
  late Future<http.Response> Function(http.Request) respond;
  late List<Uri> reads;
  setUp(() {
    reads = [];
    api = ApiClient(
      base: Uri.parse('http://127.0.0.1:8016'),
      client: MockClient((r) async {
        expect(r.method, 'GET');
        reads.add(r.url);
        return respond(r);
      }),
    );
  });
  tearDown(() => api.close());
  Future<void> open(WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        home: ProductCatalogScreen(api: api, onOpen: (_) {}),
      ),
    );
    await tester.pumpAndSettle();
  }

  testWidgets(
    'Loads the next page only on demand, preserves rows on failure and retries the same cursor',
    (tester) async {
      var fail = true;
      respond = (r) async {
        if (r.url.queryParameters['despues'] == null) {
          return json({
            'results': [product(1)],
            'next_cursor': '1',
            'categorias': ['Alimentos'],
          });
        }
        if (fail) return json({'detalle': 'Error QA'}, 503);
        return json({
          'results': [product(2)],
          'next_cursor': null,
        });
      };
      await open(tester);
      expect(reads.length, 1);
      await tester.ensureVisible(find.text('Cargar más productos'));
      await tester.tap(find.text('Cargar más productos'));
      await tester.pumpAndSettle();
      expect(find.text('Producto 1'), findsOneWidget);
      expect(find.text('Reintentar'), findsOneWidget);
      expect(reads.length, 2);
      fail = false;
      await tester.tap(find.text('Reintentar'));
      await tester.pumpAndSettle();
      expect(find.text('Producto 1'), findsOneWidget);
      expect(find.text('Producto 2'), findsOneWidget);
      expect(reads.last.queryParameters['despues'], '1');
      expect(find.text('Cargar más productos'), findsNothing);
    },
  );
  testWidgets(
    'Typing does not fetch; search is sent on submit and stale replies are ignored',
    (tester) async {
      final stale = Completer<http.Response>();
      respond = (r) async => r.url.queryParameters['buscar'] == 'viejo'
          ? stale.future
          : json({
              'results': [
                product(r.url.queryParameters.containsKey('buscar') ? 107 : 1),
              ],
              'next_cursor': null,
              'categorias': ['Alimentos'],
            });
      await open(tester);
      await tester.enterText(find.byType(TextField), 'viejo');
      expect(reads.length, 1);
      await tester.testTextInput.receiveAction(TextInputAction.search);
      await tester.pump();
      await tester.enterText(find.byType(TextField), 'nuevo');
      await tester.testTextInput.receiveAction(TextInputAction.search);
      await tester.pumpAndSettle();
      stale.complete(
        json({
          'results': [product(99)],
          'next_cursor': null,
          'categorias': ['Alimentos'],
        }),
      );
      await tester.pumpAndSettle();
      expect(find.text('Producto 107'), findsOneWidget);
      expect(find.text('Producto 99'), findsNothing);
      expect(reads.length, 3);
      expect(reads.last.queryParameters['buscar'], 'nuevo');
    },
  );
  testWidgets(
    'Rejects external or backwards next cursors without requesting them',
    (tester) async {
      respond = (r) async => json({
        'results': [product(1)],
        'next_cursor': 'https://example.invalid/',
        'categorias': ['Alimentos'],
      });
      await open(tester);
      expect(reads.length, 1);
      expect(find.text('Reintentar'), findsOneWidget);
      expect(find.text('Cargar más productos'), findsNothing);
    },
  );
  testWidgets('Legacy list remains usable without extra filter requests', (
    tester,
  ) async {
    respond = (r) async => json([product(1), product(2)]);
    await open(tester);
    await tester.enterText(find.byType(TextField), 'Producto 2');
    await tester.testTextInput.receiveAction(TextInputAction.search);
    await tester.pumpAndSettle();
    expect(reads.length, 1);
    expect(
      find.byWidgetPredicate((w) => w is Text && w.data == 'Producto 2'),
      findsOneWidget,
    );
    expect(find.text('Producto 1'), findsNothing);
  });
  testWidgets('Catalog fits at 320px and 200 percent text', (tester) async {
    tester.view.devicePixelRatio = 1;
    tester.view.physicalSize = const Size(320, 640);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.view.resetPhysicalSize);
    respond = (r) async => json({
      'results': [product(1)],
      'next_cursor': null,
      'categorias': ['Alimentos'],
    });
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        builder: (context, child) => MediaQuery(
          data: MediaQuery.of(context)
              .copyWith(textScaler: TextScaler.linear(2)),
          child: child!,
        ),
        home: ProductCatalogScreen(api: api, onOpen: (_) {}),
      ),
    );
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    expect(reads.length, 1);
  });
}
