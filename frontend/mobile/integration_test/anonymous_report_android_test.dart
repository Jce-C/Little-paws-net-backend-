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
    'Android corrige y cierra un reporte sintético con su clave privada',
    (tester) async {
      const base = String.fromEnvironment('LPN_API_BASE_URL');
      if (base != 'http://10.0.2.2:8016') {
        fail('Usa exclusivamente Django QA local.');
      }
      final qa = ApiClient(base: Uri.parse(base));
      addTearDown(qa.close);
      final options = await qa.get(
        '/api/reportes/opciones/?ciudad=Riohacha',
      ) as Map<String, dynamic>;
      final cities = options['ciudades'] as List<dynamic>;
      final types = options['tipos'] as List<dynamic>;
      final marker =
          'Gestión anónima Android QA ${DateTime.now().millisecondsSinceEpoch}';
      final created = await qa.post('/api/reportes/', {
        'tipo_reporte': (types.first as Map)['id_valor_maestro'],
        'ciudad_id': (cities.first as Map)['id_ciudad'],
        'barrio': 'Sector sintético QA',
        'direccion': 'Referencia ficticia QA',
        'descripcion': marker,
      }) as Map<String, dynamic>;
      final id = created['id_reporte'] as int;
      final code = created['codigo_gestion'] as String;
      await tester.pumpWidget(
        LittlePawsApp(
          showWelcome: false,
          api: ApiClient(base: Uri.parse(base)),
        ),
      );
      await waitFor(tester, find.byType(PetPlaceholder));
      await tester.tap(find.text('Rescates'));
      await waitFor(tester, find.text('Gestionar reporte anónimo'));
      await tester.ensureVisible(find.text('Gestionar reporte anónimo'));
      await tester.tap(find.text('Gestionar reporte anónimo'));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.byKey(const Key('anonymous-report-id')),
        '$id',
      );
      await tester.enterText(
        find.byKey(const Key('anonymous-report-code')),
        code,
      );
      await tester.ensureVisible(
        find.byKey(const Key('anonymous-report-description')),
      );
      await tester.enterText(
        find.byKey(const Key('anonymous-report-description')),
        '$marker corregido',
      );
      await tester.tap(find.byKey(const Key('anonymous-report-save')));
      await waitFor(tester, find.text('Cambio confirmado'));
      expect(find.text('Estado: Pendiente'), findsOneWidget);
      final publicRows = await qa.get(
        '/api/seguridad/operaciones/reportes-publicos/',
      ) as List<dynamic>;
      final updated = publicRows.cast<Map<String, dynamic>>().singleWhere(
        (row) => row['id_reporte'] == id,
      );
      expect(updated['descripcion'], '$marker corregido');
      await tester.tap(find.text('Volver a rescates'));
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.text('Gestionar reporte anónimo'));
      await tester.tap(find.text('Gestionar reporte anónimo'));
      await tester.pumpAndSettle();
      await tester.enterText(
        find.byKey(const Key('anonymous-report-id')),
        '$id',
      );
      await tester.enterText(
        find.byKey(const Key('anonymous-report-code')),
        code,
      );
      await tester.tap(find.byKey(const Key('anonymous-report-close')));
      await tester.pumpAndSettle();
      await tester.tap(find.widgetWithText(FilledButton, 'Cerrar reporte'));
      await waitFor(tester, find.text('Estado: Cerrado'));
      await expectLater(
        qa.post('/api/reportes/$id/gestion-anonima/', {
          'codigo_gestion': code,
          'descripcion': 'Cambio rechazado QA',
        }),
        throwsA(
          isA<ApiException>().having((error) => error.status, 'status', 409),
        ),
      );
    },
  );
}
