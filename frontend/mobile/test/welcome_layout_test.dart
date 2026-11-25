import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_navigation.dart';
import 'package:little_paws_net/main.dart';

void main() {
  setUpAll(() async {
    final loader = FontLoader('Inter')
      ..addFont(rootBundle.load('assets/fonts/Inter.ttf'));
    await loader.load();
  });
  setUp(() => FlutterSecureStorage.setMockInitialValues({}));
  ApiClient api() => ApiClient(
    base: Uri.parse('https://example.invalid'),
    client: MockClient(
      (_) async => http.Response(
        jsonEncode({'results': [], 'next': null, 'species': []}),
        200,
        headers: {'content-type': 'application/json'},
      ),
    ),
  );

  for (final size in [const Size(320, 560), const Size(390, 740)]) {
    testWidgets('Welcome fits and content follows the floating bar at $size', (
      tester,
    ) async {
      tester.view.physicalSize = size;
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await tester.pumpWidget(LittlePawsApp(api: api()));
      await tester.pumpAndSettle();
      for (final key in [
        'welcome-login',
        'welcome-explore',
        'welcome-register',
      ]) {
        expect(find.byKey(Key(key)).hitTestable(), findsOneWidget);
      }
      final welcome = tester.state<ScrollableState>(
        find.byType(Scrollable).first,
      );
      expect(welcome.position.maxScrollExtent, 0);
      await tester.tap(find.byKey(const Key('welcome-explore')));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Inicio'));
      await tester.pumpAndSettle();
      final list = find.byType(ListView).first;
      final bar = tester.getRect(find.byKey(const Key('navigation-capsule')));
      // The body must paint behind the capsule, not end at its rectangular top.
      expect(tester.getRect(list).bottom, greaterThan(bar.bottom));
      final state = tester.state<ScrollableState>(
        find.descendant(of: list, matching: find.byType(Scrollable)).first,
      );
      state.position.jumpTo(state.position.maxScrollExtent);
      await tester.pumpAndSettle();
      final last = find.text('Tienda');
      expect(last.hitTestable(), findsOneWidget);
      expect(
        tester.getRect(last).bottom,
        lessThan(tester.getRect(find.byType(LpnNavigation)).top),
      );
      final clipper = tester
          .widget<ClipPath>(find.byKey(const Key('navigation-capsule')))
          .clipper!;
      final shape = clipper.getClip(bar.size);
      for (final label in LpnNavigation.labels) {
        final rect = tester
            .getRect(
              find.descendant(
                of: find.byType(LpnNavigation),
                matching: find.text(label),
              ),
            )
            .shift(-bar.topLeft)
            .deflate(.5);
        for (final point in [
          rect.topLeft,
          rect.topRight,
          rect.bottomLeft,
          rect.bottomRight,
        ]) {
          expect(
            shape.contains(point),
            isTrue,
            reason: '$label must remain inside the capsule',
          );
        }
      }
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox.shrink());
    });
  }

  testWidgets(
    'Reduced motion keeps welcome usable immediately with large text',
    (tester) async {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      tester.platformDispatcher.accessibilityFeaturesTestValue =
          const FakeAccessibilityFeatures(disableAnimations: true);
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      addTearDown(
        tester.platformDispatcher.clearAccessibilityFeaturesTestValue,
      );
      await tester.pumpWidget(LittlePawsApp(api: api()));
      await tester.pumpAndSettle();
      final login = find.byKey(const Key('welcome-login'));
      await tester.ensureVisible(login);
      await tester.pumpAndSettle();
      await tester.tap(login);
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('account-email')), findsOneWidget);
      expect(tester.takeException(), isNull);
      await tester.pumpWidget(const SizedBox.shrink());
    },
  );
}
