import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ApiException implements Exception {
  const ApiException(this.message, {this.status});

  final String message;
  final int? status;

  @override
  String toString() => message;
}

class ApiClient {
  ApiClient({
    required Uri base,
    http.Client? client,
    Duration requestTimeout = const Duration(seconds: 15),
  }) : base = _validateBase(base),
       _requestTimeout = _validateTimeout(requestTimeout),
       _client = client ?? http.Client();

  factory ApiClient.fromEnvironment() => ApiClient(
    base: Uri.parse(
      const String.fromEnvironment(
        'LPN_API_BASE_URL',
        defaultValue: '',
      ),
    ),
  );

  final Uri base;
  final http.Client _client;
  final Duration _requestTimeout;
  static const maxResponseBytes = 1024 * 1024;

  static Duration _validateTimeout(Duration timeout) {
    if (timeout <= Duration.zero) {
      throw ArgumentError('El tiempo de espera debe ser positivo.');
    }
    return timeout;
  }

  static Uri _validateBase(Uri base) {
    const local = {'127.0.0.1', 'localhost', '10.0.2.2'};
    final secure = base.scheme == 'https';
    final devOrigin =
        kDebugMode && base.scheme == 'http' && local.contains(base.host);
    if (base.host.isEmpty ||
        (!secure && !devOrigin) ||
        base.userInfo.isNotEmpty ||
        base.hasQuery ||
        base.hasFragment ||
        (base.path.isNotEmpty && base.path != '/')) {
      throw ArgumentError(
        'Utiliza una URL HTTPS del backend o el servidor local de desarrollo.',
      );
    }
    return base;
  }

  static String _imageName(Uint8List bytes) {
    if (bytes.length >= 12 &&
        String.fromCharCodes(bytes.sublist(0, 4)) == 'RIFF' &&
        String.fromCharCodes(bytes.sublist(8, 12)) == 'WEBP') {
      return 'foto.webp';
    }
    if (bytes.length >= 8 &&
        listEquals(bytes.sublist(0, 8), const [
          137,
          80,
          78,
          71,
          13,
          10,
          26,
          10,
        ])) {
      return 'foto.png';
    }
    // A safe generated name; the backend still decodes and validates the bytes.
    return 'foto.jpg';
  }

  Future<Object?> get(String path, {String? token}) =>
      _send('GET', path, token: token);

  Future<Object?> delete(String path, {String? token}) =>
      _send('DELETE', path, token: token);

  Future<Object?> post(
    String path,
    Map<String, Object?> body, {
    String? token,
    String? operationKey,
  }) =>
      _send('POST', path, body: body, token: token, operationKey: operationKey);

  Future<Object?> patch(
    String path,
    Map<String, Object?> body, {
    String? token,
  }) => _send('PATCH', path, body: body, token: token);

  Future<Object?> uploadImage(
    String path,
    Map<String, Object?> fields,
    List<int> bytes, {
    String? token,
    String? operationKey,
  }) {
    if (bytes.isEmpty || bytes.length > 5 * 1024 * 1024) {
      throw const ApiException('Elige una imagen de hasta 5 MB.');
    }
    return _send(
      'POST',
      path,
      body: fields,
      fileData: Uint8List.fromList(bytes),
      token: token,
      operationKey: operationKey,
    );
  }

  Future<Object?> uploadProfilePhoto(List<int> bytes, {required String token}) {
    if (bytes.isEmpty || bytes.length > 5 * 1024 * 1024) {
      throw const ApiException('Elige una imagen de hasta 5 MB.');
    }
    return _send(
      'POST',
      '/api/auth/foto-publica/',
      token: token,
      body: {'confirmar_publicacion': 'true'},
      fileData: Uint8List.fromList(bytes),
    );
  }

