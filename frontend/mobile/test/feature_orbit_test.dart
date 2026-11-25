import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/design/organic_surface.dart';

void main() {
  for (final width in [280.0, 320.0, 412.0, 720.0]) {
    testWidgets('Feature arrows remain centered in their orbit at $width', (
      tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: SizedBox(
                width: width,
                child: FeatureDeck(
                  children: [
                    FeatureRow(
                      icon: Icons.pets,
                      title: 'Adopción',
                      subtitle: 'Mascotas disponibles',
                      onTap: () {},
                    ),
                    FeatureRow(
                      icon: Icons.shield,
                      title: 'Mi espacio',
                      subtitle: 'Datos personales',
                      onTap: () {},
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      for (final title in ['Adopción', 'Mi espacio']) {
        final circle = find.byKey(ValueKey('feature-orbit-$title'));
        final arrow = find.descendant(
          of: circle,
          matching: find.byIcon(Icons.north_east_rounded),
        );
        expect(arrow, findsOneWidget);
        expect(
          (tester.getCenter(circle) - tester.getCenter(arrow)).distance,
          lessThan(.01),
        );
      }
      expect(tester.takeException(), isNull);
    });
  }
}
