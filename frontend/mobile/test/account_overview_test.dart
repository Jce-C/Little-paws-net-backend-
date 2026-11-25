import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/account_access.dart';
import 'package:little_paws_net/auth/account_screen.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

http.Response json(Object data, [int status = 200]) => http.Response(
  jsonEncode(data),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

void main() {
  late ApiClient api;
  late Session session;
  var reads = 0;
  var petReads = 0;
  late Future<http.Response> Function() pets;
  late Future<http.Response> Function() access;
  setUp(() async {
    reads = 0;
    petReads = 0;
    pets = () async => json([]);
    access = () async => json({
      'roles_globales': ['CIUDADANO', 'CIUDADANO'],
      'entidades': [
        {
          'id': 4,
          'nombre': 'Organización QA',
          'roles': ['GESTOR', 'CIUDADANO'],
        },
      ],
    });
    api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        if (request.url.path == '/api/auth/token/') {
          return json({'access': 'access-qa', 'refresh': 'refresh-qa'});
        }
        if (request.url.path == '/api/auth/token/revoke/') return json({});
        if (request.url.path == '/api/auth/perfil/') {
          return json({'nombre': 'Ana QA', 'email': 'ana@example.invalid'});
        }
        if (request.url.path == '/api/seguridad/mis-accesos/') {
          expect(request.method, 'GET');
          expect(request.headers['authorization'], 'Bearer access-qa');
          reads++;
          return access();
        }
        if (request.url.path == '/api/mascotas/mias/') {
          expect(request.method, 'GET');
          expect(request.headers['authorization'], 'Bearer access-qa');
          petReads++;
          return pets();
        }
        throw StateError('Unexpected route');
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
        home: Scaffold(body: AccountScreen(session: session)),
      ),
    );
    await tester.pumpAndSettle();
  }

  Future<void> login() =>
      session.login('ana@example.invalid', 'synthetic-password');

  testWidgets('Anonymous account does not load access data', (tester) async {
    await open(tester);
    expect(reads, 0);
    expect(petReads, 0);
    expect(find.text('Iniciar sesión'), findsOneWidget);
  });
  testWidgets(
    'Roles stay read-only and retain their platform or organization scope',
    (tester) async {
      await login();
      await open(tester);
      expect(reads, 1);
      expect(find.text('CIUDADANO'), findsNWidgets(2));
      expect(find.text('GESTOR'), findsOneWidget);
      expect(find.text('Plataforma'), findsOneWidget);
      expect(find.text('Organización QA'), findsNWidgets(2));
      expect(find.byType(Switch), findsNothing);
      expect(find.byType(Checkbox), findsNothing);
      await session.updateProfile(name: 'Ana QA');
      await tester.pumpAndSettle();
      expect(reads, 1);
    },
  );
  testWidgets(
    'Denied refresh removes previous roles and does not loop or renew',
    (tester) async {
      await login();
      await open(tester);
      expect(find.text('GESTOR'), findsOneWidget);
      access = () async => json({}, 403);
      await tester.ensureVisible(find.byTooltip('Actualizar mis roles'));
      await tester.tap(find.byTooltip('Actualizar mis roles'));
      await tester.pumpAndSettle();
      expect(reads, 2);
      expect(find.text('GESTOR'), findsNothing);
      expect(find.text('CIUDADANO'), findsNothing);
      expect(session.signedIn, isTrue);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Late role response after logout cannot restore private account data',
    (tester) async {
      final pending = Completer<http.Response>();
      access = () => pending.future;
      await login();
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Scaffold(body: AccountScreen(session: session)),
        ),
      );
      await tester.pump();
      expect(reads, 1);
      await session.logout();
      await tester.pump();
      pending.complete(
        json({
          'roles_globales': ['OLD_PRIVATE_ROLE'],
          'entidades': [],
        }),
      );
      await tester.pumpAndSettle();
      expect(find.text('OLD_PRIVATE_ROLE'), findsNothing);
      expect(find.text('ana@example.invalid'), findsNothing);
      expect(find.text('Iniciar sesión'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Malformed roles remain recoverable without inventing a default role',
    (tester) async {
      access = () async => json({
        'roles_globales': [null],
        'entidades': [],
      });
      await login();
      await open(tester);
      expect(reads, 1);
      expect(find.text('CIUDADANO'), findsNothing);
      expect(
        find.text('No pudimos verificar los roles de tu cuenta.'),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Long organization remains readable at 320px with enlarged text',
    (tester) async {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      const name =
          'Organización de protección y segundas oportunidades de La Guajira';
      access = () async => json({
        'roles_globales': [],
        'entidades': [
          {
            'id': 4,
            'nombre': name,
            'roles': ['RESPONSABLE_PRINCIPAL'],
          },
        ],
      });
      await login();
      await open(tester);
      await tester.scrollUntilVisible(find.text(name), 140);
      expect(tester.widget<Text>(find.text(name)).maxLines, isNull);
      await tester.scrollUntilVisible(find.text('Cerrar sesión'), 160);
      await tester.pumpAndSettle();
      expect(find.text('Cerrar sesión').hitTestable(), findsOneWidget);
      expect(reads, 1);
      expect(tester.takeException(), isNull);
    },
  );
  test('Access projection rejects malformed organization contracts', () async {
    await login();
    for (final org in [
      {'id': 0, 'nombre': 'QA', 'roles': []},
      {'id': 1, 'nombre': '', 'roles': []},
      {'id': 1, 'nombre': 'QA', 'roles': 'GESTOR'},
    ]) {
      access = () async => json({
        'roles_globales': [],
        'entidades': [org],
      });
      await expectLater(
        AccountAccess(session).load(),
        throwsA(isA<ApiException>()),
      );
    }
  });
  testWidgets(
    'Profile previews actual pets and hides medical action under active custody',
    (tester) async {
      pets = () async => json([
        {
          'id_mascota': 51,
          'nombre': 'Mascota propia QA',
          'especie': 'Perro',
          'estado': 'Adoptada',
          'custodia_vigente': false,
        },
        {
          'id_mascota': 52,
          'nombre': 'Mascota con custodia QA',
          'especie': 'Gato',
          'estado': 'En revisión',
          'custodia_vigente': true,
        },
      ]);
      await login();
      await open(tester);
      await tester.scrollUntilVisible(find.text('Mascota propia QA'), 140);
      await tester.pumpAndSettle();
      expect(find.text('Mascota con custodia QA'), findsOneWidget);
      expect(find.text('Ver expediente'), findsOneWidget);
      expect(petReads, 1);
      await tester.ensureVisible(find.byTooltip('Actualizar mis roles'));
      await tester.pumpAndSettle();
      await tester.tap(find.byTooltip('Actualizar mis roles'));
      await tester.pumpAndSettle();
      expect(petReads, 1);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Denied pet preview offers deliberate retry without automatic request loop',
    (tester) async {
      pets = () async => json({'detail': 'Acceso denegado QA'}, 403);
      await login();
      await open(tester);
      await tester.scrollUntilVisible(find.text('Reintentar mascotas'), 140);
      await tester.pumpAndSettle();
      expect(petReads, 1);
      expect(session.signedIn, isTrue);
      pets = () async => json([]);
      await tester.tap(find.text('Reintentar mascotas'));
      await tester.pumpAndSettle();
      expect(petReads, 2);
      expect(
        find.text('Todavía no tienes mascotas asociadas a tu cuenta.'),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Late pet response cannot reinsert private preview after logout',
    (tester) async {
      final pending = Completer<http.Response>();
      pets = () => pending.future;
      await login();
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Scaffold(body: AccountScreen(session: session)),
        ),
      );
      await tester.pump();
      expect(petReads, 1);
      await session.logout();
      await tester.pump();
      pending.complete(
        json([
          {
            'id_mascota': 53,
            'nombre': 'ANTIGUA_MASCOTA_PRIVADA',
            'especie': 'Perro',
            'estado': 'Adoptada',
            'custodia_vigente': false,
          },
        ]),
      );
      await tester.pumpAndSettle();
      expect(find.text('ANTIGUA_MASCOTA_PRIVADA'), findsNothing);
      expect(find.text('Iniciar sesión'), findsOneWidget);
      expect(session.signedIn, isFalse);
      expect(tester.takeException(), isNull);
    },
  );
}
