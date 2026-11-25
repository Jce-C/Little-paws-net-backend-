import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:little_paws_net/adoption/adoption_screens.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/main.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('Android solicita y el panel web decide sobre Django local', (
    tester,
  ) async {
    const base = String.fromEnvironment('LPN_API_BASE_URL');
    const email = String.fromEnvironment('LPN_QA_CITIZEN');
    const password = String.fromEnvironment('LPN_QA_PASSWORD');
    const petName = String.fromEnvironment('LPN_QA_PET_NAME');
    if (!base.startsWith('http://10.0.2.2:') ||
        email.isEmpty ||
        password.isEmpty ||
        petName.isEmpty) {
      fail('Prepara el escenario local y pasa las variables QA.');
    }

    final api = ApiClient(base: Uri.parse(base));
    final qa = ApiClient(base: Uri.parse(base));
    addTearDown(qa.close);
    await tester.pumpWidget(LittlePawsApp(showWelcome: false, api: api));
    await waitFor(tester, find.byType(PetPlaceholder));
    final catalog = find.byType(Scrollable).first;
    await tester.scrollUntilVisible(
      find.text(petName),
      240,
      scrollable: catalog,
    );
    await tester.tap(find.text(petName));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.text('Solicitar adopción'));
    await tester.tap(find.text('Solicitar adopción'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('account-email')), email);
    await tester.enterText(find.byKey(const Key('account-password')), password);
    await tester.ensureVisible(find.byKey(const Key('account-submit')));
    await tester.tap(find.byKey(const Key('account-submit')));
    await waitFor(tester, find.byKey(const Key('adoption-note')));
    await tester.enterText(
      find.byKey(const Key('adoption-note')),
      'Solicitud Android QA',
    );
    await tester.tap(find.text('Enviar solicitud'));
    await waitFor(tester, find.textContaining('· Pendiente'));
    final count = find.textContaining('· Pendiente');
    expect(count, findsOneWidget);

    final credentials = await qa.post('/api/auth/token/', {
      'email': email,
      'password': password,
    }) as Map<String, dynamic>;
    final started = DateTime.now();
    while (true) {
      final response = await qa.get(
        '/api/seguridad/operaciones/mis-registros/',
        token: credentials['access'] as String,
      ) as Map<String, dynamic>;
      final rows = response['adopciones'] as List<dynamic>;
      final row = rows.single as Map<String, dynamic>;
      if (row['estado_adopcion__nombre'] == 'Aprobada') break;
      if (DateTime.now().difference(started) > const Duration(seconds: 55)) {
        fail(
          'El panel no aprobó la solicitud. Estado: ${jsonEncode(row['estado_adopcion__nombre'])}',
        );
      }
      await tester.pump(const Duration(seconds: 2));
      await Future<void>.delayed(const Duration(seconds: 1));
    }
    await tester.tap(find.byTooltip('Actualizar solicitudes'));
    await waitFor(tester, find.textContaining('· Aprobada'));
    expect(find.text(petName), findsOneWidget);
  });
}

Future<void> waitFor(WidgetTester tester, Finder finder) async {
  final deadline = DateTime.now().add(const Duration(seconds: 20));
  while (finder.evaluate().isEmpty) {
    if (DateTime.now().isAfter(deadline)) {
      fail('El elemento esperado no apareció en Android.');
    }
    await tester.pump(const Duration(milliseconds: 120));
    await Future<void>.delayed(const Duration(milliseconds: 80));
  }
  await tester.pumpAndSettle();
}
