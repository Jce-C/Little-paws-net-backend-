import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/io_client.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/notifications/notifications_api.dart';
import 'package:little_paws_net/adoption/questionnaire_screen.dart'
    show evaluationVersion, evaluationNotice;

class _LoopbackHttp extends HttpOverrides {}

void main() {
  const credentials = String.fromEnvironment('LPN_REAL_QA_CREDENTIALS');
  const evidence = String.fromEnvironment('LPN_REAL_QA_EVIDENCE');
  test('Real loopback HTTP: adoption decision links own notification and server read timestamp', () async {
    final data = jsonDecode(
      File(credentials).readAsStringSync(),
    ) as Map<String, dynamic>;
    expect((data['email'] as String).endsWith('@example.invalid'), isTrue);
    final api = ApiClient(
      base: Uri.parse('http://127.0.0.1:8018'),
      client: IOClient(_LoopbackHttp().createHttpClient(null)),
    );
    final citizen = Session(api), operator = Session(api);
    addTearDown(api.close);
    addTearDown(citizen.dispose);
    addTearDown(operator.dispose);
    await citizen.restore();
    await operator.restore();
    final watch = Stopwatch()..start();
    await citizen.login(
      data['email'] as String,
      data['password'] as String,
      remember: false,
    );
    expect(citizen.account!.adoptionEvaluation, isTrue);
    final answers = <String, dynamic>{
      'nombre': 'Persona QA local',
      'documento': 'QA-HTTP-PRIVADO',
      'telefono': '0000000000',
      'email': data['email'],
      'direccion': 'Dirección ficticia QA',
      'vivienda': 'casa',
      'tenencia': 'propia',
      'seguridad_espacio': 'Ventanas protegidas',
      'personas_hogar': 2,
      'acuerdo_hogar': true,
      'tiempo_cuidado': 'diario',
      'recursos_cuidado': 'disponibles',
      'cuidados_especiales': 'necesito_orientacion',
      'seguimiento': 'si',
      'mascotas_actuales': false,
      'experiencia_previa': false,
      'motivo': 'Quiero ofrecer un hogar responsable.',
      'datos_correctos': true,
      'autoriza_evaluacion': true,
      'version': evaluationVersion,
    };
    final createWatch = Stopwatch()..start();
    final id = await AdoptionApi(
      api,
      citizen,
    ).requestEvaluation(data['pet'] as int, answers);
    createWatch.stop();
    final own = await citizen.authorized(
      (token) => api.get('/api/adopcion/solicitudes/$id/', token: token),
    ) as Map;
    expect((own['evaluacion'] as Map)['respuestas'], answers);
    expect((own['evaluacion'] as Map)['autorizacion'], evaluationNotice);
    final page = await AdoptionApi(api, citizen).requestPage();
    expect(page.rows.any((r) => r.id == id), isTrue);
    await operator.login(
      data['operator'] as String,
      data['password'] as String,
      remember: false,
    );
    await expectLater(
      operator.authorized(
        (token) => api.get('/api/adopcion/solicitudes/$id/', token: token),
      ),
      throwsA(isA<ApiException>()),
    );
    await operator.authorized(
      (token) => api.post(
        '/api/seguridad/asignaciones/adopcion/$id/tomar/',
        {},
        token: token,
      ),
    );
    final review = await operator.authorized(
      (token) => api.get(
        '/api/seguridad/operaciones/registros/adopcion/$id/',
        token: token,
      ),
    ) as Map;
    expect('${review['evaluacion_inicial']}', contains('QA-HTTP-PRIVADO'));
    await operator.authorized(
      (token) => api.post('/api/adopcion/solicitudes/$id/resolver/', {
        'id_fundacion': (own['evaluacion'] as Map)['organizacion_receptora'],
        'aprobar': false,
        'observacion': 'Decisión ficticia de QA local',
      }, token: token),
    );
    final finalState = await citizen.authorized(
      (token) => api.get('/api/adopcion/solicitudes/$id/', token: token),
    ) as Map;
    expect(finalState['estado_adopcion__nombre'], 'Rechazada');
    expect((finalState['evaluacion'] as Map)['respuestas'], answers);
    final notifications = NotificationsApi(api, citizen);
    final inbox = await notifications.page();
    final notification = inbox.items.singleWhere((n) => n.requestId == id);
    expect(notification.unread, isTrue);
    expect(notification.kind, 'Resultado de adopción');
    final readAt = await notifications.markRead(notification.id);
    expect(readAt, isNotNull);
    expect(await notifications.markRead(notification.id), readAt);
    final readInbox = await notifications.page();
    expect(
      readInbox.items.singleWhere((n) => n.id == notification.id).readAt,
      readAt,
    );
    await expectLater(
      NotificationsApi(api, operator).markRead(notification.id),
      throwsA(isA<ApiException>().having((e) => e.status, 'status', 404)),
    );
    final ownRequests = await AdoptionApi(api, citizen).requestPage();
    expect(ownRequests.rows.singleWhere((r) => r.id == id).status, 'Rechazada');
    watch.stop();
    if (evidence.isNotEmpty) {
      File(evidence).writeAsStringSync(
        jsonEncode({
          'loopback_only': true,
          'application_id': id,
          'create_ms': createWatch.elapsedMilliseconds,
          'full_flow_ms': watch.elapsedMilliseconds,
          'questions_preserved_after_decision': true,
          'notification_id': notification.id,
          'destination_matches_request': true,
          'read_timestamp_from_server': readAt!.toIso8601String(),
          'repeat_read_same_timestamp': true,
          'foreign_mark_denied': true,
          'request_list_matches_detail': true,
          'operator_cannot_impersonate_applicant': true,
          'assigned_review': true,
          'fixture': 'synthetic-local-only',
          'note': 'Single local sample; not a production latency or capacity guarantee.',
        }),
      );
    }
  }, skip: credentials.isEmpty);
}
