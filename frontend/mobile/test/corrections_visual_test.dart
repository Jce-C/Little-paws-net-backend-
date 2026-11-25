import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/catalog_hero.dart';
import 'package:little_paws_net/design/rescue_hero.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/explore/community_screen.dart';
import 'package:little_paws_net/rescue/anonymous_report_screen.dart';
import 'package:little_paws_net/rescue/rescue_api.dart';

void main() {
  const directory = String.fromEnvironment('LPN_VISUAL_QA_DIR');
  setUpAll(() async {
    for (final entry in {
      'Inter': 'assets/fonts/Inter.ttf',
      'MaterialIcons': 'fonts/MaterialIcons-Regular.otf',
    }.entries) {
      await (FontLoader(
        entry.key,
      )..addFont(rootBundle.load(entry.value))).load();
    }
  });
  for (final page in ['adopcion', 'rescate', 'comunidad', 'editar-reporte']) {
    testWidgets('Visual correction: $page', (tester) async {
      tester.view.physicalSize = const Size(393, 852);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient(
          (_) async => http.Response(
            jsonEncode({
              'results': [
                for (var i = 1; i <= 3; i++)
                  {
                    'id': i,
                    'autor': 'Comunidad de ejemplo',
                    'fecha': '2026-11-24T12:00:00Z',
                    'contenido': [
                      'Hoy acompañamos una jornada de cuidado y adopción.',
                      'Gracias a quienes ofrecen un hogar temporal.',
                      'Cada pequeño gesto ayuda a nuestra comunidad.',
                    ][i - 1],
                    'reacciones': i,
                    'comentarios': 0,
                    'propia': false,
                    'reaccion_propia': false,
                  },
              ],
              'antes': null,
              'puede_publicar': false,
            }),
            200,
            headers: {'content-type': 'application/json'},
          ),
        ),
      );
      final session = Session(api);
      await session.restore();
      Widget home;
      if (page == 'adopcion') {
        home = Scaffold(
          appBar: AppBar(title: const Text('Adopción')),
          body: SingleChildScrollView(
            child: CatalogHero(
              species: const ['Gato', 'Perro', 'Conejo'],
              selected: '',
              counter: '3 resultados',
              onSelected: (_) {},
            ),
          ),
        );
      } else if (page == 'rescate') {
        home = Scaffold(
          appBar: AppBar(title: const Text('Animales que necesitan ayuda')),
          body: SingleChildScrollView(
            child: RescueHero(onSearchChanged: (_) {}),
          ),
        );
      } else if (page == 'comunidad') {
        home = CommunityScreen(api: api, session: session);
      } else {
        home = AnonymousReportScreen(
          api: RescueApi(api, session),
          reportId: 12,
        );
      }
      const key = Key('correction-snapshot');
      await tester.pumpWidget(
        RepaintBoundary(
          key: key,
          child: MaterialApp(
            theme: lpnTheme(),
            debugShowCheckedModeBanner: false,
            home: home,
          ),
        ),
      );
      if (page == 'adopcion' || page == 'rescate') {
        await tester.runAsync(
          () => precacheImage(
            AssetImage(
              'assets/${page == 'adopcion' ? 'adoption' : 'rescue'}-banner.webp',
            ),
            tester.element(find.byKey(key)),
          ),
        );
      }
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
      await expectLater(
        find.byKey(key),
        matchesGoldenFile(Uri.file('$directory/$page.png')),
      );
      await tester.pumpWidget(const SizedBox.shrink());
      session.dispose();
      api.close();
    }, skip: directory.isEmpty);
  }
}
