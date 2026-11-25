import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:little_paws_net/main.dart' show LittlePawsApp;
import 'package:little_paws_net/design/lpn_navigation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/auth/account_screen.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

void main() {
  testWidgets(
    'Successful welcome login enters Home rather than fetching the catalog',
    (tester) async {
      FlutterSecureStorage.setMockInitialValues({});
      var calls = 0;
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          calls++;
          if (request.url.path == '/api/auth/token/') {
            return http.Response(
              jsonEncode({
                'access': 'synthetic',
                'refresh': 'synthetic-refresh',
              }),
              200,
            );
          }
          if (request.url.path == '/api/auth/perfil/') {
            return http.Response(
              jsonEncode({
                'nombre': 'Persona QA',
                'email': 'qa@example.invalid',
              }),
              200,
            );
          }
          throw StateError('Unexpected request after welcome login');
        }),
      );
      await tester.pumpWidget(LittlePawsApp(api: api));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('welcome-login')));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.byKey(const Key('account-email')),
        'qa@example.invalid',
      );
      await tester.enterText(
        find.byKey(const Key('account-password')),
        'synthetic-password',
      );
      final submit = find.byKey(const Key('account-submit'));
      await tester.ensureVisible(submit);
      await tester.tap(submit);
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('integrated-home-header')), findsOneWidget);
      expect(
        tester.widget<LpnNavigation>(find.byType(LpnNavigation)).selected,
        0,
      );
      expect(calls, 2);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'Switching to registration returns to the full-width wave and brand',
    (tester) async {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient(
          (request) async => throw StateError('No network on access'),
        ),
      );
      final session = Session(api);
      addTearDown(() {
        session.dispose();
        api.close();
      });
      await session.restore();
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: LoginScreen(session: session),
        ),
      );
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.text('Registrarme'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Registrarme'));
      await tester.pumpAndSettle();
      final wave = tester.getRect(find.byKey(const Key('access-wave')));
      expect(wave.left, 0);
      expect(wave.right, 320);
      expect(find.text('Little Paws Net').hitTestable(), findsOneWidget);
      final scroll = tester.state<ScrollableState>(
        find.byType(Scrollable).first,
      );
      expect(scroll.position.pixels, 0);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'Login validates on submit, clears corrected errors, and does not query while typing',
    (tester) async {
      var calls = 0;
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          calls++;
          throw StateError('No network before valid submission');
        }),
      );
      final session = Session(api);
      addTearDown(() {
        session.dispose();
        api.close();
      });
      await session.restore();
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: LoginScreen(session: session),
        ),
      );
      await tester.pumpAndSettle();
      final email = find.byKey(const Key('account-email'));
      await tester.enterText(email, 'ana');
      await tester.pumpAndSettle();
      expect(find.text('Escribe un correo válido.'), findsNothing);
      final submit = find.byKey(const Key('account-submit'));
      await tester.ensureVisible(submit);
      await tester.tap(submit);
      await tester.pumpAndSettle();
      expect(find.text('Escribe un correo válido.'), findsOneWidget);
      await tester.ensureVisible(email);
      await tester.enterText(email, 'ana@example.invalid');
      await tester.pumpAndSettle();
      expect(find.text('Escribe un correo válido.'), findsNothing);
      expect(calls, 0);
      expect(tester.takeException(), isNull);
    },
  );
}
