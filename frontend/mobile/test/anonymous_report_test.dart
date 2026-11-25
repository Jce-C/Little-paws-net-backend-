import 'dart:convert';
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/rescue/anonymous_report_screen.dart';
import 'package:little_paws_net/rescue/rescue_api.dart';

void main() {
  testWidgets(
    'Saves anonymous changes without a bearer token and hides the key on success',
    (tester) async {
      var calls = 0;
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          calls++;
          expect(request.url.path, '/api/reportes/12/gestion-anonima/');
          expect(request.headers['authorization'], isNull);
          expect(jsonDecode(request.body), {
            'codigo_gestion': 'clave-sintetica-QA',
            'cerrar': false,
            'descripcion': 'Descripción corregida QA',
          });
          return http.Response(
            jsonEncode({'id_reporte': 12, 'estado': 'Pendiente'}),
            200,
          );
        }),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await tester.pumpWidget(
        MaterialApp(
          home: AnonymousReportScreen(
            api: RescueApi(client, session),
            reportId: 12,
            privateCode: 'clave-sintetica-QA',
          ),
        ),
      );
      await tester.pumpAndSettle();
      final secretField = find.descendant(
        of: find.byKey(const Key('anonymous-report-code')),
        matching: find.byType(TextField),
      );
      expect(tester.widget<TextField>(secretField).obscureText, isTrue);
      await tester.scrollUntilVisible(
        find.byKey(const Key('anonymous-report-description')),
        150,
        scrollable: find
            .byWidgetPredicate(
              (widget) =>
                  widget is Scrollable &&
                  widget.axisDirection == AxisDirection.down,
            )
            .first,
      );
      await tester.enterText(
        find.byKey(const Key('anonymous-report-description')),
        'Descripción corregida QA',
      );
      await tester.tap(find.byKey(const Key('anonymous-report-save')));
      await tester.pumpAndSettle();
      expect(find.text('Cambio confirmado'), findsOneWidget);
      expect(find.text('Estado: Pendiente'), findsOneWidget);
      expect(find.text('clave-sintetica-QA'), findsNothing);
      expect(calls, 1);
    },
  );

  testWidgets(
    'Cancel preserves the draft until discard is confirmed and sends no request',
    (tester) async {
      var calls = 0;
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((_) async {
          calls++;
          return http.Response('{}', 500);
        }),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (context) => Scaffold(
              body: TextButton(
                onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => AnonymousReportScreen(
                      api: RescueApi(client, session),
                      reportId: 12,
                      privateCode: 'qa-secret',
                    ),
                  ),
                ),
                child: const Text('Abrir editor'),
              ),
            ),
          ),
        ),
      );
      await tester.tap(find.text('Abrir editor'));
      await tester.pumpAndSettle();
      final field = find.byKey(const Key('anonymous-report-description'));
      await tester.scrollUntilVisible(
        field,
        150,
        scrollable: find
            .byWidgetPredicate(
              (w) => w is Scrollable && w.axisDirection == AxisDirection.down,
            )
            .first,
      );
      await tester.enterText(field, 'Borrador que no debe enviarse');
      await tester.tap(find.byKey(const Key('anonymous-report-cancel')));
      await tester.pumpAndSettle();
      expect(find.text('¿Descartar los cambios?'), findsOneWidget);
      await tester.tap(find.text('Seguir editando'));
      await tester.pumpAndSettle();
      expect(find.text('Borrador que no debe enviarse'), findsOneWidget);
      await tester.tap(find.byKey(const Key('anonymous-report-cancel')));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Descartar cambios'));
      await tester.pumpAndSettle();
      expect(find.text('Abrir editor'), findsOneWidget);
      expect(calls, 0);
    },
  );

  testWidgets('Closing requires confirmation and cancelling does not submit', (
    tester,
  ) async {
    var calls = 0;
    final client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        calls++;
        expect(jsonDecode(request.body), {
          'codigo_gestion': 'clave-sintetica-QA',
          'cerrar': true,
        });
        return http.Response(
          jsonEncode({'id_reporte': 12, 'estado': 'Cerrado'}),
          200,
        );
      }),
    );
    final session = Session(client);
    addTearDown(client.close);
    addTearDown(session.dispose);
    await tester.pumpWidget(
      MaterialApp(
        home: AnonymousReportScreen(
          api: RescueApi(client, session),
          reportId: 12,
          privateCode: 'clave-sintetica-QA',
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('anonymous-report-close')));
    await tester.pumpAndSettle();
    await tester.tap(
      find.descendant(
        of: find.byType(AlertDialog),
        matching: find.text('Cancelar'),
      ),
    );
    await tester.pumpAndSettle();
    expect(calls, 0);
    await tester.tap(find.byKey(const Key('anonymous-report-close')));
    await tester.pumpAndSettle();
    await tester.tap(find.widgetWithText(FilledButton, 'Cerrar reporte'));
    await tester.pumpAndSettle();
    expect(calls, 1);
    expect(find.text('Estado: Cerrado'), findsOneWidget);
  });

  testWidgets(
    'Wrong key preserves the form and explains how to correct access',
    (tester) async {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((_) async => http.Response('{}', 403)),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await tester.pumpWidget(
        MaterialApp(
          home: AnonymousReportScreen(
            api: RescueApi(client, session),
            reportId: 12,
            privateCode: 'clave-invalida-QA',
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.byKey(const Key('anonymous-report-description')),
        150,
        scrollable: find
            .byWidgetPredicate(
              (widget) =>
                  widget is Scrollable &&
                  widget.axisDirection == AxisDirection.down,
            )
            .first,
      );
      await tester.enterText(
        find.byKey(const Key('anonymous-report-description')),
        'Cambio de prueba',
      );
      await tester.tap(find.byKey(const Key('anonymous-report-save')));
      await tester.pumpAndSettle();
      expect(
        find.text('Revisa el número de reporte y la clave privada.'),
        findsOneWidget,
      );
      expect(find.byKey(const Key('anonymous-report-save')), findsOneWidget);
      expect(find.text('Cambio confirmado'), findsNothing);
    },
  );
  test(
    'Private contact is removed only through the explicit clear option',
    () async {
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          expect(jsonDecode(request.body), {
            'codigo_gestion': 'clave-sintetica-QA',
            'cerrar': false,
            'contacto_reportante': '',
          });
          return http.Response(
            jsonEncode({'id_reporte': 12, 'estado': 'Pendiente'}),
            200,
          );
        }),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await RescueApi(client, session).manageAnonymous(
        reportId: 12,
        code: 'clave-sintetica-QA',
        clearContact: true,
      );
    },
  );
  testWidgets(
    'Lost edit response preserves draft and blocks duplicate submissions',
    (tester) async {
      var calls = 0;
      final pending = Completer<http.Response>();
      final client = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) {
          calls++;
          return pending.future;
        }),
      );
      final session = Session(client);
      addTearDown(client.close);
      addTearDown(session.dispose);
      await tester.pumpWidget(
        MaterialApp(
          home: AnonymousReportScreen(
            api: RescueApi(client, session),
            reportId: 12,
            privateCode: 'qa-synthetic',
          ),
        ),
      );
      final field = find.byKey(const Key('anonymous-report-description'));
      await tester.ensureVisible(field);
      await tester.enterText(field, 'Borrador que permanece');
      final save = find.byKey(const Key('anonymous-report-save'));
      await tester.tap(save);
      await tester.pump();
      expect(tester.widget<FilledButton>(save).onPressed, isNull);
      expect(calls, 1);
      pending.complete(http.Response('{}', 503));
      await tester.pumpAndSettle();
      expect(find.text('Verifica el cambio'), findsOneWidget);
      await tester.tap(find.widgetWithText(TextButton, 'Cerrar'));
      await tester.pumpAndSettle();
      expect(find.text('Borrador que permanece'), findsOneWidget);
      expect(tester.widget<FilledButton>(save).onPressed, isNull);
      expect(calls, 1);
      expect(find.text('Cambio confirmado'), findsNothing);
    },
  );
}
