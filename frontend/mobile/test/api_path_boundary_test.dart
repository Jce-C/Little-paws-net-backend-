import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/core/api_client.dart';

void main() {
  test(
    'Invalid API paths never reach transport with a session credential',
    () async {
      var calls = 0;
      final api = ApiClient(
        base: Uri.parse('https://backend.example.invalid'),
        client: MockClient((_) async {
          calls++;
          return http.Response('{}', 200);
        }),
      );
      addTearDown(api.close);
      for (final path in [
        '/api/../panel/',
        '/api/%2e%2e/panel/',
        '/api/catalogo/../../panel/',
        '/api/catalogo/%2e%2e/%2e%2e/panel/',
        '/api/%2f..%2fpanel/',
        '/api/%5c..%5cpanel/',
        '/api/catalogo/#private',
        'https://other.example.invalid/api/catalogo/',
        '//other.example.invalid/api/catalogo/',
      ]) {
        await expectLater(
          api.get(path, token: 'synthetic-session'),
          throwsArgumentError,
          reason: path,
        );
        expect(calls, 0, reason: path);
      }
    },
  );

  test(
    'Search query encoding remains intact inside the approved API origin',
    () async {
      final target = Uri(
        path: '/api/reportes/publicos/',
        queryParameters: {'q': 'Río / ../ # & café', 'cursor': '20'},
      );
      var calls = 0;
      final api = ApiClient(
        base: Uri.parse('https://backend.example.invalid'),
        client: MockClient((request) async {
          calls++;
          expect(request.url.origin, 'https://backend.example.invalid');
          expect(request.url.path, '/api/reportes/publicos/');
          expect(request.url.queryParameters, target.queryParameters);
          return http.Response('{}', 200);
        }),
      );
      addTearDown(api.close);
      await api.get(target.toString());
      expect(calls, 1);
    },
  );
}