  Future<Object?> _send(
    String method,
    String path, {
    Map<String, Object?>? body,
    Uint8List? fileData,
    String? token,
    String? operationKey,
  }) async {
    final route = Uri.tryParse(path);
    if (!path.startsWith('/api/') ||
        route == null ||
        route.hasScheme ||
        route.hasAuthority ||
        route.hasFragment ||
        route.pathSegments.any(
          (segment) => segment.contains('/') || segment.contains(r'\'),
        )) {
      throw ArgumentError('La ruta debe pertenecer a la API.');
    }
    final target = base.resolveUri(route);
    if (target.origin != base.origin || !target.path.startsWith('/api/')) {
      throw ArgumentError('La ruta debe pertenecer a la API.');
    }
    final abort = Completer<void>();
    final http.BaseRequest request;
    if (fileData != null) {
      request =
          http.AbortableMultipartRequest(
              method,
              target,
              abortTrigger: abort.future,
            )
            ..fields.addAll({
              for (final e in body!.entries) e.key: '${e.value}',
            })
            ..files.add(
              http.MultipartFile.fromBytes(
                'archivo',
                fileData,
                filename: _imageName(fileData),
              ),
            );
    } else {
      final json = http.AbortableRequest(
        method,
        target,
        abortTrigger: abort.future,
      );
      if (body != null) {
        json.headers['Content-Type'] = 'application/json';
        json.body = jsonEncode(body);
      }
      request = json;
    }
    request.followRedirects = false;
    request.headers['Accept'] = 'application/json';
    if (operationKey != null) {
      if (!RegExp(r'^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$')
          .hasMatch(operationKey)) {
        throw ArgumentError('La clave de operación no es válida.');
      }
      request.headers['Idempotency-Key'] = operationKey;
    }
    if (token != null) request.headers['Authorization'] = 'Bearer $token';
    final http.Response response;
    try {
      response = await _client
          .send(request)
          .then((value) => _boundedResponse(value, abort))
          .timeout(
            _requestTimeout,
            onTimeout: () {
              if (!abort.isCompleted) abort.complete();
              throw TimeoutException('API request deadline');
            },
          );
    } on TimeoutException {
      if (!abort.isCompleted) abort.complete();
      throw const ApiException(
        'El servidor tardó en responder. Intenta de nuevo.',
      );
    } on http.ClientException {
      throw const ApiException(
        'No pudimos conectar. Revisa tu conexión e intenta de nuevo.',
      );
    }
    Object? payload;
    if (response.bodyBytes.isNotEmpty) {
      try {
        payload = jsonDecode(utf8.decode(response.bodyBytes));
      } on FormatException {
        if (response.statusCode < 400) {
          throw const ApiException(
            'El servidor devolvió una respuesta inesperada.',
          );
        }
      }
    }
    if (response.statusCode >= 200 && response.statusCode < 300) return payload;
    throw ApiException(
      _errorMessage(response.statusCode, payload),
      status: response.statusCode,
    );
  }

  Future<http.Response> _boundedResponse(
    http.StreamedResponse response,
    Completer<void> abort,
  ) async {
    final declared = response.contentLength;
    if (abort.isCompleted ||
        (declared != null && declared > maxResponseBytes)) {
      // Even custom clients that ignore abort must release an unread response.
      await response.stream.listen((_) {}, onError: (Object _) {}).cancel();
      if (!abort.isCompleted) abort.complete();
      if (declared != null && declared > maxResponseBytes) {
        throw _oversized(response.statusCode);
      }
      throw http.RequestAbortedException(response.request?.url);
    }
    final bytes = BytesBuilder(copy: false);
    await for (final chunk in response.stream) {
      if (abort.isCompleted) {
        throw http.RequestAbortedException(response.request?.url);
      }
      if (bytes.length + chunk.length > maxResponseBytes) {
        if (!abort.isCompleted) abort.complete();
        throw _oversized(response.statusCode);
      }
      bytes.add(chunk);
    }
    return http.Response.bytes(
      bytes.takeBytes(),
      response.statusCode,
      headers: response.headers,
      request: response.request,
      isRedirect: response.isRedirect,
      persistentConnection: response.persistentConnection,
      reasonPhrase: response.reasonPhrase,
    );
  }

  static ApiException _oversized(int status) => ApiException(
    'La respuesta del servidor es demasiado grande. Intenta de nuevo más tarde.',
    status: status >= 400 ? status : null,
  );

  static String _errorMessage(int status, Object? payload) {
    if (status == 429) {
      return 'Hubo demasiados intentos. Espera un momento y vuelve a probar.';
    }
    if (status == 401) {
      return 'Revisa tus credenciales o vuelve a iniciar sesión.';
    }
    if (status == 403) {
      return 'Tu cuenta no tiene acceso para realizar esta acción.';
    }
    if (status >= 500) return 'El servicio no está disponible en este momento.';
    if (payload is Map<String, dynamic>) {
      for (final key in [
        'detalle',
        'detail',
        'non_field_errors',
        ...payload.keys,
      ]) {
        final value = payload[key];
        if (value is String && value.trim().isNotEmpty) return value;
        if (value is List && value.isNotEmpty && value.first is String) {
          return value.first as String;
        }
      }
    }
    return 'No pudimos completar la operación. Revisa los datos e intenta de nuevo.';
  }

  void close() => _client.close();
}
