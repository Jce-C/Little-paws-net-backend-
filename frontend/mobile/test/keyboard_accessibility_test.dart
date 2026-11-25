import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/auth/account_screen.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/form_surfaces.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/explore/message_composer.dart';
import 'package:little_paws_net/pets/personal_pet_screen.dart';

Widget app(Widget child, double scale) => MaterialApp(
  theme: lpnTheme(),
  locale: const Locale('es'),
  supportedLocales: const [Locale('es')],
  localizationsDelegates: GlobalMaterialLocalizations.delegates,
  builder: (context, child) => MediaQuery(
    data: MediaQuery.of(context).copyWith(textScaler: TextScaler.linear(scale)),
    child: child!,
  ),
  home: child,
);

void main() {
  late ApiClient api;
  late Session session;
  var writes = 0;
  setUp(() async {
    writes = 0;
    api = ApiClient(
      base: Uri.parse('https://qa.example.invalid'),
      client: MockClient((r) async {
        Object data = {};
        if (r.url.path == '/api/auth/token/') {
          data = {'access': 'synthetic-access', 'refresh': 'synthetic-refresh'};
        } else if (r.url.path == '/api/auth/perfil/') {
          data = {'email': 'qa@example.invalid', 'nombre': 'Persona QA'};
        } else if (r.method != 'GET') {
          writes++;
        }
        return http.Response(
          jsonEncode(data),
          200,
          headers: {'content-type': 'application/json'},
        );
      }),
    );
    session = Session(api);
    await session.restore();
    await session.login('qa@example.invalid', 'synthetic-password');
  });
  tearDown(() {
    session.dispose();
    api.close();
  });

  Widget message() => PublicMessageScreen(
    api: api,
    session: session,
    path: '/api/comunidad/publicaciones/',
    title: 'Crear publicación',
  );
  for (final register in [false, true]) {
    testWidgets(
      'Access preserves fields in extreme landscape keyboard and restores submit: register=$register',
      (tester) async {
        tester.view.devicePixelRatio = 1;
        tester.view.physicalSize = const Size(800, 360);
        addTearDown(tester.view.resetDevicePixelRatio);
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetViewInsets);
        await tester.pumpWidget(
          app(LoginScreen(session: session, initialRegister: register), 1),
        );
        await tester.pumpAndSettle();
        final email = find.byKey(const Key('account-email'));
        await tester.scrollUntilVisible(
          email,
          250,
          scrollable: find.byType(Scrollable).first,
        );
        await tester.enterText(email, 'qa@example.invalid');
        tester.view.viewInsets = const FakeViewPadding(bottom: 260);
        await tester.pumpAndSettle();
        expect(find.byKey(const Key('account-submit')), findsNothing);
        expect(find.text('qa@example.invalid'), findsOneWidget);
        expect(tester.takeException(), isNull);
        tester.view.viewInsets = FakeViewPadding.zero;
        await tester.pumpAndSettle();
        expect(find.byKey(const Key('account-submit')), findsOneWidget);
        expect(find.text('qa@example.invalid'), findsOneWidget);
        expect(writes, 0);
      },
    );
    testWidgets(
      'Access keyboard Next moves to the next field rather than the password icon: register=$register',
      (tester) async {
        await tester.pumpWidget(
          app(LoginScreen(session: session, initialRegister: register), 1),
        );
        await tester.pumpAndSettle();
        final email = find.byKey(const Key('account-email'));
        await tester.scrollUntilVisible(
          email,
          250,
          scrollable: find.byType(Scrollable).first,
        );
        await tester.enterText(email, 'qa@example.invalid');
        await tester.testTextInput.receiveAction(TextInputAction.next);
        await tester.pumpAndSettle();
        final password = find.byKey(const Key('account-password'));
        final editable = find.descendant(
          of: password,
          matching: find.byType(EditableText),
        );
        expect(
          tester.widget<EditableText>(editable).focusNode.hasFocus,
          isTrue,
        );
        if (register) {
          await tester.enterText(password, 'synthetic-password');
          await tester.testTextInput.receiveAction(TextInputAction.next);
          await tester.pumpAndSettle();
          final confirm = find.descendant(
            of: find.byKey(const Key('account-confirm-password')),
            matching: find.byType(EditableText),
          );
          expect(
            tester.widget<EditableText>(confirm).focusNode.hasFocus,
            isTrue,
          );
        }
        expect(tester.takeException(), isNull);
        expect(writes, 0);
      },
    );
  }

  for (final viewport in [
    (size: const Size(320, 640), scale: 2.0, keyboard: 200.0),
    (size: const Size(800, 360), scale: 1.0, keyboard: 120.0),
    (size: const Size(800, 1280), scale: 2.0, keyboard: 320.0),
  ]) {
    for (final pet in [false, true]) {
      testWidgets(
        'Actions remain above keyboard: pet=$pet viewport=$viewport',
        (tester) async {
          tester.view.devicePixelRatio = 1;
          tester.view.physicalSize = viewport.size;
          addTearDown(tester.view.resetDevicePixelRatio);
          addTearDown(tester.view.resetPhysicalSize);
          addTearDown(tester.view.resetViewInsets);
          await tester.pumpWidget(
            app(
              pet ? PersonalPetScreen(session: session) : message(),
              viewport.scale,
            ),
          );
          await tester.pumpAndSettle();
          final field = pet
              ? find.byKey(const Key('personal-nombre'))
              : find.byType(TextField);
          await tester.scrollUntilVisible(
            field,
            250,
            scrollable: find.byType(Scrollable).first,
          );
          await tester.enterText(field, 'Borrador QA');
          tester.view.viewInsets = FakeViewPadding(bottom: viewport.keyboard);
          await tester.pumpAndSettle();
          final action = pet
              ? find.byKey(const Key('personal-save'))
              : find.text('Enviar');
          final rect = tester.getRect(action);
          expect(
            rect.bottom,
            lessThanOrEqualTo(viewport.size.height - viewport.keyboard),
          );
          expect(rect.top, greaterThanOrEqualTo(0));
          expect(tester.takeException(), isNull);
          expect(writes, 0);
        },
      );
    }
  }

  testWidgets(
    'Body action bar uses the resized body without a second keyboard inset',
    (tester) async {
      tester.view.devicePixelRatio = 1;
      tester.view.physicalSize = const Size(400, 800);
      tester.view.viewInsets = const FakeViewPadding(bottom: 300);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetViewInsets);
      await tester.pumpWidget(
        app(
          Scaffold(
            body: Column(
              children: [
                const Expanded(child: SizedBox()),
                LpnActionBar(
                  child: FilledButton(
                    onPressed: () {},
                    child: const Text('Continuar'),
                  ),
                ),
              ],
            ),
          ),
          1,
        ),
      );
      await tester.pumpAndSettle();
      final rect = tester.getRect(find.text('Continuar'));
      expect(rect.bottom, lessThanOrEqualTo(500));
      expect(rect.bottom, greaterThan(450));
    },
  );

  testWidgets(
    'Very tall landscape keyboard reserves room for editing and restores actions on dismissal',
    (tester) async {
      tester.view.devicePixelRatio = 1;
      tester.view.physicalSize = const Size(800, 360);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetViewInsets);
      await tester.pumpWidget(app(message(), 1));
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.byType(TextField),
        250,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.enterText(find.byType(TextField), 'Borrador horizontal');
      tester.view.viewInsets = const FakeViewPadding(bottom: 260);
      await tester.pumpAndSettle();
      expect(find.text('Enviar'), findsNothing);
      expect(find.text('Borrador horizontal'), findsOneWidget);
      expect(tester.takeException(), isNull);
      tester.view.viewInsets = FakeViewPadding.zero;
      await tester.pumpAndSettle();
      expect(find.text('Enviar'), findsOneWidget);
      expect(find.text('Borrador horizontal'), findsOneWidget);
      expect(writes, 0);
    },
  );

  testWidgets(
    'Dismiss discard confirmation with Escape and preserve the draft',
    (tester) async {
      await tester.pumpWidget(
        app(
          Builder(
            builder: (context) => Scaffold(
              body: TextButton(
                onPressed: () => Navigator.of(context)
                    .push(MaterialPageRoute<void>(builder: (_) => message())),
                child: const Text('Abrir'),
              ),
            ),
          ),
          1,
        ),
      );
      await tester.tap(find.text('Abrir'));
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextField), 'Borrador conservado');
      await tester.pumpAndSettle();
      await tester.tap(find.byType(BackButton));
      await tester.pumpAndSettle();
      expect(find.text('¿Descartar el borrador?'), findsOneWidget);
      for (var i = 0; i < 6; i++) {
        await tester.sendKeyEvent(LogicalKeyboardKey.tab);
        await tester.pump();
        final focused = FocusManager.instance.primaryFocus!.context!;
        expect(focused.findAncestorWidgetOfExactType<AlertDialog>(), isNotNull);
      }
      await tester.sendKeyEvent(LogicalKeyboardKey.escape);
      await tester.pumpAndSettle();
      expect(find.byType(AlertDialog), findsNothing);
      expect(find.text('Borrador conservado'), findsOneWidget);
      expect(writes, 0);
    },
  );
}
