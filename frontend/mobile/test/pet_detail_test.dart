import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/adoption/adoption_screens.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

Map<String, Object?> detail() => {
  'id_mascota': 2,
  'nombre': 'Luna',
  'especie': 'Perro',
  'raza': null,
  'edad_meses': 25,
  'edad_estimada': true,
  'tamano': 'Mediano',
  'sexo': null,
  'organizacion': 'Fundacion Patitas QA',
  'ciudad': 'Riohacha',
  'custodia_desde': '2026-11-18T12:00:00Z',
};

void main() {
  testWidgets(
    'Story uses verified custody without inventing medical or rescue events',
    (tester) async {
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient(
          (_) async => http.Response(jsonEncode(detail()), 200),
        ),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: PetScreen(
            pet: const Pet(id: 2, name: 'Luna', species: 'Perro'),
            api: AdoptionApi(client, session),
            session: session,
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text('Disponible para adopción'),
        160,
      );
      expect(find.text('Fundacion Patitas QA'), findsOneWidget);
      expect(find.text('Ciudad: Riohacha'), findsOneWidget);
      expect(find.textContaining('Vacunado'), findsNothing);
      expect(find.textContaining('Esterilizado'), findsNothing);
      expect(find.textContaining('Reportado en la calle'), findsNothing);
      expect(find.text('Ver Expediente y QR'), findsNothing);
      expect(find.text('Solicitar adopción').hitTestable(), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('Long public custody values remain readable with enlarged text', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(320, 640);
    tester.view.devicePixelRatio = 1;
    tester.platformDispatcher.textScaleFactorTestValue = 2;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    const organization =
        'Organización de segundas oportunidades y protección animal de La Guajira';
    final client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient(
        (_) async => http.Response(
          jsonEncode({
            ...detail(),
            'organizacion': organization,
            'edad_meses': null,
            'tamano': null,
          }),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        ),
      ),
    );
    final session = Session(client);
    addTearDown(client.close);
    addTearDown(session.dispose);
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(reduceTransparency: true),
        home: PetScreen(
          pet: const Pet(id: 2, name: 'Luna', species: 'Perro'),
          api: AdoptionApi(client, session),
          session: session,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(find.text(organization), 160);
    expect(tester.widget<Text>(find.text(organization)).maxLines, isNull);
    expect(find.text('Solicitar adopción').hitTestable(), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets(
    'Refresh removes request action when pet is no longer available',
    (tester) async {
      var unavailable = false;
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          expect(request.url.path, '/api/adopcion/mascotas/2/');
          return http.Response(
            jsonEncode(unavailable ? {} : detail()),
            unavailable ? 404 : 200,
          );
        }),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await tester.pumpWidget(
        MaterialApp(
          home: PetScreen(
            pet: const Pet(id: 2, name: 'Luna', species: 'Perro'),
            api: AdoptionApi(client, session),
            session: session,
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Solicitar adopción'), findsOneWidget);
      unavailable = true;
      await tester.tap(find.byTooltip('Actualizar ficha'));
      await tester.pumpAndSettle();
      expect(
        find.text('Esta mascota ya no está disponible para adopción.'),
        findsOneWidget,
      );
      expect(find.text('Solicitar adopción'), findsNothing);
      expect(find.text('Fundacion Patitas QA'), findsNothing);
    },
  );

  testWidgets(
    'Public facts and request action fit narrow screens with 200% text',
    (tester) async {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient(
          (_) async => http.Response(jsonEncode(detail()), 200),
        ),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await tester.pumpWidget(
        MaterialApp(
          home: PetScreen(
            pet: const Pet(id: 2, name: 'Luna', species: 'Perro'),
            api: AdoptionApi(client, session),
            session: session,
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text('Fundacion Patitas QA'),
        150,
        scrollable: find
            .byWidgetPredicate(
              (widget) =>
                  widget is Scrollable &&
                  widget.axisDirection == AxisDirection.down,
            )
            .first,
      );
      expect(find.text('Fundacion Patitas QA'), findsOneWidget);
      expect(find.text('Solicitar adopción').hitTestable(), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  test('Public detail distinguishes unknown and estimated ages', () {
    expect(PetDetail.fromJson(detail()).ageLabel, '2 años y 1 mes (aprox.)');
    expect(
      PetDetail.fromJson({...detail(), 'edad_meses': null}).ageLabel,
      'Sin registrar',
    );
    expect(
      () => PetDetail.fromJson({...detail(), 'edad_meses': -1}),
      throwsA(isA<ApiException>()),
    );
  });

  test(
    'Unnamed rescued pets do not break the catalog or receive a fake identity',
    () {
      expect(
        Pet.fromJson({'id_mascota': 2, 'nombre': '', 'especie': 'Perro'}).name,
        'Sin nombre registrado',
      );
    },
  );
}
