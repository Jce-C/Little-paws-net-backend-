import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/explore/message_composer.dart';

http.Response reply(Object data, [int status = 200]) => http.Response(
  jsonEncode(data),
  status,
  headers: {'content-type': 'application/json'},
);

void main() {
  for (final public in [true, false]) {
    group(public ? 'Public community draft' : 'Private interest draft', () {
      late ApiClient api;
      late Session session;
      var identity = 'ana@example.invalid';
      var name = 'Persona QA';
      var writes = 0;
      late Future<http.Response> Function() send;
      setUp(() async {
        identity = 'ana@example.invalid';
        name = 'Persona QA';
        writes = 0;
        send = () async => reply({'id': 51}, 201);
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
                if (request.method == 'PATCH') {
                  name = (jsonDecode(request.body) as Map)['nombre'] as String;
                }
                return reply({'email': identity, 'nombre': name});
              case '/api/auth/token/revoke/':
                return reply({});
              case '/api/comunidad/publicaciones/':
              case '/api/ayudas/intereses/':
                writes++;
                return send();
              default:
                throw StateError('Unexpected mock route');
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
            home: Builder(
              builder: (context) => Scaffold(
                body: TextButton(
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute<bool>(
                      builder: (_) => PublicMessageScreen(
                        api: api,
                        session: session,
                        path: public
                            ? '/api/comunidad/publicaciones/'
                            : '/api/ayudas/intereses/',
                        title: 'Redactar mensaje',
                        public: public,
                        extra: public
                            ? const {}
                            : const {'fundacion_id': 1, 'modalidad': 'especie'},
                      ),
                    ),
                  ),
                  child: const Text('Abrir'),
                ),
              ),
            ),
          ),
        );
        await tester.tap(find.text('Abrir'));
        await tester.pumpAndSettle();
      }

      String text(WidgetTester tester) =>
          tester.widget<TextField>(find.byType(TextField)).controller!.text;

      testWidgets(
        'suggestions change only the draft and preserve existing text',
        (tester) async {
          await open(tester);
          final label = public
              ? 'Una historia de rescate'
              : 'Quiero conocer más';
          final suggestion = find.text(label);
          await tester.ensureVisible(suggestion);
          await tester.tap(suggestion);
          await tester.pumpAndSettle();
          expect(text(tester), '$label: ');
          expect(writes, 0);
          await tester.enterText(find.byType(TextField), 'Mi información');
          await tester.ensureVisible(suggestion);
          await tester.tap(suggestion);
          await tester.pumpAndSettle();
          expect(text(tester), 'Mi información\n$label: ');
          expect(writes, 0);
          expect(tester.takeException(), isNull);
        },
      );

      testWidgets(
        'profile edits preserve draft; logout hides it and new identity starts blank',
        (tester) async {
          await open(tester);
          await tester.enterText(
            find.byType(TextField),
            'Borrador privado sintético',
          );
          await session.updateProfile(name: 'Nuevo nombre QA');
          await tester.pumpAndSettle();
          expect(text(tester), 'Borrador privado sintético');
          expect(
            find.text('Envías el mensaje como Nuevo nombre QA'),
            findsOneWidget,
          );
          await session.logout();
          await tester.pumpAndSettle();
          expect(find.byType(TextField), findsNothing);
          expect(find.text('Borrador privado sintético'), findsNothing);
          await session.login('bea@example.invalid', 'synthetic-password');
          await tester.pumpAndSettle();
          expect(text(tester), isEmpty);
          expect(writes, 0);
        },
      );

      testWidgets(
        'late response cannot close another identity composer or replace its draft',
        (tester) async {
          final pending = Completer<http.Response>();
          send = () => pending.future;
          await open(tester);
          await tester.enterText(find.byType(TextField), 'Mensaje anterior');
          await tester.tap(find.text('Enviar'));
          await tester.pump();
          expect(writes, 1);
          await session.login('bea@example.invalid', 'synthetic-password');
          await tester.pumpAndSettle();
          expect(text(tester), isEmpty);
          await tester.enterText(
            find.byType(TextField),
            'Mensaje de la segunda cuenta',
          );
          pending.complete(reply({'id': 51}, 201));
          await tester.pumpAndSettle();
          expect(text(tester), 'Mensaje de la segunda cuenta');
          expect(find.textContaining('No pudimos confirmar'), findsNothing);
          expect(writes, 1);
          expect(tester.takeException(), isNull);
          await tester.pumpWidget(const SizedBox.shrink());
        },
      );

      testWidgets(
        'logout removes the old discard dialog without blocking sign-in',
        (tester) async {
          await open(tester);
          await tester.enterText(find.byType(TextField), 'Borrador anterior');
          await tester.pump();
          await tester.tap(find.byType(BackButton));
          await tester.pumpAndSettle();
          expect(find.byType(AlertDialog), findsOneWidget);
          await session.logout();
          await tester.pumpAndSettle();
          expect(find.byType(AlertDialog), findsNothing);
          expect(find.text('Borrador anterior'), findsNothing);
          await tester.tap(find.text('Iniciar sesión'));
          await tester.pumpAndSettle();
          expect(find.byKey(const Key('account-email')), findsOneWidget);
          expect(writes, 0);
          expect(tester.takeException(), isNull);
        },
      );

      testWidgets(
        'switching account removes only the old dialog and preserves the new composer route',
        (tester) async {
          await open(tester);
          await tester.enterText(find.byType(TextField), 'Borrador anterior');
          await tester.pump();
          await tester.tap(find.byType(BackButton));
          await tester.pumpAndSettle();
          expect(find.byType(AlertDialog), findsOneWidget);
          await session.login('bea@example.invalid', 'synthetic-password');
          await tester.pumpAndSettle();
          expect(find.byType(AlertDialog), findsNothing);
          expect(text(tester), isEmpty);
          await tester.enterText(find.byType(TextField), 'Borrador nuevo');
          await tester.pump();
          await tester.tap(find.byType(BackButton));
          await tester.pumpAndSettle();
          await tester.tap(find.text('Seguir editando'));
          await tester.pumpAndSettle();
          expect(text(tester), 'Borrador nuevo');
          expect(writes, 0);
          expect(tester.takeException(), isNull);
          await tester.pumpWidget(const SizedBox.shrink());
        },
      );

      testWidgets(
        'same-identity profile update keeps the dialog and its cancellation preserves the draft',
        (tester) async {
          await open(tester);
          await tester.enterText(find.byType(TextField), 'Borrador conservado');
          await tester.pump();
          await tester.tap(find.byType(BackButton));
          await tester.pumpAndSettle();
          await session.updateProfile(name: 'Nuevo nombre QA');
          await tester.pumpAndSettle();
          expect(find.byType(AlertDialog), findsOneWidget);
          await tester.tap(find.text('Seguir editando'));
          await tester.pumpAndSettle();
          expect(text(tester), 'Borrador conservado');
          expect(
            find.text('Envías el mensaje como Nuevo nombre QA'),
            findsOneWidget,
          );
          expect(writes, 0);
          expect(tester.takeException(), isNull);
          await tester.pumpWidget(const SizedBox.shrink());
        },
      );

      testWidgets(
        'anonymous entry cannot draft or submit and has a working sign-in action',
        (tester) async {
          await session.logout();
          await open(tester);
          expect(find.byType(TextField), findsNothing);
          expect(find.text('Enviar'), findsNothing);
          await tester.tap(find.text('Iniciar sesión'));
          await tester.pumpAndSettle();
          expect(find.byKey(const Key('account-email')), findsOneWidget);
          expect(writes, 0);
          expect(tester.takeException(), isNull);
        },
      );
    });
  }
}
