import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/pets/owned_pets_api.dart';
import 'package:little_paws_net/pets/owned_pets_screens.dart';

http.Response json(Object value, {int status = 200}) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

void main() {
  for (final medical in [false, true]) {
    testWidgets(
      '${medical ? 'Record' : 'Owned list'} coalesces refresh and allows explicit recovery',
      (tester) async {
        var reads = 0;
        final paths = <String>[];
        var pending = Completer<http.Response>();
        final client = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((request) async {
            switch (request.url.path) {
              case '/api/auth/token/':
                return json({
                  'access': 'synthetic',
                  'refresh': 'synthetic-refresh',
                });
              case '/api/auth/perfil/':
                return json({
                  'nombre': 'Persona QA',
                  'email': 'qa@example.invalid',
                });
              default:
                paths.add(request.url.path);
                reads++;
                return pending.future;
            }
          }),
        );
        final session = Session(client);
        addTearDown(() {
          session.dispose();
          client.close();
        });
        await session.restore();
        await session.login('qa@example.invalid', 'synthetic-password');
        final api = OwnedPetsApi(client, session);
        await tester.pumpWidget(
          MaterialApp(
            home: medical
                ? PetMedicalRecordScreen(api: api, petId: 8)
                : OwnedPetsScreen(api: api),
          ),
        );
        await tester.pump();
        final tooltip = medical
            ? 'Actualizar expediente'
            : 'Actualizar mis mascotas';
        IconButton refreshButton() => tester.widget<IconButton>(
          find.byWidgetPredicate(
            (widget) => widget is IconButton && widget.tooltip == tooltip,
          ),
        );
        Future<void> refresh() => tester
            .widget<RefreshIndicator>(find.byType(RefreshIndicator))
            .onRefresh();
        Object payload() => medical
            ? {
                'id': 8,
                'nombre': 'Mascota QA',
                'atenciones_recientes_maximo_50': [],
              }
            : [
                {
                  'id_mascota': 8,
                  'nombre': 'Mascota QA',
                  'especie': 'Perro',
                  'raza': null,
                  'estado': 'Con dueño',
                  'custodia_vigente': false,
                },
              ];

        expect(reads, 1);
        expect(refreshButton().onPressed, isNull);
        final initial = [refresh(), refresh(), refresh()];
        await tester.pump();
        expect(reads, 1);
        pending.complete(json(payload()));
        await Future.wait(initial);
        await tester.pumpAndSettle();
        expect(refreshButton().onPressed, isNotNull);
        expect(find.text('Mascota QA'), findsOneWidget);

        pending = Completer<http.Response>();
        final repeat = [refresh(), refresh()];
        await tester.pump();
        expect(reads, 2);
        expect(refreshButton().onPressed, isNull);
        expect(find.text('Mascota QA'), findsNothing);
        pending.complete(json({}, status: 503));
        await Future.wait(repeat);
        await tester.pumpAndSettle();
        await tester.pump(const Duration(seconds: 2));
        expect(reads, 2);
        expect(find.text('Reintentar'), findsOneWidget);
        expect(refreshButton().onPressed, isNotNull);

        pending = Completer<http.Response>();
        await tester.tap(find.text('Reintentar'));
        await tester.pump();
        expect(reads, 3);
        pending.complete(json(payload()));
        await tester.pumpAndSettle();
        expect(find.text('Mascota QA'), findsOneWidget);
        expect(tester.takeException(), isNull);
        expect(
          paths,
          List.filled(
            3,
            medical
                ? '/api/seguridad/operaciones/registros/expediente/8/'
                : '/api/mascotas/mias/',
          ),
        );
      },
    );
  }
}
