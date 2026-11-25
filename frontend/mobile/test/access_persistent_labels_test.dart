import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/account_screen.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/access_reference.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

void main() {
  const directory = String.fromEnvironment('LPN_VISUAL_QA_DIR');
  setUpAll(() async {
    for (final f in {
      'Inter': 'assets/fonts/Inter.ttf',
      'LPN Script': 'assets/fonts/LeckerliOne.ttf',
      'MaterialIcons': 'fonts/MaterialIcons-Regular.otf',
    }.entries) {
      await (FontLoader(f.key)..addFont(rootBundle.load(f.value))).load();
    }
  });
  for (final scale in [1.0, 2.0]) {
    for (final register in [false, true]) {
      testWidgets(
        'Access labels remain visible and named after typing and blur: register=$register scale=$scale',
        (tester) async {
          var calls = 0;
          final api = ApiClient(
            base: Uri.parse('http://localhost:8016'),
            client: MockClient((r) async {
              calls++;
              throw StateError('No request until submitting.');
            }),
          );
          final session = Session(api);
          addTearDown(session.dispose);
          addTearDown(api.close);
          tester.view.physicalSize = scale == 1
              ? const Size(393, 852)
              : const Size(320, 640);
          tester.view.devicePixelRatio = 1;
          addTearDown(tester.view.resetPhysicalSize);
          addTearDown(tester.view.resetDevicePixelRatio);
          final semantics = tester.ensureSemantics();
          try {
            await tester.pumpWidget(
              RepaintBoundary(
                key: const Key('access-label-capture'),
                child: MaterialApp(
                  theme: lpnTheme(),
                  builder: (context, child) => MediaQuery(
                    data: MediaQuery.of(context)
                        .copyWith(textScaler: TextScaler.linear(scale)),
                    child: child!,
                  ),
                  locale: const Locale('es'),
                  supportedLocales: const [Locale('es')],
                  localizationsDelegates: GlobalMaterialLocalizations.delegates,
                  debugShowCheckedModeBanner: false,
                  home: LoginScreen(
                    session: session,
                    initialRegister: register,
                  ),
                ),
              ),
            );
            await tester.runAsync(() async {
              await precacheImage(
                const AssetImage('assets/access/login-pets.webp'),
                tester.element(find.byKey(const Key('access-label-capture'))),
              );
            });
            await tester.pumpAndSettle();
            if (directory.isNotEmpty) {
              await expectLater(
                find.byKey(const Key('access-label-capture')),
                matchesGoldenFile(
                  '$directory/${scale == 1 ? 'normal' : 'texto-200'}-${register ? 'registro' : 'login'}-inicial.png',
                ),
              );
            }
            final labels = {
              if (register) 'account-name': ('Nombre completo', 'Persona QA'),
              'account-email': ('Correo electrónico', 'qa@example.invalid'),
              'account-password': ('Contraseña', 'synthetic-password'),
              if (register)
                'account-confirm-password': (
                  'Confirmar contraseña',
                  'synthetic-password',
                ),
            };
            for (final item in labels.entries) {
              final field = find.byKey(Key(item.key));
              await tester.ensureVisible(field);
              await tester.enterText(field, item.value.$2);
            }
            FocusManager.instance.primaryFocus?.unfocus();
            await tester.pumpAndSettle();
            for (final item in labels.entries) {
              final field = find.byKey(Key(item.key));
              await tester.ensureVisible(field);
              await tester.pumpAndSettle();
              expect(
                find.text(item.value.$1),
                scale == 1 ? findsOneWidget : findsNWidgets(2),
              );
              if (scale > 1) {
                expect(
                  find.byKey(ValueKey('access-caption-${item.value.$1}')),
                  findsOneWidget,
                );
              }
              final named = find.bySemanticsLabel(item.value.$1);
              expect(named, findsWidgets);
              expect(
                tester
                    .getSemantics(named.first)
                    .getSemanticsData()
                    .flagsCollection
                    .isTextField,
                isTrue,
              );
            }
            if (directory.isNotEmpty) {
              await tester.ensureVisible(
                find.byKey(const Key('account-email')),
              );
              await tester.pumpAndSettle();
              await expectLater(
                find.byKey(const Key('access-label-capture')),
                matchesGoldenFile(
                  '$directory/${scale == 1 ? 'normal' : 'texto-200'}-${register ? 'registro' : 'login'}-completo.png',
                ),
              );
            }
            if (scale > 1) {
              tester.view.viewInsets = const FakeViewPadding(bottom: 200);
              addTearDown(tester.view.resetViewInsets);
              await tester.pumpAndSettle();
              final submit = find.byKey(const Key('account-submit'));
              expect(tester.getBottomRight(submit).dy, lessThanOrEqualTo(440));
              await tester.ensureVisible(
                find.byKey(const Key('account-password')),
              );
              await tester.pumpAndSettle();
              if (directory.isNotEmpty) {
                await expectLater(
                  find.byKey(const Key('access-label-capture')),
                  matchesGoldenFile(
                    '$directory/teclado-${register ? 'registro' : 'login'}.png',
                  ),
                );
              }
            }
            expect(calls, 0);
            expect(tester.takeException(), isNull);
          } finally {
            semantics.dispose();
          }
        },
      );
    }
  }
  test('Access field label and input contrast meet normal-text minimum', () {
    double contrast(Color a, Color b) {
      final x = a.computeLuminance(), y = b.computeLuminance();
      return ((x > y ? x : y) + .05) / ((x < y ? x : y) + .05);
    }

    expect(
      contrast(AccessPalette.brown, AccessPalette.sand),
      greaterThanOrEqualTo(4.5),
    );
    expect(
      contrast(const Color(0xfffef3c7), AccessPalette.brown),
      greaterThanOrEqualTo(4.5),
    );
  });
}
