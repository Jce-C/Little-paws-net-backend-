import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:little_paws_net/main.dart';
import 'package:little_paws_net/core/api_client.dart';

import 'adoption_android_test.dart' show waitFor;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
    'Catálogo Android carga páginas y filtra en todo el catálogo QA',
    (tester) async {
      const base = String.fromEnvironment('LPN_API_BASE_URL');
      if (base != 'http://10.0.2.2:8016') fail('Usa exclusivamente QA local.');
      await tester.pumpWidget(
        LittlePawsApp(
          showWelcome: false,
          api: ApiClient(base: Uri.parse(base)),
        ),
      );
      await waitFor(tester, find.widgetWithText(ChoiceChip, 'QA Paginacion'));
      await tester.tap(find.widgetWithText(ChoiceChip, 'QA Paginacion'));
      await waitFor(tester, find.text('24 cargados'));
      await tester.scrollUntilVisible(
        find.text('Cargar más'),
        600,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.tap(find.text('Cargar más'));
      // The header is virtualized while the last page is at the bottom.
      tester
          .state<ScrollableState>(find.byType(Scrollable).first)
          .position
          .jumpTo(0);
      await waitFor(tester, find.text('27 resultados'));
      await tester.scrollUntilVisible(
        find.text('QA Pagina 26'),
        250,
        scrollable: find.byType(Scrollable).first,
      );
      expect(find.text('Cargar más'), findsNothing);
      expect(find.text('QA Pagina 26'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
}
