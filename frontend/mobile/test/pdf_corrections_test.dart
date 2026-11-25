import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:image_picker/image_picker.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/auth/account_screen.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/design/photo_attachment.dart';
import 'package:little_paws_net/rescue/rescue_api.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/adoption/adoption_screens.dart';
import 'package:little_paws_net/pets/personal_pet_screen.dart';
import 'package:little_paws_net/explore/bank_instructions.dart';

http.Response json(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() => FlutterSecureStorage.setMockInitialValues({}));

  testWidgets(
    'Camera and gallery selections can be replaced and removed before upload',
    (tester) async {
      final bytes = (await rootBundle.load('assets/access/login-pets.webp'))
          .buffer
          .asUint8List();
      var value = bytes.sublist(0, 0);
      final sources = <ImageSource>[];
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StatefulBuilder(
              builder: (context, change) => PhotoAttachment(
                value: value.isEmpty ? null : value,
                onChanged: (next) =>
                    change(() => value = next ?? bytes.sublist(0, 0)),
                choose: (source) async {
                  sources.add(source);
                  return bytes;
                },
              ),
            ),
          ),
        ),
      );
      await tester.tap(find.text('Tomar fotografía'));
      await tester.pumpAndSettle();
      expect(sources, [ImageSource.camera]);
      expect(value, bytes);
      expect(
        find.bySemanticsLabel('Vista previa de la fotografía'),
        findsOneWidget,
      );
      await tester.tap(find.text('Seleccionar de galería'));
      await tester.pumpAndSettle();
      expect(sources, [ImageSource.camera, ImageSource.gallery]);
      await tester.tap(find.text('Quitar foto'));
      await tester.pumpAndSettle();
      expect(value, isEmpty);
      expect(find.byType(Image), findsNothing);
    },
  );

  test('Report photo travels in the same multipart request as its data and consent', () async {
    var writes = 0;
    final api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        writes++;
        expect(request.url.path, '/api/reportes/');
        expect(request.method, 'POST');
        expect(
          request.headers['content-type'],
          contains('multipart/form-data'),
        );
        final body = latin1.decode(request.bodyBytes);
        expect(body, contains('filename="foto.webp"'));
        for (final field in [
          'archivo',
          'descripcion',
          'tipo_reporte',
          'ciudad_id',
          'confirmar_foto_publica',
        ]) {
          expect(body, contains('name="$field"'));
        }
        expect(body, contains('true'));
        return json({
          'id_reporte': 41,
          'estado': 'Pendiente',
          'codigo_gestion': 'private-code-for-test',
        }, 201);
      }),
    );
    addTearDown(api.close);
    final session = Session(api);
    addTearDown(session.dispose);
    await session.restore();
    final bytes = (await rootBundle.load('assets/access/login-pets.webp'))
        .buffer
        .asUint8List();
    final receipt = await RescueApi(api, session).create(
      type: 10,
      city: 7,
      neighborhood: 'Centro',
      address: 'Referencia QA',
      description: 'Necesita ayuda',
      photo: bytes,
      photoPublic: true,
    );
    expect(receipt.id, 41);
    expect(writes, 1);
  });

  testWidgets(
    'Remember preference is restored without HTTP and can be disabled',
    (tester) async {
      var calls = 0;
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((_) async {
          calls++;
          return json({});
        }),
      );
      addTearDown(api.close);
      final session = Session(api);
      addTearDown(session.dispose);
      await session.restore();
      await session.setRememberPreference(true);
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: LoginScreen(session: session),
        ),
      );
      await tester.pumpAndSettle();
      expect(tester.widget<Checkbox>(find.byType(Checkbox)).value, isTrue);
      await tester.ensureVisible(find.byType(Checkbox));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(Checkbox));
      await tester.pumpAndSettle();
      expect(tester.widget<Checkbox>(find.byType(Checkbox)).value, isFalse);
      expect(await session.loadRememberPreference(), isFalse);
      expect(calls, 0);
      expect(
        (await const FlutterSecureStorage().readAll()).values,
        isNot(contains('synthetic-password')),
      );
    },
  );

  testWidgets(
    'Personal pet form submits owner-free data once and preserves its origin',
    (tester) async {
      var writes = 0;
      Map<String, dynamic>? sent;
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          if (request.url.path == '/api/auth/token/') {
            return json({
              'access': 'synthetic',
              'refresh': 'synthetic-refresh',
            });
          }
          if (request.url.path == '/api/auth/perfil/') {
            return json({'nombre': 'Ana QA', 'email': 'ana@example.invalid'});
          }
          expect(request.url.path, '/api/mascotas/personales/');
          expect(request.method, 'POST');
          writes++;
          sent = jsonDecode(request.body) as Map<String, dynamic>;
          return json({'id_mascota': 91, 'nombre': 'Moka'}, 201);
        }),
      );
      addTearDown(api.close);
      final session = Session(api);
      addTearDown(session.dispose);
      await session.restore();
      await session.login('ana@example.invalid', 'synthetic-password');
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Builder(
            builder: (context) => Scaffold(
              body: TextButton(
                onPressed: () => openPersonalPet(context, session),
                child: const Text('Agregar'),
              ),
            ),
          ),
        ),
      );
      await tester.tap(find.text('Agregar'));
      await tester.pumpAndSettle();
      await tester.enterText(find.byKey(const Key('personal-nombre')), 'Moka');
      await tester.enterText(
        find.byKey(const Key('personal-especie')),
        'Conejo',
      );
      await tester.tap(find.text('Registrar mascota'));
      await tester.pumpAndSettle();
      expect(writes, 1);
      expect(sent, {'nombre': 'Moka', 'especie': 'Conejo'});
      expect(find.text('Agregar'), findsOneWidget);
    },
  );

  testWidgets(
    'A request opens its private decision and history, rather than a public adoption page',
    (tester) async {
      final paths = <String>[];
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          paths.add(request.url.path);
          if (request.url.path == '/api/auth/token/') {
            return json({
              'access': 'synthetic',
              'refresh': 'synthetic-refresh',
            });
          }
          if (request.url.path == '/api/auth/perfil/') {
            return json({'nombre': 'Ana QA', 'email': 'ana@example.invalid'});
          }
          final summary = {
            'id_solicitud_adopcion': 21,
            'mascota_id': 8,
            'mascota__nombre': 'Moka',
            'estado_adopcion__nombre': 'Rechazada',
            'fecha_solicitud': '2026-11-20T12:00:00Z',
          };
          if (request.url.path == '/api/adopcion/solicitudes/mias/') {
            return json({
              'results': [summary],
              'next_cursor': null,
            });
          }
          expect(request.url.path, '/api/adopcion/solicitudes/21/');
          return json({
            ...summary,
            'motivo_decision': 'Se requiere un espacio adecuado.',
            'historial': [
              {
                'estado_nuevo__nombre': 'Rechazada',
                'fecha_cambio': '2026-11-21T12:00:00Z',
                'observacion': 'Revisión concluida por la organización.',
              },
            ],
          });
        }),
      );
      addTearDown(api.close);
      final session = Session(api);
      addTearDown(session.dispose);
      await session.restore();
      await session.login('ana@example.invalid', 'synthetic-password');
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Scaffold(
            body: RequestsScreen(
              api: AdoptionApi(api, session),
              session: session,
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      await tester.tap(find.text('Moka'));
      await tester.pumpAndSettle();
      expect(find.text('Motivo de la decisión'), findsOneWidget);
      expect(find.text('Se requiere un espacio adecuado.'), findsOneWidget);
      expect(
        paths.where((path) => path.startsWith('/api/adopcion/mascotas/')),
        isEmpty,
      );
    },
  );

  testWidgets(
    'Bank instructions follow the selected fund and copy that recipient account',
    (tester) async {
      String? copied;
      tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
        SystemChannels.platform,
        (call) async {
          if (call.method == 'Clipboard.setData') {
            copied = (call.arguments as Map)['text'] as String;
          }
          return null;
        },
      );
      addTearDown(
        () => tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
          SystemChannels.platform,
          null,
        ),
      );
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          if (request.url.path == '/api/auth/token/') {
            return json({
              'access': 'synthetic',
              'refresh': 'synthetic-refresh',
            });
          }
          if (request.url.path == '/api/auth/perfil/') {
            return json({'nombre': 'Ana QA', 'email': 'ana@example.invalid'});
          }
          expect(request.url.path, '/api/fondos/7/datos-aporte/');
          return json({
            'organizacion': 'Refugio Norte QA',
            'titular': 'Titular ficticio',
            'banco': 'Banco ficticio',
            'tipo_cuenta': 'Prueba',
            'numero_cuenta': '000000000007',
            'identificacion_titular': 'QA-0007',
            'prueba': true,
          });
        }),
      );
      addTearDown(api.close);
      final session = Session(api);
      addTearDown(session.dispose);
      await session.restore();
      await session.login('ana@example.invalid', 'synthetic-password');
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Scaffold(
            body: SingleChildScrollView(
              child: BankInstructions(
                session: session,
                path: '/api/fondos/7/datos-aporte/',
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Refugio Norte QA'), findsOneWidget);
      expect(find.textContaining('DATOS FICTICIOS'), findsOneWidget);
      await tester.ensureVisible(find.text('Copiar número de cuenta'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Copiar número de cuenta'));
      await tester.pumpAndSettle();
      expect(copied, '000000000007');
    },
  );
}
