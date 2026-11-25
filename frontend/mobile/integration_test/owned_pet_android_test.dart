import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:little_paws_net/adoption/adoption_screens.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/main.dart';
import 'package:qr_flutter/qr_flutter.dart';

import 'adoption_android_test.dart' show waitFor;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets(
    'La mascota adoptada abre expediente privado y genera un QR válido en Android',
    (tester) async {
      const base = String.fromEnvironment('LPN_API_BASE_URL');
      const email = String.fromEnvironment('LPN_QA_CITIZEN');
      const password = String.fromEnvironment('LPN_QA_PASSWORD');
      const petName = String.fromEnvironment('LPN_QA_PET_NAME');
      const petId = int.fromEnvironment('LPN_QA_PET_ID');
      if (base != 'http://10.0.2.2:8016' ||
          !email.endsWith('@example.invalid') ||
          password.isEmpty ||
          petName.isEmpty ||
          petId <= 0) {
        fail('Usa el escenario local después de aprobar su adopción.');
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
      await waitFor(tester, find.text('Mis mascotas'));
      await tester.tap(find.text('Mis mascotas'));
      await waitFor(tester, find.text(petName));
      final record = find.byKey(Key('pet-record-$petId'));
      await tester.ensureVisible(record);
      await tester.tap(record);
      await waitFor(
        tester,
        find.text(
          'Todavía no hay atenciones médicas registradas para esta mascota.',
        ),
      );
      await tester.ensureVisible(find.text('QR de identificación'));
      await tester.tap(find.text('QR de identificación'));
      await tester.pumpAndSettle();
      expect(find.byType(QrImageView), findsNothing);
      await tester.ensureVisible(find.text('Generar QR'));
      await tester.tap(find.text('Generar QR'));
      await waitFor(tester, find.byType(QrImageView));
      expect(find.text('Generar otro QR'), findsOneWidget);
      await tester.tap(find.byType(BackButton).last);
      await tester.pumpAndSettle();
      expect(find.text(petName), findsOneWidget);
      expect(find.text('Expediente privado'), findsOneWidget);
      await tester.tap(find.byTooltip('Actualizar expediente'));
      await waitFor(
        tester,
        find.text(
          'Todavía no hay atenciones médicas registradas para esta mascota.',
        ),
      );
    },
  );
}
