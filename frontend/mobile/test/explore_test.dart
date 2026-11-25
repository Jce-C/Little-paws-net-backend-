import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/explore/explore_screens.dart';

http.Response json(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

void main() {
  testWidgets(
    'Organization categories filter existing records without extra requests',
    (tester) async {
      var calls = 0;
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((_) async {
          calls++;
          return json([
            {
              'id': 1,
              'nombre': 'Fundación QA',
              'tipo': 'Fundación',
              'ciudad': 'Ciudad QA',
            },
            {
              'id': 2,
              'nombre': 'Clínica QA',
              'tipo': 'Veterinaria',
              'ciudad': 'Ciudad QA',
            },
          ]);
        }),
      );
      addTearDown(api.close);
      await tester.pumpWidget(
        MaterialApp(
          home: PublicListScreen(
            api: api,
            path: '/api/red/organizaciones/',
            title: 'Nuestra red',
            kind: 'organizations',
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Fundación QA'), findsOneWidget);
      await tester.tap(find.widgetWithText(ChoiceChip, 'Veterinaria'));
      await tester.pumpAndSettle();
      expect(find.text('Fundación QA'), findsNothing);
      expect(find.text('Clínica QA'), findsOneWidget);
      expect(calls, 1);
    },
  );

  for (final order in [false, true]) {
    testWidgets(
      '${order ? 'Order' : 'Contribution'} submits once and never claims payment',
      (tester) async {
        var posts = 0;
        Map<String, dynamic>? sent;
        final pending = Completer<http.Response>();
        final api = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((request) async {
            if (request.url.path == '/api/auth/token/') {
              return json({
                'access': 'synthetic',
                'refresh': 'synthetic-refresh',
              });
            }
            if (request.url.path == '/api/auth/perfil/') {
              return json({
                'nombre': 'Persona QA',
                'email': 'qa@example.invalid',
              });
            }
            if (request.url.path == '/api/fondos/8/datos-aporte/' &&
                request.method == 'GET') {
              return json({
                'organizacion': 'Fundación QA',
                'titular': 'Titular QA',
                'banco': 'Banco de prueba',
                'tipo_cuenta': 'Ahorros',
                'numero_cuenta': '00000000',
                'identificacion_titular': 'QA-0',
                'prueba': true,
              });
            }
            posts++;
            sent = jsonDecode(request.body) as Map<String, dynamic>;
            return pending.future;
          }),
        );
        final session = Session(api);
        addTearDown(() {
          session.dispose();
          api.close();
        });
        await session.restore();
        await session.login('qa@example.invalid', 'synthetic-password');
        await tester.pumpWidget(
          MaterialApp(
            home: order
                ? OrderScreen(
                    row: const {
                      'id_producto': 9,
                      'id_tienda': 4,
                      'nombre': 'Producto QA',
                      'precio': '2000.00',
                      'existencias': 3,
                    },
                    api: api,
                    session: session,
                  )
                : ContributionScreen(
                    row: const {'id_fondo_externo': 8, 'nombre': 'Fondo QA'},
                    api: api,
                    session: session,
                  ),
          ),
        );
        if (order) {
          await tester.tap(find.byTooltip('Aumentar cantidad'));
        } else {
          await tester.enterText(find.byType(TextField), '2500,50');
        }
        final label = order
            ? 'Iniciar pedido sin pago'
            : 'Registrar compromiso';
        await tester.tap(find.text(label));
        await tester.tap(find.text(label));
        await tester.pump();
        expect(posts, 1);
        if (order) {
          expect(sent, {
            'id_tienda': 4,
            'lineas': [
              {'id_producto': 9, 'cantidad': 2},
            ],
          });
          pending.complete(json({'id_pedido': 7, 'cobrado': false}, 201));
        } else {
          expect(sent, {
            'id_fondo_externo': 8,
            'monto_comprometido': '2500.50',
          });
          pending.complete(json({}, 503));
        }
        await tester.pumpAndSettle();
        expect(posts, 1);
        if (order) {
          expect(
            find.text('Pedido #7 iniciado. No se ha cobrado dinero.'),
            findsOneWidget,
          );
        } else {
          expect(
            find.textContaining('Evita repetir el compromiso'),
            findsOneWidget,
          );
          expect(
            tester.widget<FilledButton>(find.byType(FilledButton)).onPressed,
            isNull,
          );
        }
        expect(tester.takeException(), isNull);
      },
    );
  }
}
