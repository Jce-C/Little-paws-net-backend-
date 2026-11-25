import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/rescue/rescue_api.dart';
import 'package:little_paws_net/rescue/public_reports_controller.dart';
import 'package:little_paws_net/rescue/rescue_screens.dart';

Map<String, Object> row(int id, {String status = 'Pendiente'}) => {
  'id_reporte': id,
  'tipo_reporte__nombre': 'Rescate',
  'estado_reporte__nombre': status,
  'descripcion': 'Reporte sintético QA $id',
};
http.Response page(List<Object> rows, {String? next, int status = 200}) =>
    http.Response(
      jsonEncode({'results': rows, 'next_cursor': next}),
      status,
      headers: {'content-type': 'application/json; charset=utf-8'},
    );

void main() {
  late ApiClient client;
  late Session session;
  late PublicReportsController feed;
  late Future<http.Response> Function(http.Request) respond;
  late List<Uri> requests;
  setUp(() {
    requests = [];
    respond = (_) async => page([]);
    client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) {
        if (request.method != 'GET' ||
            request.url.path != '/api/reportes/publicos/' ||
            request.headers.containsKey('authorization')) {
          throw StateError('Unexpected private or mutating request');
        }
        requests.add(request.url);
        return respond(request);
      }),
    );
    session = Session(client);
    feed = PublicReportsController(RescueApi(client, session));
  });
  tearDown(() {
    feed.dispose();
    session.dispose();
    client.close();
  });

  testWidgets(
    'Search debounces and discards a response from the previous query',
    (tester) async {
      final old = Completer<http.Response>();
      respond = (request) => request.url.queryParameters['buscar'] == 'Riohacha'
          ? Future.value(page([row(1)]))
          : old.future;
      final initial = feed.reload();
      await tester.pump();
      feed.search('R');
      feed.search('Riohacha');
      await tester.pump(const Duration(milliseconds: 399));
      expect(requests.length, 1);
      expect(feed.loading, isTrue);
      await tester.pump(const Duration(milliseconds: 1));
      await tester.pump();
      expect(requests.length, 2);
      expect(feed.reports.single.id, 1);
      old.complete(page([row(999)]));
      await initial;
      expect(feed.reports.single.id, 1);
      expect(feed.error, isNull);
    },
  );

  test('A page failure preserves earlier rows and retries the same cursor explicitly', () async {
    var attempts = 0;
    respond = (request) async {
      if (!request.url.queryParameters.containsKey('antes')) {
        return page([row(30)], next: '30');
      }
      expect(request.url.queryParameters['antes'], '30');
      attempts++;
      if (attempts == 1) return page([], status: 503);
      return page([row(30), row(9)]);
    };
    await feed.reload();
    await feed.loadMore();
    expect(feed.reports.map((r) => r.id), [30]);
    expect(feed.pageError, isA<ApiException>());
    expect(attempts, 1);
    await feed.loadMore();
    expect(feed.reports.map((r) => r.id), [30, 9]);
    expect(feed.nextCursor, isNull);
    expect(feed.pageError, isNull);
    expect(attempts, 2);
  });

  test(
    'An invalid or nonadvancing cursor never replaces already loaded rows',
    () async {
      respond = (request) async =>
          request.url.queryParameters.containsKey('antes')
          ? page([row(30)], next: '30')
          : page([row(30)], next: '30');
      await feed.reload();
      await feed.loadMore();
      expect(feed.pageError, isA<ApiException>());
      expect(feed.reports.map((r) => r.id), [30]);
      expect(requests.length, 2);
    },
  );

  test(
    'Duplicate taps while a page is pending cause only one request',
    () async {
      final pending = Completer<http.Response>();
      respond = (request) => request.url.queryParameters.containsKey('antes')
          ? pending.future
          : Future.value(page([row(30)], next: '30'));
      await feed.reload();
      final more = feed.loadMore();
      await feed.loadMore();
      await Future<void>.delayed(Duration.zero);
      expect(requests.length, 2);
      pending.complete(page([row(9)]));
      await more;
      expect(feed.reports.length, 2);
    },
  );

  testWidgets('An older pending page cannot append into a new search', (
    tester,
  ) async {
    final pending = Completer<http.Response>();
    respond = (request) {
      if (request.url.queryParameters['buscar'] == 'nuevo') {
        return Future.value(page([row(1)]));
      }
      if (request.url.queryParameters.containsKey('antes')) {
        return pending.future;
      }
      return Future.value(page([row(30)], next: '30'));
    };
    await feed.reload();
    final more = feed.loadMore();
    feed.search('nuevo');
    await tester.pump(const Duration(milliseconds: 400));
    await tester.pump();
    pending.complete(page([row(9)]));
    await more;
    expect(feed.reports.map((r) => r.id), [1]);
    expect(feed.loadingMore, isFalse);
    expect(feed.nextCursor, isNull);
  });

  test(
    'Malformed public envelopes do not become empty successful results',
    () async {
      final api = RescueApi(client, session);
      for (final value in [
        {'results': []},
        {'results': [], 'next_cursor': 'https://example.invalid/'},
        {
          'results': [row(2)],
          'next_cursor': '1',
        },
        {
          'results': [for (var id = 1; id <= 21; id++) row(id)],
          'next_cursor': null,
        },
      ]) {
        respond = (_) async => http.Response(jsonEncode(value), 200);
        await expectLater(api.publicReportPage(), throwsA(isA<ApiException>()));
      }
      final before = requests.length;
      await expectLater(
        api.publicReportPage(cursor: '-1'),
        throwsA(isA<ApiException>()),
      );
      expect(requests.length, before);
    },
  );

  testWidgets(
    'An empty active page offers continuation and history includes archived rows',
    (tester) async {
      respond = (request) async =>
          request.url.queryParameters.containsKey('antes')
          ? page([row(9)])
          : page([row(30, status: 'Cerrado')], next: '30');
      // The screen owns its controller; keep this test focused on real controls.
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: RescueScreen(api: RescueApi(client, session))),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Rescate, #30'), findsNothing);
      await tester.ensureVisible(find.text('Cargar más reportes'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Cargar más reportes'));
      await tester.pumpAndSettle();
      await tester.ensureVisible(find.text('Rescate'));
      await tester.pumpAndSettle();
      expect(find.text('Rescate'), findsOneWidget);
      await tester.ensureVisible(find.byTooltip('Historias de rescate'));
      await tester.pumpAndSettle();
      await tester.tap(find.byTooltip('Historias de rescate'));
      await tester.pumpAndSettle();
      expect(find.byType(ReportTile), findsNWidgets(2));
      expect(requests.length, 2);
      expect(tester.takeException(), isNull);
    },
  );
}
