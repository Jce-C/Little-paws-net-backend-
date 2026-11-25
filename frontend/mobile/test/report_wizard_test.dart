import 'dart:convert';
import 'dart:async';

import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:little_paws_net/design/photo_attachment.dart';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/rescue/rescue_api.dart';
import 'package:little_paws_net/rescue/rescue_screens.dart';

void main() {
  const visualDirectory = String.fromEnvironment('LPN_VISUAL_QA_DIR');
  setUpAll(() async {
    if (visualDirectory.isNotEmpty) {
      for (final font in {
        'Inter': 'assets/fonts/Inter.ttf',
        'MaterialIcons': 'fonts/MaterialIcons-Regular.otf',
      }.entries) {
        await (FontLoader(
          font.key,
        )..addFont(rootBundle.load(font.value))).load();
      }
    }
  });
  late ApiClient api;
  late Session session;
  var reads = 0, posts = 0;
  String loginEmail = 'qa@example.invalid';
  ReportReceipt? returned;
  late Future<http.Response> Function(http.Request) respond;
  http.Response json(Object value, [int status = 200]) => http.Response(
    jsonEncode(value),
    status,
    headers: {'content-type': 'application/json; charset=utf-8'},
  );
  setUp(() async {
    reads = 0;
    posts = 0;
    returned = null;
    respond = (_) async => http.Response('{}', 503);
    api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((r) async {
        if (r.url.path == '/api/auth/token/') {
          loginEmail = (jsonDecode(r.body) as Map)['email'] as String;
          return json({'access': 'qa-token', 'refresh': 'qa-refresh'});
        }
        if (r.url.path == '/api/auth/perfil/') {
          return json({'nombre': 'Persona QA', 'email': loginEmail});
        }
        if (r.url.path == '/api/auth/token/revoke/') return json({});
        if (r.method == 'POST') {
          posts++;
          return respond(r);
        }
        reads++;
        return http.Response(
          jsonEncode({
            'tipos': [
              {'id_valor_maestro': 1, 'nombre': 'Rescate'},
            ],
            'ciudades': [
              {
                'id_ciudad': 7,
                'nombre': 'Riohacha',
                'departamento': 'La Guajira',
              },
            ],
          }),
          200,
          headers: {'content-type': 'application/json; charset=utf-8'},
        );
      }),
    );
    session = Session(api);
    await session.restore();
  });
  tearDown(() {
    session.dispose();
    api.close();
  });
  Future<void> open(
    WidgetTester tester, {
    Future<Uint8List?> Function(ImageSource)? choosePhoto,
  }) async {
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        debugShowCheckedModeBanner: false,
        home: Builder(
          builder: (context) => Scaffold(
            body: TextButton(
              onPressed: () async {
                returned = await Navigator.of(context).push<ReportReceipt>(
                  MaterialPageRoute(
                    builder: (_) => RepaintBoundary(
                      key: const Key('creation-capture'),
                      child: ReportFormScreen(
                        api: RescueApi(api, session),
                        choosePhoto: choosePhoto,
                      ),
                    ),
                  ),
                );
              },
              child: const Text('Abrir reporte'),
            ),
          ),
        ),
      ),
    );
    await tester.tap(find.text('Abrir reporte'));
    await tester.pumpAndSettle();
  }

  Future<void> visible(WidgetTester tester, Finder finder) async {
    if (finder.evaluate().isEmpty) {
      await tester.scrollUntilVisible(
        finder,
        160,
        scrollable: find
            .byWidgetPredicate(
              (widget) =>
                  widget is Scrollable &&
                  widget.axisDirection == AxisDirection.down,
            )
            .first,
      );
    } else {
      await tester.ensureVisible(finder);
    }
    await tester.pumpAndSettle();
  }

  Future<void> next(WidgetTester tester) async {
    await tester.tap(find.byKey(const Key('report-next')));
    await tester.pumpAndSettle();
  }

  Future<void> capture(
    WidgetTester tester,
    String name, {
    bool top = true,
  }) async {
    if (visualDirectory.isEmpty) return;
    tester.testTextInput.hide();
    if (top) {
      tester
          .state<ScrollableState>(
            find
                .byWidgetPredicate(
                  (w) =>
                      w is Scrollable && w.axisDirection == AxisDirection.down,
                )
                .first,
          )
          .position
          .jumpTo(0);
    }
    await tester.pumpAndSettle();
    await expectLater(
      find.byKey(const Key('creation-capture')),
      matchesGoldenFile(Uri.file('$visualDirectory/$name.png')),
    );
  }

  Future<void> location(WidgetTester tester, {bool snapshots = false}) async {
    await visible(tester, find.text('Rescate'));
    await tester.tap(find.text('Rescate'));
    await visible(tester, find.byKey(const Key('report-description')));
    await tester.enterText(
      find.byKey(const Key('report-description')),
      'Animal que necesita ayuda en el parque.',
    );
    if (snapshots) await capture(tester, '01-situacion');
    await next(tester);
    await visible(tester, find.byKey(const Key('report-city')));
    await tester.enterText(find.byKey(const Key('report-city')), 'Rio');
    await tester.pump(const Duration(milliseconds: 400));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Riohacha, La Guajira').last);
    await tester.pumpAndSettle();
    for (final entry in {
      'report-neighborhood': 'Barrio QA',
      'report-address': 'Parque QA',
    }.entries) {
      await visible(tester, find.byKey(Key(entry.key)));
      await tester.pumpAndSettle();
      await tester.enterText(find.byKey(Key(entry.key)), entry.value);
    }
  }

  testWidgets('Steps validate locally and retain fields when returning', (
    tester,
  ) async {
    await open(tester);
    await next(tester);
    expect(find.text('Selecciona la situación.'), findsOneWidget);
    expect(find.byKey(const Key('report-city')), findsNothing);
    expect(posts, 0);
    await location(tester);
    await next(tester);
    expect(find.byKey(const Key('report-contact')), findsOneWidget);
    expect(posts, 0);
    await tester.tap(find.byKey(const Key('report-previous')));
    await tester.pumpAndSettle();
    expect(
      tester
          .widget<TextFormField>(find.byKey(const Key('report-city')))
          .controller!
          .text,
      'Riohacha, La Guajira',
    );
    await tester.tap(find.byKey(const Key('report-previous')));
    await tester.pumpAndSettle();
    expect(
      tester
          .widget<TextFormField>(find.byKey(const Key('report-description')))
          .controller!
          .text,
      'Animal que necesita ayuda en el parque.',
    );
    expect(
      tester
          .widget<ChoiceChip>(find.widgetWithText(ChoiceChip, 'Rescate'))
          .selected,
      isTrue,
    );
    expect(reads, 2);
    expect(posts, 0);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox.shrink());
  });
  testWidgets('Discard confirmation keeps a draft until confirmed', (
    tester,
  ) async {
    await open(tester);
    await tester.enterText(
      find.byKey(const Key('report-description')),
      'Borrador QA',
    );
    await tester.pageBack();
    await tester.pumpAndSettle();
    expect(find.text('¿Descartar este reporte?'), findsOneWidget);
    await tester.tap(find.text('Seguir editando'));
    await tester.pumpAndSettle();
    expect(find.text('Borrador QA'), findsOneWidget);
    await tester.pageBack();
    await tester.pumpAndSettle();
    await tester.tap(find.text('Descartar'));
    await tester.pumpAndSettle();
    expect(find.text('Abrir reporte'), findsOneWidget);
    expect(posts, 0);
    expect(tester.takeException(), isNull);
  });
  testWidgets('Uncertain final submission blocks accidental duplicates', (
    tester,
  ) async {
    await open(tester);
    await location(tester);
    await next(tester);
    await tester.tap(find.byKey(const Key('report-submit')));
    await tester.pumpAndSettle();
    expect(posts, 1);
    final button = tester.widget<FilledButton>(
      find.byKey(const Key('report-submit')),
    );
    expect(button.onPressed, isNull);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox.shrink());
  });
  testWidgets(
    'Photo survives steps, requires explicit consent and uploads once',
    (tester) async {
      if (visualDirectory.isNotEmpty) {
        tester.view.physicalSize = const Size(393, 852);
        tester.view.devicePixelRatio = 1;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);
      }
      final bytes = (await rootBundle.load('assets/access/login-pets.webp'))
          .buffer
          .asUint8List();
      final pending = Completer<http.Response>();
      respond = (request) {
        expect(
          request.headers['content-type'],
          contains('multipart/form-data'),
        );
        final body = latin1.decode(request.bodyBytes);
        expect(body, contains('confirmar_foto_publica'));
        expect(
          body,
          contains('foto.webp'),
        ); // The server validates and normalizes the image bytes.
        return pending.future;
      };
      await open(tester, choosePhoto: (_) async => bytes);
      await visible(tester, find.text('Seleccionar de galería'));
      await tester.tap(find.text('Seleccionar de galería'));
      await tester.pumpAndSettle();
      expect(
        tester.widget<PhotoAttachment>(find.byType(PhotoAttachment)).value,
        bytes,
      );
      await location(tester, snapshots: true);
      await capture(tester, '02-ubicacion');
      await next(tester);
      final consent = find.byKey(const Key('report-photo-consent'));
      await capture(tester, '03-revision');
      await visible(tester, consent);
      await tester.pumpAndSettle();
      expect(tester.widget<CheckboxListTile>(consent).value, isFalse);
      expect(
        tester
            .widget<FilledButton>(find.byKey(const Key('report-submit')))
            .onPressed,
        isNull,
      );
      await tester.tap(
        find.descendant(of: consent, matching: find.byType(Checkbox)),
      );
      await tester.pumpAndSettle();
      await capture(tester, '04-confirmacion-foto', top: false);
      await tester.tap(find.byKey(const Key('report-previous')));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('report-previous')));
      await tester.pumpAndSettle();
      await visible(tester, find.byType(PhotoAttachment));
      expect(
        tester.widget<PhotoAttachment>(find.byType(PhotoAttachment)).value,
        bytes,
      );
      await next(tester);
      await next(tester);
      await visible(tester, consent);
      expect(tester.widget<CheckboxListTile>(consent).value, isTrue);
      await tester.tap(find.byKey(const Key('report-submit')));
      await tester.pump();
      expect(posts, 1);
      expect(
        tester
            .widget<FilledButton>(find.byKey(const Key('report-submit')))
            .onPressed,
        isNull,
      );
      pending.complete(
        json({
          'id_reporte': 91,
          'estado': 'Pendiente',
          'codigo_gestion': 'synthetic-once',
        }, 201),
      );
      for (var frame = 0; frame < 20 && returned == null; frame++) {
        await tester.pump(const Duration(milliseconds: 50));
      }
      await tester.pumpAndSettle();
      expect(
        returned,
        isNotNull,
        reason: find
            .byType(Text)
            .evaluate()
            .map((e) => (e.widget as Text).data)
            .join(' | '),
      );
      expect(returned!.id, 91);
      expect(returned!.privateCode, 'synthetic-once');
      expect(posts, 1);
      expect(reads, 2);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'Cancel is available from review, keeps the draft until confirmed',
    (tester) async {
      await open(tester);
      await location(tester);
      await visible(tester, find.byKey(const Key('report-directions')));
      await tester.enterText(
        find.byKey(const Key('report-directions')),
        'Frente al parque QA',
      );
      await next(tester);
      expect(find.text('Frente al parque QA'), findsOneWidget);
      await tester.tap(find.byKey(const Key('report-cancel')));
      await tester.pumpAndSettle();
      expect(find.text('¿Descartar este reporte?'), findsOneWidget);
      await tester.tap(find.text('Seguir editando'));
      await tester.pumpAndSettle();
      expect(find.text('Frente al parque QA'), findsOneWidget);
      await tester.tap(find.byKey(const Key('report-cancel')));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Descartar'));
      await tester.pumpAndSettle();
      expect(find.text('Abrir reporte'), findsOneWidget);
      expect(posts, 0);
    },
  );

  testWidgets(
    'An account boundary destroys the draft and ignores a late result',
    (tester) async {
      final pending = Completer<http.Response>();
      respond = (_) => pending.future;
      await open(tester);
      await location(tester);
      await next(tester);
      await visible(tester, find.byKey(const Key('report-contact')));
      await tester.enterText(
        find.byKey(const Key('report-contact')),
        'contacto-ficticio.invalid',
      );
      await tester.tap(find.byKey(const Key('report-submit')));
      await tester.pump();
      expect(posts, 1);
      await session.login('otra@example.invalid', 'synthetic', remember: false);
      await tester.pumpAndSettle();
      expect(find.textContaining('La sesión cambió.'), findsOneWidget);
      expect(find.text('contacto-ficticio.invalid'), findsNothing);
      pending.complete(
        json({
          'id_reporte': 93,
          'estado': 'Pendiente',
          'codigo_gestion': 'old-receipt',
        }, 201),
      );
      await tester.pumpAndSettle();
      expect(returned, isNull);
      expect(find.textContaining('La sesión cambió.'), findsOneWidget);
      expect(find.text('old-receipt'), findsNothing);
      expect(posts, 1);
    },
  );

  test(
    'Photo upload without confirmation is rejected before any request',
    () async {
      await expectLater(
        RescueApi(api, session).create(
          type: 1,
          city: 7,
          neighborhood: 'Sector',
          address: 'Referencia',
          description: 'Situación',
          photo: Uint8List.fromList([1, 2]),
        ),
        throwsA(isA<ApiException>()),
      );
      expect(posts, 0);
      expect(reads, 0);
    },
  );
  testWidgets('City typing is debounced and normal navigation does not poll', (
    tester,
  ) async {
    await open(tester);
    await tester.tap(find.text('Rescate'));
    await tester.enterText(
      find.byKey(const Key('report-description')),
      'Situación QA',
    );
    await next(tester);
    for (final value in ['R', 'Ri', 'Rio', 'Rioh']) {
      await tester.enterText(find.byKey(const Key('report-city')), value);
      await tester.pump(const Duration(milliseconds: 80));
    }
    await tester.pump(const Duration(milliseconds: 400));
    await tester.pumpAndSettle();
    expect(reads, 2);
    expect(posts, 0);
    await tester.pump(const Duration(seconds: 10));
    expect(reads, 2);
    expect(posts, 0);
  });

  testWidgets(
    'All three steps keep actions reachable at 320px and 200 percent text',
    (tester) async {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      await open(tester);
      await location(tester);
      await next(tester);
      expect(
        find.byKey(const Key('report-cancel')).hitTestable(),
        findsOneWidget,
      );
      expect(
        find.byKey(const Key('report-submit')).hitTestable(),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
      expect(posts, 0);
    },
  );
  testWidgets(
    'A photo picker response cannot restore a draft after an identity change',
    (tester) async {
      final pending = Completer<Uint8List?>();
      await open(tester, choosePhoto: (_) => pending.future);
      await visible(tester, find.text('Seleccionar de galería'));
      await tester.tap(find.text('Seleccionar de galería'));
      await tester.pump();
      await session.login('otra@example.invalid', 'synthetic', remember: false);
      await tester.pumpAndSettle();
      expect(find.textContaining('La sesión cambió.'), findsOneWidget);
      await tester.tap(find.text('Salir del formulario'));
      await tester.pumpAndSettle();
      expect(find.text('Abrir reporte'), findsOneWidget);
      pending.complete(Uint8List.fromList([1, 2, 3]));
      await tester.pumpAndSettle();
      expect(find.text('Abrir reporte'), findsOneWidget);
      expect(find.byType(PhotoAttachment), findsNothing);
      expect(posts, 0);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets(
    'An uncertain signed-in request offers verification without retry',
    (tester) async {
      await session.login(
        'cuenta@example.invalid',
        'synthetic',
        remember: false,
      );
      await open(tester);
      await location(tester);
      await next(tester);
      await tester.tap(find.byKey(const Key('report-submit')));
      await tester.pumpAndSettle();
      expect(find.text('Verifica el envío'), findsOneWidget);
      await tester.tap(find.widgetWithText(TextButton, 'Cerrar'));
      await tester.pumpAndSettle();
      expect(
        find.byKey(const Key('report-check-own')).hitTestable(),
        findsOneWidget,
      );
      expect(
        tester
            .widget<FilledButton>(find.byKey(const Key('report-submit')))
            .onPressed,
        isNull,
      );
      expect(posts, 1);
    },
  );
}
