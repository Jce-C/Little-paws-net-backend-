import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

// Existing screen fixtures describe one list. Present that fixture through the
// real paginated envelope; pagination contract tests use unadapted MockClient.
MockClient catalogClient(
  Future<http.Response> Function(http.Request) respond,
) => MockClient((request) async {
  if (request.url.path == '/api/adopcion/solicitudes/mias/') {
    final legacy = http.Request(
      request.method,
      request.url.replace(
        path: '/api/seguridad/operaciones/mis-registros/',
        query: '',
      ),
    )..headers.addAll(request.headers);
    final response = await respond(legacy);
    if (response.statusCode != 200) return response;
    final data = jsonDecode(response.body);
    return http.Response(
      jsonEncode({'results': data['adopciones'], 'next_cursor': null}),
      200,
      headers: response.headers,
    );
  }
  final response = await respond(request);
  if (request.url.path != '/api/adopcion/catalogo/' ||
      response.statusCode != 200) {
    return response;
  }
  final data = jsonDecode(response.body);
  if (data is! List) return response;
  return http.Response(
    jsonEncode({
      'results': data,
      'next': null,
      'previous': null,
      'species': data
          .whereType<Map>()
          .map((row) => row['especie'])
          .whereType<String>()
          .toSet()
          .toList(),
    }),
    200,
    headers: response.headers,
  );
});
