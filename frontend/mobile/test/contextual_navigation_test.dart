import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_navigation.dart';
import 'package:little_paws_net/main.dart';

void main() {
  testWidgets('The elevated action stays tappable above a genuine cut-out', (
    tester,
  ) async {
    var actions = 0;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          bottomNavigationBar: LpnNavigation(
            selected: 2,
            onSelected: (_) {},
            onPrimary: () => actions++,
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    final action = find.byKey(const Key('navigation-primary'));
    final capsule = find.byKey(const Key('navigation-capsule'));
    final button = tester.getRect(action), bar = tester.getRect(capsule);
    expect(button.top, lessThan(bar.top));
    expect(button.bottom, greaterThan(bar.top));
    expect(button.size.shortestSide, greaterThanOrEqualTo(48));
    final clipper = tester.widget<ClipPath>(capsule).clipper!;
    final path = clipper.getClip(bar.size);
    expect(path.contains(Offset(bar.width / 2, 8)), isFalse);
    expect(path.contains(Offset(bar.width / 2, bar.height - 4)), isTrue);
    expect(find.byTooltip('Nueva solicitud de adopción'), findsOneWidget);
    await tester.tapAt(Offset(button.center.dx, button.top + 8));
    expect(actions, 1);
  });

  testWidgets(
    'Plus opens animal selection without submitting; dog opens report form',
    (tester) async {
      final requests = <http.Request>[];
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          requests.add(request);
          return http.Response(
            jsonEncode({'results': [], 'next': null, 'species': []}),
            200,
            headers: {'content-type': 'application/json'},
          );
        }),
      );
      await tester.pumpWidget(LittlePawsApp(api: api, showWelcome: false));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Solicitudes'));
      await tester.pumpAndSettle();
      expect(find.byTooltip('Nueva solicitud de adopción'), findsOneWidget);
      await tester.tap(find.byKey(const Key('navigation-primary')));
      await tester.pumpAndSettle();
      expect(find.text('ADOPTAR'), findsOneWidget);
      expect(requests.where((request) => request.method != 'GET'), isEmpty);
      await tester.tap(find.byKey(const Key('navigation-primary')));
      await tester.pumpAndSettle();
      expect(find.byTooltip('Crear reporte'), findsNothing);
      expect(find.text('Reportar un animal'), findsWidgets);
      expect(requests.where((request) => request.method != 'GET'), isEmpty);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );
}
