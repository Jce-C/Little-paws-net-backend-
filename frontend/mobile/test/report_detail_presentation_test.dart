import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/rescue/rescue_api.dart';
import 'package:little_paws_net/rescue/rescue_screens.dart';

void main() {
  const directory = String.fromEnvironment('LPN_VISUAL_QA_DIR');
  setUpAll(() async {
    for (final font in {
      'Inter': 'assets/fonts/Inter.ttf',
      'MaterialIcons': 'fonts/MaterialIcons-Regular.otf',
    }.entries) {
      await (FontLoader(font.key)..addFont(rootBundle.load(font.value))).load();
    }
  });
  for (final accepted in [false, true]) {
    for (final enlarged in [false, true]) {
      testWidgets(
        'Report detail preserves real status and single scroll; accepted=$accepted enlarged=$enlarged',
        (tester) async {
          tester.view.physicalSize = enlarged
              ? const Size(320, 640)
              : const Size(393, 852);
          tester.view.devicePixelRatio = 1;
          tester.platformDispatcher.textScaleFactorTestValue = enlarged ? 2 : 1;
          addTearDown(tester.view.resetPhysicalSize);
          addTearDown(tester.view.resetDevicePixelRatio);
          addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
          var calls = 0;
          final api = ApiClient(
            base: Uri.parse('http://localhost:8016'),
            client: MockClient((_) async {
              calls++;
              return http.Response(jsonEncode({}), 500);
            }),
          );
          final session = Session(api);
          addTearDown(api.close);
          addTearDown(session.dispose);
          const key = Key('report-detail-capture');
          await tester.pumpWidget(
            RepaintBoundary(
              key: key,
              child: MaterialApp(
                theme: lpnTheme(),
                debugShowCheckedModeBanner: false,
                home: ReportDetailScreen(
                  api: RescueApi(api, session),
                  report: AnimalReport(
                    id: 12,
                    type: 'Animal en riesgo',
                    status: accepted ? 'Aceptado' : 'Pendiente',
                    city: 'Riohacha',
                    description: 'Un perro necesita apoyo cerca del parque. Está consciente y busca refugio.',
                    rescueCase: accepted
                        ? const RescueCase(
                            8,
                            'En proceso',
                            'Organización de ejemplo',
                          )
                        : null,
                  ),
                ),
              ),
            ),
          );
          await tester.pumpAndSettle();
          expect(
            find.text(accepted ? 'Aceptado' : 'Pendiente'),
            findsOneWidget,
          );
          expect(find.text('Riohacha'), findsOneWidget);
          final vertical = find.byWidgetPredicate(
            (w) => w is Scrollable && w.axisDirection == AxisDirection.down,
          );
          expect(vertical, findsOneWidget);
          final action = find.widgetWithText(
            FilledButton,
            'Apadrinar este caso',
          );
          expect(action, accepted ? findsOneWidget : findsNothing);
          if (accepted) expect(action.hitTestable(), findsOneWidget);
          if (!enlarged && directory.isNotEmpty) {
            await expectLater(
              find.byKey(key),
              matchesGoldenFile(
                Uri.file(
                  '$directory/detalle-${accepted ? 'aceptado' : 'pendiente'}.png',
                ),
              ),
            );
          }
          await tester.scrollUntilVisible(
            find.text('Seguimiento del rescate'),
            180,
            scrollable: vertical,
          );
          if (accepted) {
            await tester.scrollUntilVisible(
              find.text('En proceso'),
              100,
              scrollable: vertical,
            );
            expect(
              find.text('Aceptado por Organización de ejemplo'),
              findsOneWidget,
            );
            expect(action.hitTestable(), findsOneWidget);
          } else {
            expect(
              find.textContaining('Aún sin organización asignada'),
              findsOneWidget,
            );
          }
          expect(calls, 0);
          expect(tester.takeException(), isNull);
        },
      );
    }
  }
}
