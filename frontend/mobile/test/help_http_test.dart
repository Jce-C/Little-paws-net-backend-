import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/io_client.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';

class _LocalHttp extends HttpOverrides {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  const credentials = String.fromEnvironment('LPN_REAL_QA_CREDENTIALS');
  const evidence = String.fromEnvironment('LPN_REAL_QA_EVIDENCE');
  test('Real help publication interest scoped management and commitment integrate with MySQL', () async {
    final data = jsonDecode(File(credentials).readAsStringSync()) as Map;
    expect((data['email'] as String).endsWith('@example.invalid'), isTrue);
    final api = ApiClient(
      base: Uri.parse('http://127.0.0.1:8019'),
      client: IOClient(_LocalHttp().createHttpClient(null)),
    );
    final own = Session(api), manager = Session(api);
    addTearDown(api.close);
    addTearDown(own.dispose);
    addTearDown(manager.dispose);
    await own.restore();
    await manager.restore();
    await own.login(
      data['email'] as String,
      data['password'] as String,
      remember: false,
    );
    await manager.login(
      data['operator'] as String,
      data['password'] as String,
      remember: false,
    );
    final id = data['foundation'];
    final path = '/api/ayudas/organizaciones/$id/';
    final programPath = '${path}programa/';
    var original =
        await manager.authorized((t) => api.get(programPath, token: t)) as Map;
    if (original['publicada'] == true) {
      original = await manager.authorized(
        (t) => api.patch(programPath, {
          ...Map<String, Object?>.from(original),
          'publicada': false,
          'confirmar_publicacion': false,
        }, token: t),
      ) as Map;
    }
    final body = <String, Object?>{
      'version': original['version'],
      'publicada': true,
      'confirmar_publicacion': true,
      'actividades': [
        {
          'titulo': 'Paseos QA integración',
          'descripcion': 'Acompañamiento supervisado ficticio.',
          'horario': 'Por acordar',
          'requisitos': 'Inducción del equipo',
        },
      ],
      'canales': [
        {
          'titulo': 'Canal ficticio QA',
          'descripcion': 'No es un medio de pago real.',
          'url': 'https://example.invalid/ayuda',
        },
      ],
    };
    final published = await manager.authorized(
      (t) => api.patch(programPath, body, token: t),
    ) as Map;
    await expectLater(
      manager.authorized(
        (t) => api.patch(programPath, {...body, 'actividades': []}, token: t),
      ),
      throwsA(isA<ApiException>().having((e) => e.status, 'status', 409)),
    );
    final public = await api.get('/api/red/organizaciones/') as List;
    final foundation = public.cast<Map>().singleWhere((r) => r['id'] == id);
    expect(
      (foundation['programa_ayuda'] as Map)['actividades'],
      body['actividades'],
    );
    final offer = <String, Object?>{
      'fundacion_id': id,
      'modalidad': 'voluntariado',
      'actividad': 'Paseos QA integración',
      'mensaje': 'Interés privado sintético de integración.',
    };
    Future<Object?> send() => own.authorized(
      (t) => api.post('/api/ayudas/intereses/', offer, token: t),
    );
    final first = await send() as Map;
    final second = await send() as Map;
    expect(first['id'], second['id']);
    expect(second['ya_registrado'], true);
    expect(first['aceptado'], false);
    final mine = await own.authorized(
      (t) => api.get('/api/ayudas/intereses/', token: t),
    ) as List;
    expect(
      mine.cast<Map>().singleWhere((r) => r['id'] == first['id'])['actividad'],
      offer['actividad'],
    );
    final received =
        await manager.authorized((t) => api.get(path, token: t)) as Map;
    expect(
      (received['ofrecimientos'] as List).cast<Map>().singleWhere(
        (r) => r['id'] == first['id'],
      )['mensaje'],
      offer['mensaje'],
    );
    final others = await manager.authorized(
      (t) => api.get('/api/ayudas/intereses/', token: t),
    ) as List;
    expect(others.where((r) => (r as Map)['id'] == first['id']), isEmpty);
    await expectLater(
      own.authorized((t) => api.get(path, token: t)),
      throwsA(isA<ApiException>().having((e) => e.status, 'status', 403)),
    );
    await expectLater(
      manager.authorized(
        (t) =>
            api.get('/api/ayudas/organizaciones/${data['foreign']}/', token: t),
      ),
      throwsA(isA<ApiException>().having((e) => e.status, 'status', 403)),
    );
    await expectLater(
      api.get('/api/ayudas/intereses/'),
      throwsA(isA<ApiException>().having((e) => e.status, 'status', 401)),
    );
    final saved = await manager.authorized(
      (t) => api.patch(path, {
        'version': received['version'],
        'acepta_voluntarios': false,
        'necesidades_ayuda': 'Insumos sellados QA',
      }, token: t),
    ) as Map;
    await expectLater(
      own.authorized(
        (t) => api.post('/api/ayudas/intereses/', offer, token: t),
      ),
      throwsA(isA<ApiException>().having((e) => e.status, 'status', 400)),
    );
    final closed = await api.get('/api/red/organizaciones/') as List;
    final closedProgram =
        closed.cast<Map>().singleWhere((r) => r['id'] == id)['programa_ayuda']
            as Map;
    expect(closedProgram['actividades'], isEmpty);
    expect(closedProgram['canales'], isNotEmpty);
    // The monetary flow records an intention only, not a payment.
    final commitment = await own.authorized(
      (t) => api.post('/api/fondos/donaciones/', {
        'id_fondo_externo': data['fund'],
        'monto_comprometido': '10000.00',
      }, token: t),
    ) as Map;
    expect(commitment['id_donacion'], isA<int>());
    expect(commitment['dinero_recibido'], false);
    final withdrawn = await manager.authorized(
      (t) => api.patch(programPath, {
        ...body,
        'version': published['version'],
        'publicada': false,
        'confirmar_publicacion': false,
      }, token: t),
    ) as Map;
    expect(withdrawn['publicada'], false);
    final end = await api.get('/api/red/organizaciones/') as List;
    expect(
      end.cast<Map>().singleWhere((r) => r['id'] == id)['programa_ayuda'],
      isNull,
    );
    // Restore intake setting for repeatable local QA.
    await manager.authorized(
      (t) => api.patch(path, {
        'version': saved['version'],
        'acepta_voluntarios': true,
        'necesidades_ayuda': '',
      }, token: t),
    );
    if (evidence.isNotEmpty) {
      File(evidence).writeAsStringSync(
        jsonEncode({
          'solo_loopback_QA': true,
          'interes_id': first['id'],
          'compromiso_id': commitment['id_donacion'],
          'publicacion_visible_y_retirada': true,
          'conflicto_rechazado': true,
          'reintento_interes_mismo_id': true,
          'actividad_y_mensaje_persistidos': true,
          'titular_y_gestor_ven_mismo_ofrecimiento': true,
          'ambito_ajeno_y_anonimo_denegados': true,
          'cierre_voluntariado_oculta_actividades_y_rechaza_envio': true,
          'compromiso_sin_pago': true,
        }),
      );
    }
  }, skip: credentials.isEmpty);
}
