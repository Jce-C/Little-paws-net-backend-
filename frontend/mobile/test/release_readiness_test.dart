import 'package:little_paws_net/rescue/my_sponsorships_screen.dart';

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/design/readable_text.dart';
import 'package:little_paws_net/explore/bank_instructions.dart';
import 'package:little_paws_net/pets/personal_pet_screen.dart';
import 'package:little_paws_net/rescue/report_photo.dart';
import 'package:little_paws_net/rescue/rescue_api.dart';
import 'package:little_paws_net/rescue/rescue_screens.dart';
import 'package:little_paws_net/rescue/sponsorship_screen.dart';

http.Response reply(Object data, [int status = 200]) => http.Response(
  jsonEncode(data),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);
void main() {
  setUp(() => FlutterSecureStorage.setMockInitialValues({}));
  testWidgets(
    'Own and history report cards show city, photograph fallback and status',
    (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Scaffold(
            body: ReportTile(
              report: const AnimalReport(
                id: 1,
                type: 'Rescate',
                status: 'Aceptado',
                description: 'Descripción QA',
                city: 'Riohacha',
              ),
            ),
          ),
        ),
      );
      expect(find.byType(ReportPhoto), findsOneWidget);
      expect(find.text('Riohacha'), findsOneWidget);
      expect(find.text('Aceptado'), findsOneWidget);
    },
  );
  for (final savedBeforeFailure in [true, false]) {
    for (final personal in [true, false]) {
      testWidgets(
        '${personal ? 'Personal pet' : 'Sponsorship'} recovers without duplicates, server saved: $savedBeforeFailure',
        (tester) async {
          final keys = <String>[];
          final stored = <String, int>{};
          var posts = 0, bankReads = 0;
          final api = ApiClient(
            base: Uri.parse('http://localhost:8016'),
            client: MockClient((request) async {
              if (request.url.path == '/api/auth/token/') {
                return reply({
                  'access': 'synthetic',
                  'refresh': 'synthetic-refresh',
                });
              }
              if (request.url.path == '/api/auth/perfil/') {
                return reply({
                  'nombre': 'QA',
                  'email': 'qa@example.invalid',
                  'reintentos_seguros': true,
                });
              }
              if (request.url.path.endsWith('/cuenta/')) {
                bankReads++;
                return bankReads == 1
                    ? reply({
                        'detalle': 'Consulta temporalmente no disponible',
                      }, 503)
                    : reply({
                        'organizacion': 'Receptora QA',
                        'titular': 'Titular QA',
                        'banco': 'Banco QA',
                        'tipo_cuenta': 'Ahorros',
                        'numero_cuenta': '0000000072',
                        'identificacion_titular': 'QA-72',
                      });
              }
              posts++;
              final key = request.headers['idempotency-key'];
              expect(key, isNotNull);
              keys.add(key!);
              final body = jsonDecode(request.body) as Map;
              if (personal) expect(body['edad_meses'], 8);
              if (posts == 1) {
                if (savedBeforeFailure) stored[key] = 72;
                return reply({'detalle': 'Respuesta perdida QA'}, 503);
              }
              stored.putIfAbsent(key, () => 72);
              return reply(
                personal
                    ? {'id_mascota': stored[key], 'nombre': 'Milo QA'}
                    : {'id_apadrinamiento': stored[key]},
                201,
              );
            }),
          );
          final session = Session(api);
          addTearDown(api.close);
          addTearDown(session.dispose);
          await session.restore();
          await session.login('qa@example.invalid', 'synthetic-password');
          await tester.pumpWidget(
            MaterialApp(
              theme: lpnTheme(),
              home: Builder(
                builder: (context) => Scaffold(
                  body: TextButton(
                    onPressed: () => Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => personal
                            ? PersonalPetScreen(session: session)
                            : SponsorshipScreen(session: session, reportId: 1),
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
          if (personal) {
            await tester.enterText(
              find.byKey(const Key('personal-nombre')),
              'Milo QA',
            );
            await tester.enterText(
              find.byKey(const Key('personal-especie')),
              'Gato',
            );
            await tester.enterText(
              find.byKey(const Key('personal-edad_meses')),
              '8',
            );
          } else {
            await tester.enterText(find.byType(TextField), '10000');
          }
          await tester.tap(
            find.text(personal ? 'Registrar mascota' : 'Registrar compromiso'),
          );
          await tester.pumpAndSettle();
          final recovery = personal
              ? 'Comprobar registro'
              : 'Comprobar compromiso';
          expect(find.text(recovery), findsOneWidget);
          if (personal) {
            expect(
              tester
                  .widget<TextFormField>(
                    find.byKey(const Key('personal-nombre')),
                  )
                  .enabled,
              isFalse,
            );
          }
          if (personal) {
            await tester.tap(find.widgetWithText(TextButton, 'Cerrar'));
            await tester.pumpAndSettle();
          }
          await tester.tap(find.text(recovery));
          await tester.pumpAndSettle();
          expect(posts, 2);
          expect(keys.toSet(), hasLength(1));
          expect(stored, hasLength(1));
          if (personal) {
            expect(find.text('Abrir'), findsOneWidget);
          } else {
            expect(find.text('Compromiso #72 registrado'), findsOneWidget);
            await tester.tap(find.text('Consultar de nuevo'));
            await tester.pumpAndSettle();
            expect(find.text('Receptora QA'), findsOneWidget);
            expect(posts, 2);
            expect(bankReads, 2);
          }
        },
      );
    }
  }
  testWidgets(
    'Reading values are exposed as static text, not disabled edit controls',
    (tester) async {
      final semantics = tester.ensureSemantics();
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          if (request.url.path == '/api/auth/token/') {
            return reply({
              'access': 'synthetic',
              'refresh': 'synthetic-refresh',
            });
          }
          if (request.url.path == '/api/auth/perfil/') {
            return reply({
              'nombre': 'QA',
              'email': 'qa@example.invalid',
              'reintentos_seguros': true,
            });
          }
          return reply({
            'organizacion': 'Receptora QA',
            'titular': 'Titular QA',
            'banco': 'Banco QA',
            'tipo_cuenta': 'Ahorros',
            'numero_cuenta': '0000000072',
            'identificacion_titular': 'QA-72',
          });
        }),
      );
      final session = Session(api);
      addTearDown(api.close);
      addTearDown(session.dispose);
      await session.restore();
      await session.login('qa@example.invalid', 'synthetic-password');
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Scaffold(
            body: SingleChildScrollView(
              child: BankInstructions(
                session: session,
                path: '/api/fondos/72/datos-aporte/',
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byType(ReadableText), findsNWidgets(6));
      expect(find.byType(SelectableText), findsNothing);
      expect(find.byType(EditableText), findsNothing);
      final tree = tester
          .getSemantics(find.byType(BankInstructions))
          .toStringDeep();
      await tester.pumpWidget(const SizedBox.shrink());
      semantics.dispose();
      expect(tree, contains('0000000072'));
    },
  );
  testWidgets(
    'Commitment history is paginated, refreshable and disappears when signed out',
    (tester) async {
      var reads = 0;
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          if (request.url.path == '/api/auth/token/') {
            return reply({
              'access': 'synthetic',
              'refresh': 'synthetic-refresh',
            });
          }
          if (request.url.path == '/api/auth/perfil/') {
            return reply({'nombre': 'QA', 'email': 'qa@example.invalid'});
          }
          if (request.url.path == '/api/auth/token/revoke/') return reply({});
          expect(request.url.path, '/api/apadrinamientos/mios/');
          reads++;
          final next = request.url.queryParameters['antes'];
          return reply({
            'results': [
              {
                'id_apadrinamiento': next == null ? 72 : 71,
                'reporte_id': 1,
                'organizacion': 'Receptora QA',
                'monto_comprometido': '10000.00',
                'estado': 'En espera',
                'fecha_compromiso': '2026-11-24T12:00:00Z',
              },
            ],
            'next_cursor': next == null ? '72' : null,
          });
        }),
      );
      final session = Session(api);
      addTearDown(api.close);
      addTearDown(session.dispose);
      await session.restore();
      await session.login('qa@example.invalid', 'synthetic-password');
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: MySponsorshipsScreen(session: session),
        ),
      );
      await tester.pumpAndSettle();
      expect(reads, 1);
      await tester.pumpAndSettle();
      expect(reads, 1);
      await tester.tap(find.text('Cargar más compromisos'));
      await tester.pumpAndSettle();
      expect(reads, 2);
      expect(find.text('Receptora QA'), findsNWidgets(2));
      await session.logout();
      await tester.pumpAndSettle();
      expect(find.text('Receptora QA'), findsNothing);
      expect(
        find.text('Inicia sesión para consultar tus compromisos.'),
        findsOneWidget,
      );
    },
  );

  for (final personal in [true, false]) {
    testWidgets(
      'Older servers cannot trigger an unsafe retry for ${personal ? 'pets' : 'sponsorships'}',
      (tester) async {
        var writes = 0;
        final api = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((request) async {
            if (request.url.path == '/api/auth/token/') {
              return reply({
                'access': 'synthetic',
                'refresh': 'synthetic-refresh',
              });
            }
            if (request.url.path == '/api/auth/perfil/') {
              return reply({'nombre': 'QA', 'email': 'qa@example.invalid'});
            }
            writes++;
            return reply({'detalle': 'Resultado sin confirmar'}, 503);
          }),
        );
        final session = Session(api);
        addTearDown(api.close);
        addTearDown(session.dispose);
        await session.restore();
        await session.login('qa@example.invalid', 'synthetic-password');
        await tester.pumpWidget(
          MaterialApp(
            theme: lpnTheme(),
            home: personal
                ? PersonalPetScreen(session: session)
                : SponsorshipScreen(session: session, reportId: 1),
          ),
        );
        await tester.pumpAndSettle();
        if (personal) {
          await tester.enterText(
            find.byKey(const Key('personal-nombre')),
            'Milo QA',
          );
          await tester.enterText(
            find.byKey(const Key('personal-especie')),
            'Gato',
          );
        } else {
          await tester.enterText(find.byType(TextField), '10000');
        }
        await tester.tap(
          find.text(personal ? 'Registrar mascota' : 'Registrar compromiso'),
        );
        await tester.pumpAndSettle();
        expect(writes, 1);
        if (personal) {
          expect(find.text('Comprobar registro'), findsNothing);
          expect(find.text('Ver mis mascotas'), findsOneWidget);
        } else {
          expect(
            tester
                .widget<FilledButton>(
                  find.widgetWithText(FilledButton, 'Comprobar compromiso'),
                )
                .onPressed,
            isNull,
          );
          expect(find.text('Ver mis compromisos'), findsOneWidget);
        }
      },
    );
  }
}
