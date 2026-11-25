import 'dart:convert';
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/notifications/notifications_api.dart';
import 'package:little_paws_net/notifications/notifications_screen.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/adoption/adoption_screens.dart';

http.Response json(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);
Map<String, dynamic> notice(int id, {int? destination, String? read}) => {
  'id_notificacion': id,
  'contenido': 'Tu solicitud de Luna fue revisada.',
  'tipo': 'Resultado de adopción',
  'fecha_creacion': '2026-11-24T15:00:00Z',
  'fecha_lectura': read,
  'destino': destination == null
      ? null
      : {'tipo': 'solicitud_adopcion', 'id': destination},
};
Map<String, dynamic> request(String state) => {
  'id_solicitud_adopcion': 7,
  'mascota__nombre': 'Luna',
  'estado_adopcion__nombre': state,
  'fecha_solicitud': '2026-11-24T12:00:00Z',
  'historial': <Object>[],
};
void main() {
  const directory = String.fromEnvironment('LPN_VISUAL_QA_DIR');
  setUpAll(() async {
    for (final font in {
      'Inter': 'assets/fonts/Inter.ttf',
      'MaterialIcons': 'fonts/MaterialIcons-Regular.otf',
    }.entries) {
      await (FontLoader(font.key)..addFont(rootBundle.load(font.value))).load();
    }
  });
  late ApiClient api;
  late Session session;
  late Future<http.Response> Function(http.Request) respond;
  setUp(() async {
    api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((r) async {
        if (r.url.path == '/api/auth/token/') {
          return json({'access': 'qa', 'refresh': 'qa-refresh'});
        }
        if (r.url.path == '/api/auth/perfil/') {
          return json({'nombre': 'Persona QA', 'email': 'qa@example.invalid'});
        }
        return respond(r);
      }),
    );
    session = Session(api);
    await session.restore();
    await session.login('qa@example.invalid', 'synthetic', remember: false);
  });
  tearDown(() {
    session.dispose();
    api.close();
  });
  Future<void> open(WidgetTester tester, Widget child) async {
    tester.view.physicalSize = const Size(393, 852);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      RepaintBoundary(
        key: const Key('inbox-capture'),
        child: MaterialApp(
          theme: lpnTheme(),
          locale: const Locale('es'),
          supportedLocales: const [Locale('es')],
          localizationsDelegates: GlobalMaterialLocalizations.delegates,
          debugShowCheckedModeBanner: false,
          home: Scaffold(body: child),
        ),
      ),
    );
    await tester.pumpAndSettle();
  }

  Future<void> capture(WidgetTester tester, String name) async {
    if (directory.isNotEmpty) {
      await expectLater(
        find.byKey(const Key('inbox-capture')),
        matchesGoldenFile(Uri.file('$directory/$name.png')),
      );
    }
  }

  testWidgets(
    'Destination opens exact request without marking it read and returns to refreshed inbox',
    (tester) async {
      var lists = 0, details = 0, marks = 0;
      respond = (r) async {
        if (r.url.path == '/api/notificaciones/') {
          lists++;
          return json({
            'results': [notice(4, destination: 7)],
            'next_cursor': null,
          });
        }
        if (r.url.path == '/api/adopcion/solicitudes/7/') {
          details++;
          return json(request('Aprobada'));
        }
        marks++;
        return json({});
      };
      await open(
        tester,
        NotificationsScreen(api: NotificationsApi(api, session)),
      );
      await capture(tester, '01-notificaciones');
      await tester.tap(find.byKey(const Key('notification-open-4')));
      await tester.pumpAndSettle();
      expect(find.text('Solicitud #7'), findsOneWidget);
      expect(find.text('Aprobada'), findsOneWidget);
      expect(details, 1);
      expect(marks, 0);
      await capture(tester, '02-detalle-solicitud');
      await tester.tap(find.byType(BackButton).last);
      await tester.pumpAndSettle();
      expect(lists, 2);
      expect(find.text('Sin leer'), findsOneWidget);
      expect(marks, 0);
    },
  );
  testWidgets(
    'Server read timestamp is used and repeated taps do not submit twice',
    (tester) async {
      var writes = 0;
      final pending = Completer<http.Response>();
      respond = (r) async {
        if (r.method == 'GET') {
          return json({
            'results': [notice(4)],
            'next_cursor': null,
          });
        }
        writes++;
        return pending.future;
      };
      await open(
        tester,
        NotificationsScreen(api: NotificationsApi(api, session)),
      );
      final button = find.byKey(const Key('notification-read-4'));
      await tester.tap(button);
      await tester.pump();
      expect(tester.widget<TextButton>(button).onPressed, isNull);
      expect(writes, 1);
      pending.complete(
        json({'leida': true, 'fecha_lectura': '2026-11-24T16:00:00Z'}),
      );
      await tester.pumpAndSettle();
      expect(find.text('Leída'), findsOneWidget);
      expect(writes, 1);
    },
  );
  testWidgets(
    'Unread filter remains usable with later pages and deduplicates notices',
    (tester) async {
      var calls = 0;
      respond = (r) async {
        calls++;
        return json(
          r.url.queryParameters['antes'] == null
              ? {
                  'results': [notice(4, read: '2026-11-24T16:00:00Z')],
                  'next_cursor': '4',
                }
              : {
                  'results': [
                    notice(4, read: '2026-11-24T16:00:00Z'),
                    notice(3),
                  ],
                  'next_cursor': null,
                },
        );
      };
      await open(
        tester,
        NotificationsScreen(api: NotificationsApi(api, session)),
      );
      await tester.tap(find.text('Solo sin leer'));
      await tester.pumpAndSettle();
      expect(
        find.text('No hay avisos sin leer en esta lista.'),
        findsOneWidget,
      );
      await tester.tap(find.text('Ver más avisos'));
      await tester.pumpAndSettle();
      expect(find.text('Sin leer'), findsOneWidget);
      expect(calls, 2);
      await tester.pump(const Duration(seconds: 20));
      expect(calls, 2);
    },
  );
  testWidgets('Request detail refresh and return update the visible list', (
    tester,
  ) async {
    var lists = 0, details = 0;
    respond = (r) async {
      if (r.url.path == '/api/adopcion/solicitudes/mias/') {
        lists++;
        return json({
          'results': [request(lists == 1 ? 'Pendiente' : 'Aprobada')],
          'next_cursor': null,
        });
      }
      details++;
      return json(request(details == 1 ? 'Pendiente' : 'Aprobada'));
    };
    await open(
      tester,
      RequestsScreen(api: AdoptionApi(api, session), session: session),
    );
    expect(find.text('Pendiente'), findsOneWidget);
    await capture(tester, '03-mis-solicitudes');
    await tester.tap(find.text('Luna'));
    await tester.pumpAndSettle();
    await tester.tap(find.byTooltip('Actualizar solicitud'));
    await tester.pumpAndSettle();
    expect(find.text('Aprobada'), findsOneWidget);
    expect(details, 2);
    await tester.tap(find.byType(BackButton).last);
    await tester.pumpAndSettle();
    expect(find.text('Aprobada'), findsOneWidget);
    expect(lists, 2);
  });
  test('Unknown destinations do not create arbitrary links and timestamps are verified', () async {
    expect(
      AccountNotification.fromJson({
        ...notice(4),
        'destino': {'tipo': 'https://other.invalid', 'id': 8},
      }).requestId,
      isNull,
    );
    respond = (_) async => json({'leida': true, 'fecha_lectura': 'invalid'});
    await expectLater(
      NotificationsApi(api, session).markRead(4),
      throwsA(isA<ApiException>()),
    );
  });
  testWidgets(
    'Notification destination still requires backend access and does not mark read on denial',
    (tester) async {
      var writes = 0;
      respond = (r) async {
        if (r.method == 'POST') {
          writes++;
          return json({});
        }
        if (r.url.path == '/api/notificaciones/') {
          return json({
            'results': [notice(4, destination: 7)],
            'next_cursor': null,
          });
        }
        return json({'detalle': 'No disponible'}, 403);
      };
      await open(
        tester,
        NotificationsScreen(api: NotificationsApi(api, session)),
      );
      await tester.tap(find.byKey(const Key('notification-open-4')));
      await tester.pumpAndSettle();
      expect(find.text('Aprobada'), findsNothing);
      expect(find.text('Luna'), findsNothing);
      expect(writes, 0);
      expect(find.text('Reintentar'), findsOneWidget);
    },
  );
  testWidgets('Inbox actions fit at 320px with 200 percent text', (
    tester,
  ) async {
    respond = (_) async => json({
      'results': [notice(4, destination: 7)],
      'next_cursor': null,
    });
    await open(
      tester,
      NotificationsScreen(api: NotificationsApi(api, session)),
    );
    tester.view.physicalSize = const Size(320, 640);
    tester.platformDispatcher.textScaleFactorTestValue = 2;
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    await tester.pumpAndSettle();
    await tester.ensureVisible(find.byKey(const Key('notification-read-4')));
    await tester.pumpAndSettle();
    expect(
      find.byKey(const Key('notification-read-4')).hitTestable(),
      findsOneWidget,
    );
    expect(tester.takeException(), isNull);
  });
}
