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
    'Edita perfil propio y restaura los datos sintéticos en Android',
    (tester) async {
      const base = String.fromEnvironment('LPN_API_BASE_URL');
      const email = String.fromEnvironment('LPN_QA_CITIZEN');
      const password = String.fromEnvironment('LPN_QA_PASSWORD');
      if (base != 'http://10.0.2.2:8016' ||
          !email.endsWith('@example.invalid') ||
          password.isEmpty) {
        fail('Usa únicamente el escenario sintético local de QA.');
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
      await waitFor(tester, find.text('Editar perfil'));
      await tester.tap(find.text('Editar perfil'));
      await tester.pumpAndSettle();
      final originalName = tester
          .widget<TextFormField>(find.byKey(const Key('profile-name')))
          .controller!
          .text;
      final originalPhone = tester
          .widget<TextFormField>(find.byKey(const Key('profile-phone')))
          .controller!
          .text;
      await tester.enterText(
        find.byKey(const Key('profile-name')),
        'Perfil Android QA',
      );
      await tester.enterText(
        find.byKey(const Key('profile-phone')),
        '3000000000',
      );
      await tester.pumpAndSettle();
      await waitFor(
        tester,
        find.byKey(const Key('profile-save')).hitTestable(),
      );
      await tester.tap(find.byKey(const Key('profile-save')).hitTestable());
      await waitFor(tester, find.text('Editar perfil'));
      expect(find.text('Perfil Android QA'), findsOneWidget);
      expect(find.text('3000000000'), findsOneWidget);
      await tester.tap(find.text('Editar perfil'));
      await tester.pumpAndSettle();
      expect(
        tester
            .widget<TextFormField>(find.byKey(const Key('profile-name')))
            .controller!
            .text,
        'Perfil Android QA',
      );
      await tester.enterText(
        find.byKey(const Key('profile-name')),
        originalName,
      );
      await tester.enterText(
        find.byKey(const Key('profile-phone')),
        originalPhone,
      );
      await tester.pumpAndSettle();
      await waitFor(
        tester,
        find.byKey(const Key('profile-save')).hitTestable(),
      );
      await tester.tap(find.byKey(const Key('profile-save')).hitTestable());
      await waitFor(tester, find.text('Editar perfil'));
      expect(find.text(originalName), findsOneWidget);
    },
  );
}
