import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/account_screen.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';

http.Response json(Object data, [int status = 200]) => http.Response(
  jsonEncode(data),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

void main() {
  late ApiClient api;
  late Session session;
  var name = 'Ana QA';
  var phone = '3001234567';
  var writes = 0;
  var denied = false;
  Map<String, dynamic>? saved;

  setUp(() async {
    name = 'Ana QA';
    phone = '3001234567';
    writes = 0;
    denied = false;
    saved = null;
    api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        if (request.url.path == '/api/auth/token/') {
          return json({'access': 'access', 'refresh': 'refresh'});
        }
        if (request.url.path == '/api/auth/token/revoke/') return json({});
        if (request.url.path == '/api/seguridad/mis-accesos/') {
          return json({
            'roles_globales': ['CIUDADANO'],
            'entidades': [],
          });
        }
        if (request.url.path == '/api/auth/perfil/') {
          if (request.method == 'PATCH') {
            expect(request.headers['authorization'], 'Bearer access');
            writes++;
            if (denied) return json({}, 403);
            saved = jsonDecode(request.body) as Map<String, dynamic>;
            name = saved!['nombre'] as String? ?? name;
            phone = saved!['telefono'] as String? ?? phone;
          }
          return json({
            'nombre': name,
            'email': 'ana@example.invalid',
            'telefono': phone,
          });
        }
        throw StateError('Unexpected route');
      }),
    );
    session = Session(api);
    await session.restore();
    await session.login('ana@example.invalid', 'test-password');
  });

  tearDown(() {
    session.dispose();
    api.close();
  });

  Future<void> open(WidgetTester tester, {bool enlarged = false}) async {
    if (enlarged) {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
    }
    await tester.pumpWidget(
      MaterialApp(
        builder: enlarged
            ? (context, child) => MediaQuery(
                data: MediaQuery.of(context)
                    .copyWith(textScaler: const TextScaler.linear(2)),
                child: child!,
              )
            : null,
        home: Scaffold(body: AccountScreen(session: session)),
      ),
    );
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Editar perfil'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Editar perfil'));
    await tester.pumpAndSettle();
  }

  testWidgets('Save updates account and sends only changed personal fields', (
    tester,
  ) async {
    await open(tester);
    expect(writes, 0);
    await tester.enterText(
      find.byKey(const Key('profile-name')),
      'Ana Actualizada QA',
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('profile-save')));
    await tester.pumpAndSettle();
    expect(saved, {'nombre': 'Ana Actualizada QA'});
    expect(session.account!.phone, '3001234567');
    expect(find.text('Ana Actualizada QA'), findsOneWidget);
    expect(find.text('Tu perfil se actualizó.'), findsOneWidget);
    await tester.tap(find.text('Editar perfil'));
    await tester.pumpAndSettle();
    expect(find.text('Tu perfil se actualizó.'), findsNothing);
    await tester.enterText(
      find.byKey(const Key('profile-name')),
      'Ana Segunda QA',
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('profile-save')).hitTestable(), findsOneWidget);
    await tester.tap(find.byKey(const Key('profile-save')));
    await tester.pumpAndSettle();
    expect(session.account!.name, 'Ana Segunda QA');
  });

  testWidgets('Cancel offers discard or continue without writing', (
    tester,
  ) async {
    await open(tester);
    await tester.enterText(
      find.byKey(const Key('profile-name')),
      'Borrador QA',
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Cancelar'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Seguir editando'));
    await tester.pumpAndSettle();
    expect(find.text('Borrador QA'), findsOneWidget);
    await tester.tap(find.byType(BackButton).last);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Descartar'));
    await tester.pumpAndSettle();
    expect(writes, 0);
    expect(find.text('Borrador QA'), findsNothing);
    expect(find.text('Ana QA'), findsOneWidget);
  });

  testWidgets('Logout removes contact fields and unsaved private data', (
    tester,
  ) async {
    await open(tester);
    await tester.enterText(
      find.byKey(const Key('profile-name')),
      'Borrador privado QA',
    );
    await tester.pumpAndSettle();
    await session.logout();
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('profile-name')), findsNothing);
    expect(find.text('Borrador privado QA'), findsNothing);
    expect(find.text('ana@example.invalid'), findsNothing);
    expect(
      find.text('Inicia sesión de nuevo para editar tu perfil.'),
      findsOneWidget,
    );
    expect(writes, 0);
  });

  testWidgets(
    'Rejected save preserves draft and allows retry without changing account',
    (tester) async {
      await open(tester);
      denied = true;
      await tester.enterText(
        find.byKey(const Key('profile-name')),
        'Reintento QA',
      );
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('profile-save')));
      await tester.pumpAndSettle();
      expect(session.account!.name, 'Ana QA');
      expect(find.text('Reintento QA'), findsOneWidget);
      expect(
        find.text('Tu cuenta no tiene acceso para realizar esta acción.'),
        findsOneWidget,
      );
      await tester.tap(find.widgetWithText(TextButton, 'Cerrar'));
      await tester.pumpAndSettle();
      denied = false;
      await tester.tap(find.byKey(const Key('profile-save')));
      await tester.pumpAndSettle();
      expect(session.account!.name, 'Reintento QA');
    },
  );

  testWidgets('Invalid phone is rejected and explicit blank removes it', (
    tester,
  ) async {
    await open(tester);
    await tester.enterText(find.byKey(const Key('profile-phone')), 'abc');
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('profile-save')));
    await tester.pumpAndSettle();
    expect(find.text('Usa entre 7 y 15 dígitos.'), findsOneWidget);
    expect(writes, 0);
    await tester.enterText(find.byKey(const Key('profile-phone')), '');
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('profile-save')));
    await tester.pumpAndSettle();
    expect(saved, {'telefono': ''});
    expect(session.account!.phone, '');
  });

  testWidgets('Save remains reachable at 320px and 200 percent text', (
    tester,
  ) async {
    await open(tester, enlarged: true);
    await tester.ensureVisible(find.byKey(const Key('profile-name')));
    await tester.enterText(
      find.byKey(const Key('profile-name')),
      'Accesible QA',
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('profile-save')), findsOneWidget);
    await tester.tap(find.byKey(const Key('profile-save')));
    await tester.pumpAndSettle();
    expect(session.account!.name, 'Accesible QA');
    expect(tester.takeException(), isNull);
  });

  testWidgets('Save stays above the keyboard with enlarged text', (
    tester,
  ) async {
    await open(tester, enlarged: true);
    tester.view.viewInsets = const FakeViewPadding(bottom: 280);
    addTearDown(tester.view.resetViewInsets);
    await tester.pumpAndSettle();
    final bottom = tester
        .getBottomRight(find.byKey(const Key('profile-save')))
        .dy;
    expect(bottom, lessThanOrEqualTo(360));
    expect(tester.takeException(), isNull);
  });

  test(
    'Late save after logout cannot restore or modify the next session',
    () async {
      final release = Completer<http.Response>();
      final started = Completer<void>();
      final isolatedApi = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          if (request.url.path == '/api/auth/token/') {
            return json({'access': 'access', 'refresh': 'refresh'});
          }
          if (request.url.path == '/api/auth/token/revoke/') return json({});
          if (request.method == 'PATCH') {
            started.complete();
            return release.future;
          }
          return json({'nombre': 'Ana QA', 'email': 'ana@example.invalid'});
        }),
      );
      final isolated = Session(isolatedApi);
      addTearDown(isolated.dispose);
      addTearDown(isolatedApi.close);
      await isolated.login('ana@example.invalid', 'test-password');
      final operation = isolated.updateProfile(name: 'Respuesta antigua QA');
      final rejected = expectLater(operation, throwsA(isA<ApiException>()));
      await started.future;
      await isolated.logout();
      release.complete(
        json({
          'nombre': 'Respuesta antigua QA',
          'email': 'ana@example.invalid',
        }),
      );
      await rejected;
      expect(isolated.account, isNull);
    },
  );
}
