import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/core/api_client.dart';

void main() {
  for (final method in ['GET', 'POST']) {
    for (final status in [302, 307, 308]) {
      test(
        '$method $status does not forward credentials or replay a write',
        () async {
          final source = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
          final destination = await HttpServer.bind(
            InternetAddress.loopbackIPv4,
            0,
          );
          var sourceCalls = 0;
          var destinationCalls = 0;
          var recoveryCalls = 0;
          final destinationListener = destination.listen((request) async {
            destinationCalls++;
            await request.drain<void>();
            request.response.write('{"unexpected":true}');
            await request.response.close();
          });
          final sourceListener = source.listen((request) async {
            await request.drain<void>();
            if (request.uri.path == '/api/ok/') {
              recoveryCalls++;
              request.response.headers.contentType = ContentType.json;
              request.response.write('{"ok":true}');
            } else {
              sourceCalls++;
              expect(request.method, method);
              expect(
                request.headers.value(HttpHeaders.authorizationHeader),
                'Bearer synthetic-session',
              );
              request.response.statusCode = status;
              request.response.headers.set(
                HttpHeaders.locationHeader,
                'http://127.0.0.1:${destination.port}/received/',
              );
            }
            await request.response.close();
          });
          final api = ApiClient(
            base: Uri.parse('http://127.0.0.1:${source.port}'),
            requestTimeout: const Duration(seconds: 3),
          );
          addTearDown(() async {
            api.close();
            await source.close(force: true);
            await destination.close(force: true);
            await sourceListener.cancel();
            await destinationListener.cancel();
          });

          final operation = method == 'GET'
              ? api.get('/api/private/', token: 'synthetic-session')
              : api.post('/api/adopcion/solicitudes/', {
                  'id_mascota': 1,
                }, token: 'synthetic-session');
          await expectLater(
            operation,
            throwsA(
              isA<ApiException>().having((e) => e.status, 'status', status),
            ),
          );
          expect(sourceCalls, 1);
          expect(destinationCalls, 0);
          expect(await api.get('/api/ok/'), {'ok': true});
          expect(recoveryCalls, 1);
          expect(sourceCalls, 1);
          expect(destinationCalls, 0);
        },
      );
    }
  }
}
