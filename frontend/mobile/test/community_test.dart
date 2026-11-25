import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/explore/community_screen.dart';

http.Response json(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

void main() {
  for (final lost in [false, true]) {
    testWidgets(
      'Community ${lost ? 'verifies a lost response without resending' : 'publishes, comments and reacts using server results'}',
      (tester) async {
        final posts = <Map<String, Object?>>[];
        final comments = <Map<String, Object?>>[];
        var submissions = 0;
        var reads = 0;
        var reactions = 0;
        final api = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((request) async {
            final path = request.url.path;
            if (path == '/api/auth/token/') {
              return json({
                'access': 'synthetic',
                'refresh': 'synthetic-refresh',
              });
            }
            if (path == '/api/auth/perfil/') {
              return json({
                'nombre': 'Persona QA',
                'email': 'qa@example.invalid',
              });
            }
            if (path == '/api/comunidad/publicaciones/') {
              if (request.method == 'POST') {
                submissions++;
                final content = (jsonDecode(request.body) as Map)['contenido'];
                posts.add({
                  'id': 1,
                  'contenido': content,
                  'autor': 'Persona QA',
                  'fecha': '2026-11-20T12:00:00Z',
                  'propia': true,
                  'reacciones': 0,
                  'comentarios': 0,
                  'reaccion_propia': false,
                });
                return lost ? json({}, 503) : json({'id': 1}, 201);
              }
              reads++;
              return json({
                'results': posts,
                'antes': null,
                'puede_publicar': true,
              });
            }
            if (path.endsWith('/comentarios/')) {
              if (request.method == 'POST') {
                comments.add({
                  'id': 1,
                  'autor': 'Persona QA',
                  'contenido': (jsonDecode(request.body) as Map)['contenido'],
                  'fecha': '2026-11-20T13:00:00Z',
                  'respuesta_a': null,
                });
                return json({'id': 1}, 201);
              }
              return json({
                'results': comments,
                'despues': null,
                'puede_publicar': true,
              });
            }
            if (path.endsWith('/reaccion/')) {
              reactions++;
              return json({'activa': true, 'total': 1});
            }
            throw StateError('Unexpected mock route');
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
            home: CommunityScreen(api: api, session: session),
          ),
        );
        await tester.pumpAndSettle();
        await tester.tap(find.text('Crear publicación'));
        await tester.pumpAndSettle();
        await tester.enterText(
          find.byType(TextField),
          'Experiencia sintética QA',
        );
        await tester.tap(find.text('Enviar'));
        await tester.pumpAndSettle();
        expect(submissions, 1);
        if (lost) {
          expect(
            find.textContaining('No pudimos confirmar el envío'),
            findsOneWidget,
          );
          expect(
            tester
                .widget<FilledButton>(
                  find.widgetWithText(FilledButton, 'Enviar'),
                )
                .onPressed,
            isNull,
          );
          await tester.tap(find.byType(BackButton));
          await tester.pumpAndSettle();
          expect(find.text('Volver al listado'), findsOneWidget);
          await tester.tap(find.text('Volver y comprobar'));
          await tester.pumpAndSettle();
        }
        await tester.scrollUntilVisible(
          find.text('Experiencia sintética QA'),
          150,
          scrollable: find.byType(Scrollable).first,
        );
        expect(find.text('Experiencia sintética QA'), findsOneWidget);
        expect(reads, 2);
        expect(submissions, 1);
        if (!lost) {
          await tester.ensureVisible(find.text('0 Me gusta'));
          await tester.pumpAndSettle();
          await tester.tap(find.text('0 Me gusta'));
          await tester.pumpAndSettle();
          expect(reactions, 1);
          expect(find.text('1 Me gusta'), findsOneWidget);
          await tester.tap(find.text('0 comentarios'));
          await tester.pumpAndSettle();
          await tester.tap(find.text('Escribir comentario'));
          await tester.pumpAndSettle();
          await tester.enterText(
            find.byType(TextField),
            'Comentario sintético QA',
          );
          await tester.tap(find.text('Enviar'));
          await tester.pumpAndSettle();
          expect(comments.length, 1);
          expect(find.text('Comentario sintético QA'), findsOneWidget);
        }
        expect(tester.takeException(), isNull);
      },
    );
  }
  testWidgets(
    'Moderator can withdraw another publication only with a stated reason',
    (tester) async {
      var removed = false;
      Map<String, dynamic>? sent;
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
              'nombre': 'Moderador QA',
              'email': 'moderador@example.invalid',
            });
          }
          if (request.url.path.endsWith('/retirar/')) {
            sent = jsonDecode(request.body) as Map<String, dynamic>;
            removed = true;
            return json({'oculta': true});
          }
          return json({
            'results': removed
                ? []
                : [
                    {
                      'id': 1,
                      'autor': 'Miembro QA',
                      'contenido': 'Mensaje público QA',
                      'fecha': '2026-11-20T12:00:00Z',
                      'propia': false,
                      'reacciones': 0,
                      'comentarios': 0,
                      'reaccion_propia': false,
                    },
                  ],
            'antes': null,
            'puede_publicar': false,
            'puede_moderar': true,
          });
        }),
      );
      final session = Session(api);
      addTearDown(() {
        session.dispose();
        api.close();
      });
      await session.restore();
      await session.login('moderador@example.invalid', 'synthetic-password');
      await tester.pumpWidget(
        MaterialApp(
          home: CommunityScreen(api: api, session: session),
        ),
      );
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text('Moderar publicación'),
        150,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Moderar publicación'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Retirar'));
      await tester.pumpAndSettle();
      expect(removed, isFalse);
      expect(
        find.text('Explica el motivo con al menos cinco caracteres.'),
        findsOneWidget,
      );
      await tester.enterText(find.byType(TextFormField), 'Motivo sintético QA');
      await tester.tap(find.text('Retirar'));
      await tester.pumpAndSettle();
      expect(sent, {'motivo': 'Motivo sintético QA'});
      expect(removed, isTrue);
      expect(find.text('Mensaje público QA'), findsNothing);
      expect(tester.takeException(), isNull);
    },
  );
}
