import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/design/lpn_app_bar.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

void main() {
  for (final title in [
    'Notificaciones',
    'Cambio confirmado',
    'QR de la mascota',
  ]) {
    testWidgets('$title stays readable at 200 percent and preserves back', (
      tester,
    ) async {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Builder(
            builder: (context) => Scaffold(
              body: TextButton(
                child: const Text('Abrir'),
                onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (context) => Scaffold(
                      appBar: lpnAppBar(context, title),
                      body: const Center(
                        child: Text('Contenido de la pantalla'),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      );
      await tester.tap(find.text('Abrir'));
      await tester.pumpAndSettle();
      final paragraph = tester.renderObject<RenderParagraph>(find.text(title));
      expect(paragraph.didExceedMaxLines, isFalse);
      final titleRect = tester.getRect(find.text(title));
      final barRect = tester.getRect(find.byType(AppBar));
      expect(titleRect.top, greaterThanOrEqualTo(barRect.top));
      expect(titleRect.bottom, lessThanOrEqualTo(barRect.bottom));
      expect(tester.takeException(), isNull);
      await tester.tap(find.byType(BackButton));
      await tester.pumpAndSettle();
      expect(find.text('Abrir'), findsOneWidget);
    });
  }

  testWidgets('Long pet title leaves refresh and content usable in landscape', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(640, 320);
    tester.view.devicePixelRatio = 1;
    tester.platformDispatcher.textScaleFactorTestValue = 2;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    var refreshed = 0;
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        home: Builder(
          builder: (context) => Scaffold(
            appBar: lpnAppBar(
              context,
              'Conoce a ${'Nombre de mascota ' * 10}',
              actions: [
                IconButton(
                  tooltip: 'Actualizar ficha',
                  onPressed: () => refreshed++,
                  icon: const Icon(Icons.refresh),
                ),
              ],
            ),
            body: const Center(child: Text('Ficha disponible')),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byTooltip('Actualizar ficha'));
    expect(refreshed, 1);
    expect(find.text('Ficha disponible').hitTestable(), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
