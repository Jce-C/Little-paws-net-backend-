import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:little_paws_net/adoption/adoption_screens.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/main.dart';

import 'adoption_android_test.dart' show waitFor;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('Bienvenida, acceso directo y materiales accesibles en Android', (
    tester,
  ) async {
    const base = String.fromEnvironment('LPN_API_BASE_URL');
    if (base != 'http://10.0.2.2:8016') fail('Usa el backend QA local.');
    await tester.pumpWidget(
      LittlePawsApp(api: ApiClient(base: Uri.parse(base))),
    );
    await tester.pumpAndSettle();
    expect(
      tester
          .widget<Scaffold>(find.byKey(const Key('welcome-screen')))
          .backgroundColor,
      const Color(0xfffcf0d3),
    );
    await tester.ensureVisible(find.text('Iniciar sesión'));
    await tester.tap(find.text('Iniciar sesión'));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('account-email')), findsOneWidget);
    expect(
      Theme.of(tester.element(find.byKey(const Key('account-email'))))
          .scaffoldBackgroundColor,
      const Color(0xfffff9ec),
    );
    await tester.tap(find.byType(BackButton));
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.byKey(const Key('welcome-explore')));
    await tester.tap(find.byKey(const Key('welcome-explore')));
    await waitFor(tester, find.byType(PetPlaceholder));
    expect(find.byType(BackdropFilter), findsWidgets);
    await tester.tap(find.byTooltip('Apariencia'));
    await tester.pumpAndSettle();
    await tester.tap(find.byType(CheckedPopupMenuItem<String>));
    await tester.pumpAndSettle();
    expect(find.byType(BackdropFilter), findsNothing);
    await tester.tap(find.byTooltip('Apariencia'));
    await tester.pumpAndSettle();
    await tester.tap(find.byType(CheckedPopupMenuItem<String>));
    await tester.pumpAndSettle();
    expect(find.byType(BackdropFilter), findsWidgets);
    await tester.tap(find.text('Mi cuenta'));
    await tester.pumpAndSettle();
    expect(find.text('Iniciar sesión'), findsOneWidget);
  });
}
