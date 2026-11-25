import 'package:flutter/services.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/design/lpn_navigation.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

void main() {
  setUpAll(() async {
    final loader = FontLoader('Inter')
      ..addFont(rootBundle.load('assets/fonts/Inter.ttf'));
    await loader.load();
  });
  testWidgets('Navigation preserves all destinations and announces selection', (
    tester,
  ) async {
    final changes = <int>[];
    final semantics = tester.ensureSemantics();
    try {
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Scaffold(
            bottomNavigationBar: LpnNavigation(
              selected: 1,
              onSelected: changes.add,
              onPrimary: () {},
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(
        tester.getSemantics(find.bySemanticsLabel('Adoptar\nPestaña 2 de 4')),
        matchesSemantics(
          isButton: true,
          isSelected: true,
          hasSelectedState: true,
          hasTapAction: true,
          label: 'Adoptar\nPestaña 2 de 4',
          isFocusable: true,
        ),
      );
      await tester.tap(find.text('Adoptar'));
      expect(changes, isEmpty);
      for (final index in [0, 2, 3]) {
        await tester.tap(find.text(LpnNavigation.labels[index]));
      }
      expect(changes, [0, 2, 3]);
    } finally {
      semantics.dispose();
    }
  });

  for (final config in [
    (const Size(320, 640), 1.0),
    (const Size(320, 640), 2.0),
    (const Size(800, 360), 2.0),
  ]) {
    testWidgets('Four visible touch targets with safe area at $config', (
      tester,
    ) async {
      tester.view.physicalSize = config.$1;
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = config.$2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          builder: (context, child) => MediaQuery(
            data: MediaQuery.of(context)
                .copyWith(padding: const EdgeInsets.only(bottom: 24)),
            child: child!,
          ),
          home: Scaffold(
            bottomNavigationBar: LpnNavigation(
              selected: 1,
              onSelected: (_) {},
              onPrimary: () {},
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      for (var i = 0; i < 4; i++) {
        final target = find.byKey(ValueKey('navigation-$i'));
        final rect = tester.getRect(target);
        expect(target.hitTestable(), findsOneWidget);
        expect(rect.width, greaterThanOrEqualTo(48));
        expect(rect.height, greaterThanOrEqualTo(48));
        expect(rect.bottom, lessThanOrEqualTo(config.$1.height - 24));
        expect(
          tester.getRect(find.text(LpnNavigation.labels[i])).bottom,
          lessThanOrEqualTo(rect.bottom),
        );
      }
      if (config.$2 == 1) {
        expect(
          tester.getSize(find.byType(LpnNavigation)).height,
          lessThanOrEqualTo(148),
        );
        final logo = find.byType(SvgPicture);
        expect(tester.getCenter(logo).dx, closeTo(config.$1.width / 2, 1));
      }
      expect(tester.takeException(), isNull);
    });
  }
}
