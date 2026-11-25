import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/design/catalog_hero.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

void main() {
  testWidgets('Heading, count and filters remain outside the illustration', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(393, 852);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        home: Scaffold(
          body: SingleChildScrollView(
            child: CatalogHero(
              species: const ['Perro', 'Gato'],
              selected: '',
              counter: '24 cargados',
              onSelected: (_) {},
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    final title = tester.getRect(find.text('ADOPTAR'));
    final counter = tester.getRect(find.text('24 cargados'));
    expect(title.left, 20);
    expect(title.overlaps(counter), isFalse);
    final hero = tester.getRect(find.byKey(const Key('catalog-hero')));
    expect(hero.contains(tester.getCenter(find.text('Perro'))), isFalse);
    expect(counter.bottom, lessThanOrEqualTo(hero.top));
    expect(tester.takeException(), isNull);
  });

  testWidgets('Selecting the active filter does not request it again', (
    tester,
  ) async {
    final changes = <String>[];
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        home: Scaffold(
          body: SingleChildScrollView(
            child: CatalogHero(
              species: const ['Perro', 'Gato'],
              selected: 'Perro',
              onSelected: changes.add,
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Perro'));
    expect(changes, isEmpty);
    await tester.tap(find.text('Gato'));
    expect(changes, ['Gato']);
  });

  testWidgets('Enlarged text stacks count and keeps long species reachable', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(320, 640);
    tester.view.devicePixelRatio = 1;
    tester.platformDispatcher.textScaleFactorTestValue = 2;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    final changes = <String>[];
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        home: Scaffold(
          body: SingleChildScrollView(
            child: CatalogHero(
              species: const ['Perro', 'Gato', 'Animales de compañía'],
              selected: '',
              counter: '24 resultados disponibles',
              onSelected: changes.add,
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(
      tester.getRect(find.text('24 resultados disponibles')).top,
      greaterThanOrEqualTo(tester.getRect(find.text('ADOPTAR')).bottom),
    );
    await tester.ensureVisible(find.text('Animales de compañía'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Animales de compañía'));
    expect(changes, ['Animales de compañía']);
    expect(tester.takeException(), isNull);
  });
}
