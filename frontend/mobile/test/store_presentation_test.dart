import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/explore/cop_amount.dart';
import 'package:little_paws_net/explore/explore_screens.dart';

const product = {
  'id_producto': 1,
  'id_tienda': 3,
  'nombre': 'Alimento de ejemplo',
  'descripcion': 'Descripción publicada. ',
  'precio': '35000.50',
  'existencias': 2,
  'categoria': 'Alimentos',
};
http.Response json(Object value) => http.Response(
  jsonEncode(value),
  200,
  headers: {'content-type': 'application/json'},
);
void main() {
  test('COP formatting and quantity totals remain decimal-exact', () {
    expect(CopAmount.parse('35000.50')!.formatted, r'$35.000,50 COP');
    expect(CopAmount.parse('0.1')!.times(3).formatted, r'$0,30 COP');
    expect(CopAmount.parse('35000.00')!.times(2).formatted, r'$70.000 COP');
    for (final value in [
      '-1',
      'NaN',
      '1e4',
      '1.001',
      '123456789012345678901234567890',
      null,
      2.1,
    ]) {
      expect(CopAmount.parse(value), isNull);
    }
  });
  for (final scale in [1.0, 2.0]) {
    testWidgets(
      'Product action stays reachable above long information, scale $scale',
      (tester) async {
        tester.view.physicalSize = const Size(320, 640);
        tester.view.devicePixelRatio = 1;
        tester.platformDispatcher.textScaleFactorTestValue = scale;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);
        addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
        var reads = 0;
        final api = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((_) async {
            reads++;
            return json({});
          }),
        );
        final session = Session(api);
        await tester.pumpWidget(
          MaterialApp(
            theme: lpnTheme(),
            home: ProductScreen(
              row: {...product, 'descripcion': 'Descripción publicada. ' * 80},
              api: api,
              session: session,
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(find.text('Preparar pedido').hitTestable(), findsOneWidget);
        await tester.drag(find.byType(ListView), const Offset(0, -500));
        await tester.pumpAndSettle();
        expect(find.text('Preparar pedido').hitTestable(), findsOneWidget);
        expect(reads, 0);
        expect(tester.takeException(), isNull);
        await tester.pumpWidget(const SizedBox.shrink());
        session.dispose();
        api.close();
      },
    );
  }
  testWidgets('Out-of-stock and malformed prices never enable an order', (
    tester,
  ) async {
    final api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((_) async {
        fail('No request expected');
      }),
    );
    final session = Session(api);
    for (final row in [
      {...product, 'existencias': 0},
      {...product, 'precio': 'NaN'},
    ]) {
      await tester.pumpWidget(
        MaterialApp(
          home: ProductScreen(row: row, api: api, session: session),
        ),
      );
      final action = tester.widget<FilledButton>(
        find.widgetWithText(FilledButton, 'No disponible'),
      );
      expect(action.onPressed, isNull);
      expect(tester.takeException(), isNull);
    }
    await tester.pumpWidget(const SizedBox.shrink());
    session.dispose();
    api.close();
  });
  testWidgets(
    'Receipt shows server-saved total even if catalogue price changed',
    (tester) async {
      var posts = 0;
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((r) async {
          if (r.url.path == '/api/auth/token/') {
            return json({'access': 'access', 'refresh': 'refresh'});
          }
          if (r.url.path == '/api/auth/perfil/') {
            return json({'nombre': 'QA', 'email': 'qa@example.invalid'});
          }
          if (r.url.path == '/api/seguridad/mis-accesos/') {
            return json({
              'roles_globales': ['CIUDADANO'],
              'entidades': [],
            });
          }
          posts++;
          return json({
            'id_pedido': 7,
            'cobrado': false,
            'total_referencial': '80000.00',
          });
        }),
      );
      final session = Session(api);
      await session.restore();
      await session.login('qa@example.invalid', 'qa-password');
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: OrderScreen(row: product, api: api, session: session),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byTooltip('Aumentar cantidad'));
      await tester.pumpAndSettle();
      expect(find.text(r'Total de referencia: $70.001 COP'), findsOneWidget);
      await tester.tap(find.text('Iniciar pedido sin pago'));
      await tester.pumpAndSettle();
      expect(posts, 1);
      expect(
        find.text(r'Total de referencia guardado: $80.000 COP'),
        findsOneWidget,
      );
      expect(
        find.text('Pedido #7 iniciado. No se ha cobrado dinero.'),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox.shrink());
      session.dispose();
      api.close();
    },
  );
}
