import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/services.dart';
import 'package:http/io_client.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/rescue/rescue_api.dart';

class _LocalHttp extends HttpOverrides {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  const run = bool.fromEnvironment('LPN_REPORT_HTTP_QA');
  const evidence = String.fromEnvironment('LPN_REPORT_HTTP_EVIDENCE');
  test('Real MySQL HTTP report edit rejects wrong key, preserves public update and closes once', () async {
    final api = ApiClient(
      base: Uri.parse('http://127.0.0.1:8018'),
      client: IOClient(_LocalHttp().createHttpClient(null)),
    );
    final session = Session(api);
    final rescue = RescueApi(api, session);
    addTearDown(api.close);
    addTearDown(session.dispose);
    await session.restore();
    final options = await rescue.options('Riohacha');
    final description =
        'Reporte QA local ${DateTime.now().microsecondsSinceEpoch}';
    final result = await rescue.create(
      type: options.types.first.id,
      city: options.cities.first.id,
      neighborhood: 'Sector ficticio QA',
      address: 'Referencia ficticia QA',
      description: description,
      contact: 'contacto-sintetico.invalid',
      photo: (await rootBundle.load('assets/access/login-pets.webp')).buffer
          .asUint8List(),
      photoPublic: true,
    );
    final key = result.privateCode!;
    await expectLater(
      rescue.manageAnonymous(
        reportId: result.id,
        code: 'clave-incorrecta',
        description: 'Cambio no autorizado',
      ),
      throwsA(isA<ApiException>().having((e) => e.status, 'status', 403)),
    );
    final edited = await rescue.manageAnonymous(
      reportId: result.id,
      code: key,
      description: '$description corregido',
      clearContact: true,
    );
    expect(edited.status, 'Pendiente');
    expect(edited.privateCode, isNull);
    final page = await rescue.publicReportPage(query: description);
    expect(
      page.reports.singleWhere((r) => r.id == result.id).description,
      '$description corregido',
    );
    final photo =
        page.reports.singleWhere((r) => r.id == result.id).photo as Map;
    expect(photo['bytes'] as int, lessThanOrEqualTo(128 * 1024));
    expect(photo['ancho'] as int, lessThanOrEqualTo(960));
    expect(photo['alto'] as int, lessThanOrEqualTo(960));
    final photoClient = IOClient(_LocalHttp().createHttpClient(null));
    addTearDown(photoClient.close);
    final photoResponse = await photoClient.get(
      Uri.parse('http://127.0.0.1:8018/api/reportes/${result.id}/foto/'),
    );
    expect(photoResponse.statusCode, 200);
    expect(photoResponse.headers['content-type'], startsWith('image/webp'));
    final raw = await api.get(
      '/api/reportes/publicos/?buscar=${Uri.encodeQueryComponent(description)}',
    );
    expect(jsonEncode(raw).contains(key), isFalse);
    expect(jsonEncode(raw).contains('contacto-sintetico.invalid'), isFalse);
    expect(
      (await rescue.manageAnonymous(
        reportId: result.id,
        code: key,
        close: true,
      )).status,
      'Cerrado',
    );
    await expectLater(
      rescue.manageAnonymous(reportId: result.id, code: key, close: true),
      throwsA(isA<ApiException>().having((e) => e.status, 'status', 409)),
    );
    if (evidence.isNotEmpty) {
      File(evidence).writeAsStringSync(
        jsonEncode({
          'loopback_only': true,
          'synthetic_only': true,
          'report_id': result.id,
          'wrong_key_denied': true,
          'public_update_preserved': true,
          'private_contact_and_key_not_public': true,
          'closed_once': true,
          'photo_publication_confirmed': true,
          'photo_webp_bytes': photo['bytes'],
          'photo_http_status': photoResponse.statusCode,
        }),
      );
    }
  }, skip: !run);
}
