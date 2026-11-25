import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/account_screen.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/design/welcome_screen.dart';

void main() {
  setUpAll(() async {
    await (FontLoader(
      'MaterialIcons',
    )..addFont(rootBundle.load('fonts/MaterialIcons-Regular.otf'))).load();
    await (FontLoader(
      'Inter',
    )..addFont(rootBundle.load('assets/fonts/Inter.ttf'))).load();
    await (FontLoader(
      'LPN Script',
    )..addFont(rootBundle.load('assets/fonts/LeckerliOne.ttf'))).load();
  });
  for (final login in [false, true]) {
    testWidgets(
      'SVG reference composition and local image, ${login ? 'login' : 'welcome'}',
      (tester) async {
        tester.view.physicalSize = const Size(390, 884);
        tester.view.devicePixelRatio = 1;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);
        var requests = 0;
        final api = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((_) async {
            requests++;
            return http.Response('{}', 200);
          }),
        );
        final session = Session(api);
        await session.restore();
        const key = Key('reference-render');
        await tester.pumpWidget(
          RepaintBoundary(
            key: key,
            child: MaterialApp(
              theme: lpnTheme(),
              debugShowCheckedModeBanner: false,
              home: login
                  ? LoginScreen(session: session)
                  : WelcomeScreen(session: session, onExplore: () {}),
            ),
          ),
        );
        await tester.runAsync(
          () => precacheImage(
            AssetImage(
              'assets/access/${login ? 'login' : 'welcome'}-pets.webp',
            ),
            tester.element(find.byKey(key)),
          ),
        );
        await tester.pumpAndSettle();
        expect(requests, 0);
        expect(tester.takeException(), isNull);
        const renderDirectory = String.fromEnvironment('LPN_VISUAL_QA_DIR');
        if (renderDirectory.isNotEmpty) {
          await expectLater(
            find.byKey(key),
            matchesGoldenFile(
              Uri.file(
                '${renderDirectory.endsWith("/") ? renderDirectory : "$renderDirectory/"}${login ? 'login' : 'welcome'}-implementado.png',
              ),
            ),
          );
        }
        if (login) {
          final submit = find.byKey(const Key('account-submit'));
          expect(submit.hitTestable(), findsOneWidget);
        } else {
          for (final action in [
            'welcome-explore',
            'welcome-login',
            'welcome-register',
          ]) {
            expect(find.byKey(Key(action)).hitTestable(), findsOneWidget);
          }
        }
        await tester.pumpWidget(const SizedBox.shrink());
        session.dispose();
        api.close();
      },
    );
  }
}
