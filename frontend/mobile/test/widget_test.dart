import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'support/catalog_client.dart';

import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/main.dart';

void main() {
  testWidgets('Sesión revocada ofrece ingresar otra vez y permite continuar', (
    tester,
  ) async {
    var revoked = false;
    var requestCalls = 0;
    var refreshCalls = 0;
    final api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: catalogClient((request) async {
        switch (request.url.path) {
          case '/api/adopcion/catalogo/':
            return http.Response('[]', 200);
          case '/api/auth/token/':
            return http.Response(
              jsonEncode({'access': 'access-qa', 'refresh': 'refresh-qa'}),
              200,
            );
          case '/api/auth/perfil/':
            return http.Response(
              jsonEncode({'nombre': 'Ana', 'email': 'ana@example.invalid'}),
              200,
            );
          case '/api/auth/token/refresh/':
            refreshCalls++;
            return http.Response(
              jsonEncode({'access': 'renewed', 'refresh': 'rotated'}),
              200,
            );
          case '/api/seguridad/operaciones/mis-registros/':
            requestCalls++;
            return revoked
                ? http.Response(jsonEncode({'detail': 'Sesión revocada'}), 401)
                : http.Response(jsonEncode({'adopciones': []}), 200);
          default:
            throw StateError('Unexpected route');
        }
      }),
    );
    await tester.pumpWidget(LittlePawsApp(showWelcome: false, api: api));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Solicitudes'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Iniciar sesión'));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('account-email')),
      'ana@example.invalid',
    );
    await tester.enterText(
      find.byKey(const Key('account-password')),
      'test-password',
    );
    await tester.ensureVisible(find.byKey(const Key('account-submit')));
    await tester.tap(find.byKey(const Key('account-submit')));
    await tester.pumpAndSettle();
    expect(
      find.text('Todavía no has enviado solicitudes de adopción.'),
      findsOneWidget,
    );
    revoked = true;
    final previousCalls = requestCalls;
    await tester.tap(find.byTooltip('Actualizar solicitudes'));
    await tester.pumpAndSettle();
    expect(refreshCalls, 1);
    expect(requestCalls - previousCalls, 2);
    expect(
      find.text('Inicia sesión para consultar tus solicitudes.'),
      findsOneWidget,
    );
    expect(find.byType(CircularProgressIndicator), findsNothing);
    revoked = false;
    await tester.tap(find.text('Iniciar sesión'));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('account-email')),
      'ana@example.invalid',
    );
    await tester.enterText(
      find.byKey(const Key('account-password')),
      'test-password',
    );
    await tester.ensureVisible(find.byKey(const Key('account-submit')));
    await tester.tap(find.byKey(const Key('account-submit')));
    await tester.pumpAndSettle();
    expect(
      find.text('Todavía no has enviado solicitudes de adopción.'),
      findsOneWidget,
    );
  });

  testWidgets('Catálogo vacío ofrece una recarga', (tester) async {
    var requests = 0;
    final client = catalogClient((request) async {
      requests++;
      expect(request.url.path, '/api/adopcion/catalogo/');
      return http.Response('[]', 200);
    });
    await tester.pumpWidget(
      LittlePawsApp(
        showWelcome: false,
        api: ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: client,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('Todavía no hay mascotas disponibles para adopción.'),
      160,
      scrollable: find.byType(Scrollable).first,
    );
    expect(
      find.text('Todavía no hay mascotas disponibles para adopción.'),
      findsOneWidget,
    );
    await tester.ensureVisible(find.text('Actualizar'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Actualizar'));
    await tester.pumpAndSettle();
    expect(requests, 2);
  });

  testWidgets('Envía la solicitud autenticada y muestra la decisión', (
    tester,
  ) async {
    String stage = 'Pendiente';
    var submitted = 0;
    final api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: catalogClient((request) async {
        Object data;
        var status = 200;
        switch (request.url.path) {
          case '/api/adopcion/catalogo/':
            data = [
              {
                'id_mascota': 14,
                'nombre': 'Luna QA',
                'especie': 'Perro',
                'raza': null,
              },
            ];
          case '/api/adopcion/mascotas/14/':
            data = {
              'id_mascota': 14,
              'nombre': 'Luna QA',
              'especie': 'Perro',
              'raza': null,
              'edad_meses': null,
              'edad_estimada': false,
              'tamano': null,
              'sexo': null,
              'organizacion': 'Fundacion QA',
              'ciudad': 'Riohacha',
              'custodia_desde': '2026-11-18T12:00:00Z',
            };
          case '/api/auth/token/':
            expect(
              jsonDecode(request.body)['email'],
              'adoptante@example.invalid',
            );
            data = {'access': 'access-qa', 'refresh': 'refresh-qa'};
          case '/api/auth/perfil/':
            expect(request.headers['authorization'], 'Bearer access-qa');
            data = {
              'nombre': 'Adoptante QA',
              'email': 'adoptante@example.invalid',
            };
          case '/api/adopcion/solicitudes/':
            expect(request.headers['authorization'], 'Bearer access-qa');
            expect(jsonDecode(request.body), {
              'id_mascota': 14,
              'observaciones': 'Soy responsable.',
            });
            submitted++;
            status = 201;
            data = {'id_solicitud_adopcion': 8};
          case '/api/seguridad/operaciones/mis-registros/':
            expect(request.headers['authorization'], 'Bearer access-qa');
            data = {
              'adopciones': [
                {
                  'id_solicitud_adopcion': 8,
                  'mascota__nombre': 'Luna QA',
                  'estado_adopcion__nombre': stage,
                },
              ],
            };
          default:
            fail('Ruta inesperada: ${request.url.path}');
        }
        return http.Response(jsonEncode(data), status);
      }),
    );
    await tester.pumpWidget(LittlePawsApp(showWelcome: false, api: api));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('Luna QA'),
      160,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Luna QA'));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Solicitar adopción'));
    await tester.tap(find.text('Solicitar adopción'));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('account-email')),
      'adoptante@example.invalid',
    );
    await tester.enterText(
      find.byKey(const Key('account-password')),
      'solo-pruebas',
    );
    await tester.ensureVisible(find.byKey(const Key('account-submit')));
    await tester.tap(find.byKey(const Key('account-submit')));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('adoption-note')),
      'Soy responsable.',
    );
    await tester.tap(find.text('Enviar solicitud'));
    await tester.pumpAndSettle();
    expect(submitted, 1);
    expect(find.text('Pendiente'), findsOneWidget);
    stage = 'Aprobada';
    await tester.tap(find.byTooltip('Actualizar solicitudes'));
    await tester.pumpAndSettle();
    expect(find.text('Aprobada'), findsOneWidget);
  });
}
