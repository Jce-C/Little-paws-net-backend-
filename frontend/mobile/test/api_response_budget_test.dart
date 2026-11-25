import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/core/api_client.dart';

const limit = ApiClient.maxResponseBytes;
final oversized = isA<ApiException>().having(
  (e) => e.message,
  'message',
  contains('demasiado grande'),
);

void main() {
  test(
    'Oversized declared length cancels the unread response and signals abort',
    () async {
      var cancelled = false;
      var aborted = false;
      final stream = StreamController<List<int>>(
        onCancel: () => cancelled = true,
      );
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient.streaming((request, _) async {
          (request as http.Abortable).abortTrigger!.then((_) => aborted = true);
          return http.StreamedResponse(
            stream.stream,
            200,
            contentLength: limit + 1,
          );
        }),
      );
      addTearDown(api.close);
      await expectLater(api.get('/api/adopcion/catalogo/'), throwsA(oversized));
      await Future<void>.delayed(Duration.zero);
      expect(cancelled, isTrue);
      expect(aborted, isTrue);
      await stream.close();
    },
  );

  for (final declared in [null, 1]) {
    test(
      'Actual streamed bytes are bounded even with declared length $declared',
      () async {
        var stopped = false;
        Stream<List<int>> chunks() async* {
          try {
            yield List<int>.filled(limit, 97);
            yield [98];
            fail('The client must not consume more chunks after the budget');
          } finally {
            stopped = true;
          }
        }

        final api = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient.streaming(
            (_, _) async =>
                http.StreamedResponse(chunks(), 200, contentLength: declared),
          ),
        );
        addTearDown(api.close);
        await expectLater(
          api.get('/api/adopcion/catalogo/'),
          throwsA(oversized),
        );
        expect(stopped, isTrue);
      },
    );
  }

  test('Exactly one MiB of valid JSON remains supported', () async {
    final body = utf8.encode('{"v":"${'a' * (limit - 8)}"}');
    expect(body.length, limit);
    final api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((_) async => http.Response.bytes(body, 200)),
    );
    addTearDown(api.close);
    final result =
        await api.get('/api/adopcion/catalogo/') as Map<String, dynamic>;
    expect((result['v'] as String).length, limit - 8);
  });

  test('The deadline signals abort while waiting for headers', () async {
    var aborted = false;
    final api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      requestTimeout: const Duration(milliseconds: 20),
      client: MockClient.streaming((request, _) async {
        await (request as http.Abortable).abortTrigger;
        aborted = true;
        throw http.RequestAbortedException(request.url);
      }),
    );
    addTearDown(api.close);
    await expectLater(
      api.get('/api/adopcion/catalogo/'),
      throwsA(
        isA<ApiException>().having(
          (e) => e.message,
          'message',
          contains('tardó'),
        ),
      ),
    );
    await Future<void>.delayed(Duration.zero);
    expect(aborted, isTrue);
  });

  test(
    'The deadline aborts and cancels a response that stalls during streaming',
    () async {
      var cancelled = false;
      final stream = StreamController<List<int>>(
        onCancel: () => cancelled = true,
      );
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        requestTimeout: const Duration(milliseconds: 20),
        client: MockClient.streaming((request, _) async {
          (request as http.Abortable).abortTrigger!.then((_) {
            stream.addError(http.RequestAbortedException(request.url));
            unawaited(stream.close());
          });
          stream.add([123]);
          return http.StreamedResponse(stream.stream, 200);
        }),
      );
      addTearDown(api.close);
      await expectLater(
        api.get('/api/adopcion/catalogo/'),
        throwsA(
          isA<ApiException>().having(
            (e) => e.message,
            'message',
            contains('tardó'),
          ),
        ),
      );
      await Future<void>.delayed(Duration.zero);
      expect(cancelled, isTrue);
    },
  );

  test(
    'A rejected response does not close the client or replay the operation',
    () async {
      var calls = 0;
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient.streaming((request, body) async {
          calls++;
          expect(request.followRedirects, isFalse);
          expect(request.headers['authorization'], 'Bearer synthetic-token');
          await body.drain<void>();
          return calls == 1
              ? http.StreamedResponse(
                  const Stream.empty(),
                  200,
                  contentLength: limit + 1,
                )
              : http.StreamedResponse(
                  Stream.value(utf8.encode('{"ok":true}')),
                  200,
                );
        }),
      );
      addTearDown(api.close);
      await expectLater(
        api.post('/api/adopcion/solicitudes/', {
          'id_mascota': 14,
        }, token: 'synthetic-token'),
        throwsA(oversized),
      );
      expect(calls, 1);
      expect(
        await api.get('/api/adopcion/catalogo/', token: 'synthetic-token'),
        {'ok': true},
      );
      expect(calls, 2);
    },
  );

  test('Default IO transport times out a real local stalled body and stays reusable', () async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    final release = Completer<void>();
    final started = Completer<void>();
    Future<void> serve(HttpRequest request) async {
      try {
        request.response.headers.contentType = ContentType.json;
        if (request.uri.path == '/api/stalled/') {
          request.response.write('{');
          await request.response.flush();
          started.complete();
          await release.future;
          request.response.write('}');
        } else {
          request.response.write('{"ok":true}');
        }
        await request.response.close();
      } on Exception {
        // Client cancellation may close this synthetic server response.
      }
    }

    final listener = server.listen((request) => unawaited(serve(request)));
    final api = ApiClient(
      base: Uri.parse('http://127.0.0.1:${server.port}'),
      requestTimeout: const Duration(milliseconds: 500),
    );
    addTearDown(() async {
      if (!release.isCompleted) release.complete();
      api.close();
      await server.close(force: true);
      await listener.cancel();
    });
    await expectLater(
      api.get('/api/stalled/'),
      throwsA(
        isA<ApiException>().having(
          (e) => e.message,
          'message',
          contains('tardó'),
        ),
      ),
    );
    expect(started.isCompleted, isTrue);
    expect(await api.get('/api/ok/'), {'ok': true});
  });

  test('Nonpositive deadlines are rejected', () {
    expect(
      () => ApiClient(
        base: Uri.parse('http://localhost:8016'),
        requestTimeout: Duration.zero,
      ),
      throwsArgumentError,
    );
  });

  test('Oversized error bodies preserve auth and throttling status; success remains unconfirmed', () async {
    var code = 401;
    final api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient.streaming(
        (_, _) async => http.StreamedResponse(
          const Stream.empty(),
          code,
          contentLength: limit + 1,
        ),
      ),
    );
    addTearDown(api.close);
    for (final status in [401, 403, 429, 503, 201]) {
      code = status;
      await expectLater(
        api.get('/api/adopcion/catalogo/'),
        throwsA(
          isA<ApiException>().having(
            (e) => e.status,
            'status',
            status >= 400 ? status : null,
          ),
        ),
      );
    }
  });
}
