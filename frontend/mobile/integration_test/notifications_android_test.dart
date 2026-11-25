import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:little_paws_net/adoption/adoption_screens.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/main.dart';

import 'adoption_android_test.dart' show waitFor;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
    'Android abre su bandeja y conserva la lectura después de actualizar',
    (tester) async {
      const base = String.fromEnvironment('LPN_API_BASE_URL');
      const email = String.fromEnvironment('LPN_QA_CITIZEN');
      const password = String.fromEnvironment('LPN_QA_PASSWORD');
      const marker = String.fromEnvironment('LPN_QA_NOTIFICATION');
      if (!base.startsWith('http://10.0.2.2:') ||
          !email.endsWith('@example.invalid') ||
          password.isEmpty ||
          !marker.startsWith('Aviso sintético QA')) {
        fail('Prepara únicamente un aviso de prueba en QA local aislado.');
      }
      await tester.pumpWidget(
        LittlePawsApp(
          showWelcome: false,
          api: ApiClient(base: Uri.parse(base)),
        ),
      );
      await waitFor(tester, find.byType(PetPlaceholder));
      await tester.tap(find.text('Mi cuenta'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Iniciar sesión'));
      await tester.pumpAndSettle();
      await tester.enterText(find.byKey(const Key('account-email')), email);
      await tester.enterText(
        find.byKey(const Key('account-password')),
        password,
      );
      await tester.ensureVisible(find.byKey(const Key('account-submit')));
      await tester.tap(find.byKey(const Key('account-submit')));
      await waitFor(tester, find.text(email));
      await tester.tap(find.byTooltip('Notificaciones'));
      await waitFor(tester, find.text(marker));
      final card = find.ancestor(
        of: find.text(marker),
        matching: find.byType(Card),
      );
      final mark = find.descendant(
        of: card,
        matching: find.text('Marcar como leída'),
      );
      await tester.ensureVisible(mark);
      await tester.tap(mark);
      await waitFor(
        tester,
        find.descendant(of: card, matching: find.text('Leída')),
      );
      await tester.ensureVisible(find.byTooltip('Actualizar notificaciones'));
      await tester.tap(find.byTooltip('Actualizar notificaciones'));
      await waitFor(
        tester,
        find.descendant(of: card, matching: find.text('Leída')),
      );
      await tester.tap(find.text('Solo sin leer'));
      await tester.pumpAndSettle();
      expect(find.text(marker), findsNothing);
    },
  );
}
