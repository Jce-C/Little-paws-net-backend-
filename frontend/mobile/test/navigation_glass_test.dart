import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/design/lpn_navigation.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

void main() {
  testWidgets(
    'Glass selection moves, preserves destinations and respects reduced effects',
    (tester) async {
      var selected = 0;
      var solid = false;
      var reduceMotion = false;
      late StateSetter change;
      await tester.pumpWidget(
        StatefulBuilder(
          builder: (context, update) {
            change = update;
            return MaterialApp(
              theme: lpnTheme(reduceTransparency: solid),
              home: MediaQuery(
                data: MediaQueryData(
                  size: const Size(390, 844),
                  disableAnimations: reduceMotion,
                ),
                child: Scaffold(
                  bottomNavigationBar: LpnNavigation(
                    selected: selected,
                    onSelected: (index) => update(() => selected = index),
                    onPrimary: () {},
                  ),
                ),
              ),
            );
          },
        ),
      );
      expect(find.byType(BackdropFilter), findsOneWidget);
      final selection = find.byKey(const Key('navigation-selection'));
      final start = tester.getTopLeft(selection);
      await tester.tap(find.byKey(const ValueKey('navigation-3')));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 130));
      final middle = tester.getTopLeft(selection);
      await tester.pumpAndSettle();
      final end = tester.getTopLeft(selection);
      expect(start.dx, lessThan(middle.dx));
      expect(middle.dx, lessThan(end.dx));
      expect(selected, 3);
      change(() {
        solid = true;
        reduceMotion = true;
      });
      await tester.pumpAndSettle();
      expect(find.byType(BackdropFilter), findsNothing);
      await tester.tap(find.byKey(const ValueKey('navigation-1')));
      await tester.pump();
      expect(
        tester.widget<AnimatedPositioned>(selection).duration,
        Duration.zero,
      );
      expect(selected, 1);
      expect(tester.takeException(), isNull);
    },
  );
}
