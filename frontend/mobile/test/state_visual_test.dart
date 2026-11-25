import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/explore/explore_screens.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

void main() {
  const directory = String.fromEnvironment('LPN_VISUAL_QA_DIR');
  setUpAll(() async {
    for (final f in {
      'Inter': 'assets/fonts/Inter.ttf',
      'MaterialIcons': 'fonts/MaterialIcons-Regular.otf',
    }.entries) {
      await (FontLoader(f.key)..addFont(rootBundle.load(f.value))).load();
    }
  });
  for (final scale in [1.0, 2.0]) {
    testWidgets('Loading to empty uses one request at text scale $scale', (
      tester,
    ) async {
      var reads = 0;
      final pending = Completer<http.Response>();
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((r) {
          reads++;
          return pending.future;
        }),
      );
      addTearDown(api.close);
      tester.view.physicalSize = scale == 1
          ? const Size(390, 884)
          : const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await tester.pumpWidget(
        RepaintBoundary(
          key: const Key('state-capture'),
          child: MaterialApp(
            theme: lpnTheme(),
            locale: const Locale('es'),
            supportedLocales: const [Locale('es')],
            localizationsDelegates: GlobalMaterialLocalizations.delegates,
            debugShowCheckedModeBanner: false,
            builder: (context, child) => MediaQuery(
              data: MediaQuery.of(context)
                  .copyWith(textScaler: TextScaler.linear(scale)),
              child: child!,
            ),
            home: PublicListScreen(
              api: api,
              path: '/api/catalogo/productos/',
              title: 'Tienda',
              kind: 'products',
            ),
          ),
        ),
      );
      await tester.pump(const Duration(milliseconds: 200));
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(reads, 1);
      if (directory.isNotEmpty) {
        await expectLater(
          find.byKey(const Key('state-capture')),
          matchesGoldenFile(
            '$directory/${scale == 1 ? 'normal' : 'texto-200'}/tienda-cargando.png',
          ),
        );
      }
      pending.complete(
        http.Response('[]', 200, headers: {'content-type': 'application/json'}),
      );
      await tester.pumpAndSettle();
      expect(find.byType(CircularProgressIndicator), findsNothing);
      expect(reads, 1);
      expect(find.textContaining('Todavía no hay información'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  }
}
