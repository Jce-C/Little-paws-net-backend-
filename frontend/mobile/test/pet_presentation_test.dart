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

Map<String, dynamic> editorial() => {
  'descripcion': 'Disfruta los paseos tranquilos.',
  'cuidados': 'Necesita alimentación específica publicada por su fundación.',
  'espacio': 'Zona segura de descanso sin escaleras.',
};
Map<String, dynamic> row() => {
  'id_mascota': 2,
  'nombre': 'Luna QA',
  'especie': 'Perro',
  'presentacion': editorial(),
  'organizacion': 'Fundación QA',
  'ciudad': 'Riohacha',
  'custodia_desde': '2026-11-18T12:00:00Z',
  'edad_estimada': true,
};

void main() {
  testWidgets('Mixed catalog descriptions keep detail actions aligned', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(430, 1000);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient(
        (request) async => http.Response(
          jsonEncode({
            'results': [
              row(),
              {
                ...row(),
                'id_mascota': 3,
                'nombre': 'Ficha sin descripción',
                'presentacion': null,
              },
            ],
            'species': ['Perro'],
            'next': null,
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
        theme: lpnTheme(),
        home: Scaffold(
          body: CatalogScreen(
            api: AdoptionApi(client, session),
            session: session,
            onRequested: () {},
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    final actions = find.text('Ver detalles');
    expect(actions, findsNWidgets(2));
    expect(
      (tester.getRect(actions.at(0)).bottom -
              tester.getRect(actions.at(1)).bottom)
          .abs(),
      lessThan(.1),
    );
    expect(tester.takeException(), isNull);
  });
  test(
    'Public editorial fields are bounded and legacy records stay compatible',
    () {
      final pet = Pet.fromJson(row());
      expect(pet.description, editorial()['descripcion']);
      expect(pet.presentation!.care, editorial()['cuidados']);
      expect(Pet.fromJson(row()..remove('presentacion')).presentation, isNull);
      expect(
        PetPresentation.fromJson({...editorial(), 'descripcion': '🐾' * 1000})!
            .description
            .runes
            .length,
        1000,
      );
      for (final field in [
        ('descripcion', 1000),
        ('cuidados', 2000),
        ('espacio', 600),
      ]) {
        for (final invalid in [42, 'x' * (field.$2 + 1)]) {
          expect(
            () => PetPresentation.fromJson({...editorial(), field.$1: invalid}),
            throwsA(isA<ApiException>()),
          );
        }
      }
      expect(
        () => PetPresentation.fromJson({...editorial(), 'descripcion': ''}),
        throwsA(isA<ApiException>()),
      );
    },
  );

  testWidgets(
    'Detail shows published description and individual care with one GET only',
    (tester) async {
      final paths = <String>[];
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          paths.add('${request.method} ${request.url.path}');
          return http.Response(
            jsonEncode(row()),
            200,
            headers: {'content-type': 'application/json; charset=utf-8'},
          );
        }),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: PetScreen(
            pet: Pet.fromJson(row()),
            api: AdoptionApi(client, session),
            session: session,
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text(editorial()['descripcion']),
        160,
        scrollable: find
            .byWidgetPredicate(
              (w) => w is Scrollable && w.axisDirection == AxisDirection.down,
            )
            .first,
      );
      expect(find.text(editorial()['descripcion']), findsOneWidget);
      await tester.scrollUntilVisible(
        find.text(editorial()['cuidados']),
        160,
        scrollable: find
            .byWidgetPredicate(
              (w) => w is Scrollable && w.axisDirection == AxisDirection.down,
            )
            .first,
      );
      expect(find.text(editorial()['cuidados']), findsOneWidget);
      expect(find.text('Solicitar adopción').hitTestable(), findsOneWidget);
      expect(paths, ['GET /api/adopcion/mascotas/2/']);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'Request repeats individual care and keeps submit visible with enlarged text',
    (tester) async {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      var calls = 0;
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          if (request.url.path == '/api/auth/token/' ||
              request.url.path == '/api/auth/perfil/') {
            return http.Response(
              jsonEncode(
                request.url.path == '/api/auth/token/'
                    ? {'access': 'synthetic', 'refresh': 'synthetic-refresh'}
                    : {'nombre': 'Persona QA', 'email': 'qa@example.invalid'},
              ),
              200,
              headers: {'content-type': 'application/json; charset=utf-8'},
            );
          }
          calls++;
          throw StateError('No request until explicit submission');
        }),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await session.restore();
      await session.login('qa@example.invalid', 'synthetic', remember: false);
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: RequestDialog(
            pet: Pet.fromJson(row()),
            api: AdoptionApi(client, session),
            fullPage: true,
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text(editorial()['cuidados']),
        240,
        scrollable: find
            .byWidgetPredicate(
              (w) => w is Scrollable && w.axisDirection == AxisDirection.down,
            )
            .first,
      );
      expect(find.text(editorial()['cuidados']), findsOneWidget);
      expect(find.text('Enviar solicitud').hitTestable(), findsOneWidget);
      expect(calls, 0);
      expect(tester.takeException(), isNull);
    },
  );
}
