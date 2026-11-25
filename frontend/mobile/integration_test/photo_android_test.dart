import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/main.dart';
import 'package:little_paws_net/adoption/public_pet_image.dart';

import 'adoption_android_test.dart' show waitFor;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
    'Android decodifica foto pública autorizada en catálogo y ficha QA',
    (tester) async {
      const base = String.fromEnvironment('LPN_API_BASE_URL');
      if (base != 'http://10.0.2.2:8016') {
        fail('Usa solo el escenario QA local.');
      }
      await tester.pumpWidget(
        LittlePawsApp(
          showWelcome: false,
          api: ApiClient(base: Uri.parse(base)),
        ),
      );
      await waitFor(tester, find.widgetWithText(ChoiceChip, 'QA Foto'));
      await tester.tap(find.widgetWithText(ChoiceChip, 'QA Foto'));
      final decoded = find.descendant(
        of: find.byType(PublicPetImage),
        matching: find.byWidgetPredicate(
          (widget) => widget is RawImage && widget.image != null,
        ),
      );
      await waitFor(tester, decoded);
      expect(find.byTooltip('Reintentar fotografía'), findsNothing);
      await tester.tap(find.text('QA Foto Publica'));
      await waitFor(tester, decoded);
      expect(
        tester.widget<RawImage>(decoded.first).image!.width,
        greaterThan(0),
      );
      expect(
        tester.widget<RawImage>(decoded.first).image!.width,
        lessThanOrEqualTo(1280),
      );
      expect(find.byTooltip('Reintentar fotografía'), findsNothing);
      expect(find.text('Foto pública aún no disponible'), findsNothing);
      final image = find.descendant(
        of: find.byType(PublicPetImage),
        matching: find.byType(Image),
      );
      expect(tester.widget<Image>(image.first).fit, BoxFit.contain);
      expect(tester.takeException(), isNull);
    },
  );
}
