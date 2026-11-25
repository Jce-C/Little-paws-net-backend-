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

void main() {
  for (final scale in [1.0, 2.0]) {
    testWidgets('Catalog long names remain reachable and announced at $scale', (
      tester,
    ) async {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = scale;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      final semantics = tester.ensureSemantics();
      try {
        const names = [
          'Esperanza de las segundas oportunidades',
          'Compañero de la comunidad de Riohacha',
        ];
        var reads = 0;
        final api = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((request) async {
            expect(request.method, 'GET');
            expect(request.url.path, '/api/adopcion/catalogo/');
            reads++;
            return http.Response(
              jsonEncode({
                'next': null,
                'previous': null,
                'species': ['Perro'],
                'results': [
                  for (var index = 0; index < names.length; index++)
                    {
                      'id_mascota': index + 1,
                      'nombre': names[index],
                      'especie': 'Perro',
                      'raza': 'Criollo',
                    },
                ],
              }),
              200,
              headers: {'content-type': 'application/json; charset=utf-8'},
            );
          }),
        );
        final session = Session(api);
        addTearDown(session.dispose);
        addTearDown(api.close);
        await session.restore();
        await tester.pumpWidget(
          MaterialApp(
            theme: lpnTheme(),
            home: Scaffold(
              body: CatalogScreen(
                api: AdoptionApi(api, session),
                session: session,
                onRequested: () {},
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();
        final scroll = find
            .byWidgetPredicate(
              (widget) =>
                  widget is Scrollable &&
                  widget.axisDirection == AxisDirection.down,
            )
            .first;
        for (final name in names) {
          await tester.scrollUntilVisible(
            find.text(name),
            120,
            scrollable: scroll,
          );
          await tester.pumpAndSettle();
          expect(find.text(name).hitTestable(), findsOneWidget);
          final target = find.bySemanticsLabel('$name. Perro, Criollo');
          expect(target, findsOneWidget);
          expect(
            tester
                .getSemantics(target)
                .getSemanticsData()
                .flagsCollection
                .isButton,
            isTrue,
          );
          expect(tester.takeException(), isNull);
        }
        expect(reads, 1);
      } finally {
        semantics.dispose();
      }
    });
  }
}
