import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;

import 'support/catalog_client.dart';

import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/main.dart';
import 'package:little_paws_net/notifications/notifications_api.dart';
import 'package:little_paws_net/notifications/notifications_screen.dart';

http.Response response(Object? value, {int status = 200}) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

Map<String, Object?> notice(String content) => {
  'id_notificacion': 4,
  'contenido': content,
  'fecha_creacion': '2026-11-18T16:00:00Z',
  'fecha_lectura': null,
};

void main() {
  testWidgets('Bell does not fetch private notifications before sign in', (
    tester,
  ) async {
    var calls = 0;
    final client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: catalogClient((request) async {
        calls++;
        expect(request.url.path, '/api/adopcion/catalogo/');
        return response([]);
      }),
    );
    await tester.pumpWidget(LittlePawsApp(showWelcome: false, api: client));
    await tester.pumpAndSettle();
    expect(calls, 1);
    await tester.tap(find.byTooltip('Notificaciones'));
    await tester.pumpAndSettle();
    expect(
      find.text('Inicia sesión para consultar tus notificaciones.'),
      findsOneWidget,
    );
    expect(calls, 1);
  });

  testWidgets(
    'Read failure preserves unread status and successful retry updates it',
    (tester) async {
      var reads = 0;
      var gets = 0;
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: catalogClient((request) async {
          switch (request.url.path) {
            case '/api/auth/token/':
              return response({'access': 'access', 'refresh': 'refresh'});
            case '/api/auth/perfil/':
              return response({
                'nombre': 'Ana',
                'email': 'ana@example.invalid',
              });
            case '/api/notificaciones/':
              gets++;
              return response([notice('Tu solicitud fue revisada.')]);
            case '/api/notificaciones/4/leer/':
              reads++;
              return reads == 1
                  ? response({}, status: 500)
                  : response({'leida': true});
            default:
              throw StateError('Unexpected route');
          }
        }),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await session.restore();
      await session.login('ana@example.invalid', 'test-password');
      await tester.pumpWidget(
        MaterialApp(
          home: NotificationsScreen(api: NotificationsApi(client, session)),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('notification-read-4')));
      await tester.pumpAndSettle();
      expect(find.text('Sin leer'), findsOneWidget);
      expect(
        find.text('El servicio no está disponible en este momento.'),
        findsOneWidget,
      );
      await tester.tap(find.byKey(const Key('notification-read-4')));
      await tester.pumpAndSettle();
      expect(find.text('Leída'), findsOneWidget);
      expect(find.text('0 sin leer en esta lista'), findsOneWidget);
      expect(reads, 2);
      expect(gets, 1);
      await tester.tap(find.text('Solo sin leer'));
      await tester.pumpAndSettle();
      expect(
        find.text('No hay avisos sin leer en esta lista.'),
        findsOneWidget,
      );
    },
  );

  testWidgets(
    'A late inbox response cannot display messages from the previous account',
    (tester) async {
      final old = Completer<http.Response>();
      var email = 'ana@example.invalid';
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: catalogClient((request) async {
          if (request.url.path == '/api/auth/token/') {
            email = (jsonDecode(request.body) as Map)['email'] as String;
            return response({'access': email, 'refresh': 'refresh-$email'});
          }
          if (request.url.path == '/api/auth/perfil/') {
            return response({'nombre': 'Cuenta QA', 'email': email});
          }
          if (request.headers['authorization'] ==
              'Bearer ana@example.invalid') {
            return old.future;
          }
          return response([notice('Aviso de la segunda cuenta')]);
        }),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await session.restore();
      await session.login(email, 'test-password');
      await tester.pumpWidget(
        MaterialApp(
          home: NotificationsScreen(api: NotificationsApi(client, session)),
        ),
      );
      await tester.pump();
      await session.login('carlos@example.invalid', 'test-password');
      await tester.pumpAndSettle();
      old.complete(response([notice('Aviso privado de la primera cuenta')]));
      await tester.pumpAndSettle();
      expect(find.text('Aviso de la segunda cuenta'), findsOneWidget);
      expect(find.text('Aviso privado de la primera cuenta'), findsNothing);
      expect(tester.takeException(), isNull);
    },
  );

  test('Notification parser rejects malformed dates and missing content', () {
    expect(
      () => AccountNotification.fromJson({
        ...notice('Aviso'),
        'fecha_creacion': 'invalid',
      }),
      throwsA(isA<ApiException>()),
    );
    expect(
      () =>
          AccountNotification.fromJson({...notice('Aviso'), 'contenido': null}),
      throwsA(isA<ApiException>()),
    );
  });
}
