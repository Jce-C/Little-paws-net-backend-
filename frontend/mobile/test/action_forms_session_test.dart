import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/explore/explore_screens.dart';

http.Response reply(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

void main() {
  for (final order in [true, false]) {
    group(order ? 'Pedido' : 'Compromiso de aporte', () {
      late ApiClient api;
      late Session session;
      var identity = 'ana@example.invalid';
      var writes = 0;
      late Future<http.Response> Function() write;
      final label = order ? 'Iniciar pedido sin pago' : 'Registrar compromiso';
      final confirmation = order
          ? 'Pedido #91 iniciado. No se ha cobrado dinero.'
          : 'Compromiso registrado. No se ha recibido ni cobrado dinero.';
      Object result() => order
          ? {'id_pedido': 91, 'cobrado': false}
          : {'id_donacion': 91, 'dinero_recibido': false};
      setUp(() async {
        identity = 'ana@example.invalid';
        writes = 0;
        write = () async => reply(result(), 201);
        api = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((request) async {
            switch (request.url.path) {
              case '/api/auth/token/':
                identity = (jsonDecode(request.body) as Map)['email'] as String;
                return reply({
                  'access': identity,
                  'refresh': 'synthetic-refresh',
                });
              case '/api/auth/perfil/':
                return reply({'nombre': 'Persona QA', 'email': identity});
              case '/api/auth/token/revoke/':
                return reply({});
              case '/api/pedidos/':
              case '/api/fondos/donaciones/':
                writes++;
                return write();
              default:
                throw StateError('Unexpected synthetic route');
            }
          }),
        );
        session = Session(api);
        await session.restore();
        await session.login(identity, 'synthetic-password');
      });
      tearDown(() {
        session.dispose();
        api.close();
      });
      Future<void> open(WidgetTester tester) async {
        await tester.pumpWidget(
          MaterialApp(
            home: order
                ? OrderScreen(
                    api: api,
                    session: session,
                    row: const {
                      'id_producto': 1,
                      'id_tienda': 1,
                      'nombre': 'Producto QA',
                      'precio': '2000.00',
                      'existencias': 3,
                    },
                  )
                : ContributionScreen(
                    api: api,
                    session: session,
                    row: const {'id_fondo_externo': 1, 'nombre': 'Fondo QA'},
                  ),
          ),
        );
        await tester.pumpAndSettle();
      }

      Future<void> draft(WidgetTester tester) async {
        if (order) {
          await tester.tap(find.byTooltip('Aumentar cantidad'));
        } else {
          await tester.enterText(find.byType(TextField), '2500');
        }
        await tester.pump();
      }

      void expectBlank(WidgetTester tester) {
        if (order) {
          expect(find.text('Cantidad: 1'), findsOneWidget);
        } else {
          expect(
            tester.widget<TextField>(find.byType(TextField)).controller!.text,
            isEmpty,
          );
        }
      }

      testWidgets(
        'logout hides previous confirmation and a new account starts fresh',
        (tester) async {
          await open(tester);
          await draft(tester);
          await tester.tap(find.text(label));
          await tester.pumpAndSettle();
          expect(find.text(confirmation), findsOneWidget);
          await session.logout();
          await tester.pumpAndSettle();
          expect(find.text(confirmation), findsNothing);
          expect(find.text('Iniciar sesión'), findsOneWidget);
          expect(find.text(label), findsNothing);
          await session.login('bea@example.invalid', 'synthetic-password');
          await tester.pumpAndSettle();
          expectBlank(tester);
          expect(writes, 1);
        },
      );
      testWidgets(
        'late submission from another account cannot confirm or refill this form',
        (tester) async {
          final pending = Completer<http.Response>();
          write = () => pending.future;
          await open(tester);
          await draft(tester);
          await tester.tap(find.text(label));
          await tester.pump();
          expect(writes, 1);
          await session.login('bea@example.invalid', 'synthetic-password');
          await tester.pumpAndSettle();
          pending.complete(reply(result(), 201));
          await tester.pumpAndSettle();
          expect(find.text(confirmation), findsNothing);
          expectBlank(tester);
          expect(writes, 1);
          expect(tester.takeException(), isNull);
        },
      );
      testWidgets(
        'profile edits preserve a draft but switching identity clears it without sending',
        (tester) async {
          await open(tester);
          await draft(tester);
          await session.updateProfile(name: 'Nuevo nombre QA');
          await tester.pumpAndSettle();
          if (order) {
            expect(find.text('Cantidad: 2'), findsOneWidget);
          } else {
            expect(
              tester.widget<TextField>(find.byType(TextField)).controller!.text,
              '2500',
            );
          }
          await session.login('bea@example.invalid', 'synthetic-password');
          await tester.pumpAndSettle();
          expectBlank(tester);
          expect(writes, 0);
        },
      );
    });
  }
}
