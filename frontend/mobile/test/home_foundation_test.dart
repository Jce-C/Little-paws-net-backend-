import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/design/refined_surfaces.dart';
import 'package:little_paws_net/design/organic_surface.dart';

void main() {
  testWidgets('Home image scrolls with its header over one continuous canvas', (
    tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        home: Scaffold(
          body: HomeBackdrop(
            child: ListView(
              children: const [IntegratedHomeHeader(), SizedBox(height: 900)],
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    final header = find.byKey(const Key('integrated-home-header'));
    expect(
      find.descendant(of: header, matching: find.byType(Image)),
      findsOneWidget,
    );
    final pictures = find.byType(Image);
    expect(pictures, findsOneWidget);
    expect(
      tester.getRect(pictures.last).bottom,
      lessThanOrEqualTo(
        tester.getTopLeft(find.text('TU RED DE PROTECCIÓN ANIMAL')).dy,
      ),
      reason:
          'The illustration fade must finish before the reading area starts',
    );
    final before = tester.getRect(pictures.first);
    await tester.drag(find.byType(ListView), const Offset(0, -200));
    await tester.pumpAndSettle();
    expect(tester.getRect(pictures.first).top, lessThan(before.top));
    expect(tester.takeException(), isNull);
  });
  for (final solid in [false, true]) {
    testWidgets('Shared surfaces honor transparency preference: $solid', (
      tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(reduceTransparency: solid),
          home: Scaffold(
            body: HomeBackdrop(
              child: ListView(
                children: [
                  const FormCard(child: Text('Contenido legible')),
                  FeatureDeck(
                    children: [
                      FeatureRow(
                        icon: Icons.pets,
                        title: 'Adoptar',
                        subtitle: 'Mascotas',
                        onTap: () {},
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      final card = tester.widget<Container>(
        find
            .descendant(
              of: find.byType(FormCard),
              matching: find.byType(Container),
            )
            .first,
      );
      final decoration = card.decoration! as BoxDecoration;
      expect(decoration.gradient == null, solid);
      expect(decoration.boxShadow == null, solid);
      final images = find.byType(Image);
      expect(images, findsNothing);
      expect(tester.takeException(), isNull);
    });
  }
}
