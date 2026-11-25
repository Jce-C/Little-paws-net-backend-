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
    'Android envía un reporte y consulta su seguimiento privado en Django QA',
    (tester) async {
      const base = String.fromEnvironment('LPN_API_BASE_URL');
      const email = String.fromEnvironment('LPN_QA_CITIZEN');
      const password = String.fromEnvironment('LPN_QA_PASSWORD');
      if (!base.startsWith('http://10.0.2.2:') ||
          !email.endsWith('@example.invalid') ||
          password.isEmpty) {
        fail('Utiliza exclusivamente el escenario sintético local.');
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
      await tester.tap(find.text('Rescates'));
      await waitFor(tester, find.text('Reportar un animal'));
      await tester.ensureVisible(find.text('Reportar un animal'));
      await tester.tap(find.text('Reportar un animal'));
      await waitFor(tester, find.byKey(const Key('report-type')));

      await tester.pumpAndSettle();
      await tester.tap(find.text('Animal encontrado').last);
      await tester.pumpAndSettle();
      final marker =
          'Reporte Android QA ${DateTime.now().millisecondsSinceEpoch}';
      await tester.scrollUntilVisible(
        find.byKey(const Key('report-description')),
        140,
        scrollable: find
            .byWidgetPredicate(
              (widget) =>
                  widget is Scrollable &&
                  widget.axisDirection == AxisDirection.down,
            )
            .first,
      );
      await tester.pumpAndSettle();
      await tester.enterText(
        find.byKey(const Key('report-description')),
        marker,
      );
      await tester.tap(find.byKey(const Key('report-next')));
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.byKey(const Key('report-city')),
        140,
        scrollable: find
            .byWidgetPredicate(
              (widget) =>
                  widget is Scrollable &&
                  widget.axisDirection == AxisDirection.down,
            )
            .first,
      );
      await tester.pumpAndSettle();
      await tester.enterText(find.byKey(const Key('report-city')), 'Riohacha');
      await waitFor(tester, find.text('RIOHACHA, LA GUAJIRA'));
      await tester.tap(find.text('RIOHACHA, LA GUAJIRA').last);
      await tester.pumpAndSettle();
      for (final field in {
        'report-neighborhood': 'Sector sintético QA',
        'report-address': 'Referencia ficticia QA',
      }.entries) {
        await tester.scrollUntilVisible(
          find.byKey(Key(field.key)),
          150,
          scrollable: find
              .byWidgetPredicate(
                (widget) =>
                    widget is Scrollable &&
                    widget.axisDirection == AxisDirection.down,
              )
              .first,
        );
        await tester.enterText(find.byKey(Key(field.key)), field.value);
      }
      await tester.tap(find.byKey(const Key('report-next')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('report-submit')));
      await waitFor(tester, find.text('¡Reporte enviado!'));
      expect(find.text('Copiar clave privada'), findsNothing);
      await tester.ensureVisible(find.text('Ver mis reportes'));
      await tester.tap(find.text('Ver mis reportes'));
      await waitFor(tester, find.textContaining(marker));
      await tester.tap(find.textContaining(marker));
      await tester.pumpAndSettle();
      expect(find.text(marker), findsOneWidget);
      expect(find.text('RIOHACHA'), findsOneWidget);
      expect(find.text('Pendiente'), findsOneWidget);
    },
  );
}
