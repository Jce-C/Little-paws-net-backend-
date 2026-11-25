import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/public_avatar.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/design/refined_surfaces.dart';

const descriptor = {
  'url': '/api/comunidad/perfiles/00000000-0000-4000-8000-000000000001/foto/',
  'ancho': 256,
  'alto': 128,
  'bytes': 100,
};
final pixel = base64Decode(
  'iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAE0lEQVR4nGNkaGDACpiwCw9WCQBqCACQJ5at+QAAAABJRU5ErkJggg==',
);
http.Response json(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json'},
);

void main() {
  test('Avatar accepts only bounded same-origin UUID resource metadata', () {
    expect(AvatarData.parse(descriptor), isNotNull);
    for (final path in [
      'https://evil.invalid/a',
      '//evil.invalid/a',
      '/api/comunidad/perfiles/1/foto/',
      '${descriptor['url']}?private=true',
    ]) {
      expect(AvatarData.parse({...descriptor, 'url': path}), isNull);
    }
    expect(AvatarData.parse({...descriptor, 'bytes': 65537}), isNull);
    expect(AvatarData.parse({...descriptor, 'ancho': 257}), isNull);
  });
  test('Multipart upload retains bearer, consent, bounded bytes and a neutral filename', () async {
    final api = ApiClient(
      base: Uri.parse('https://api.example.invalid'),
      client: MockClient((request) async {
        expect(request.headers['authorization'], 'Bearer private-token');
        expect(
          request.headers['content-type'],
          startsWith('multipart/form-data; boundary='),
        );
        final body = latin1.decode(request.bodyBytes);
        expect(body, contains('name="confirmar_publicacion"'));
        expect(body, contains('true'));
        expect(body, contains('filename="foto.png"'));
        return json({'foto_publica': descriptor}, 201);
      }),
    );
    await api.uploadProfilePhoto(pixel, token: 'private-token');
    expect(
      () => api.uploadProfilePhoto([], token: 'x'),
      throwsA(isA<ApiException>()),
    );
    api.close();
  });
  for (final scale in [1.0, 2.0]) {
    testWidgets(
      'Photo selection is local until explicit consent, scale $scale',
      (tester) async {
        tester.view.physicalSize = const Size(320, 720);
        tester.view.devicePixelRatio = 1;
        tester.platformDispatcher.textScaleFactorTestValue = scale;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);
        addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
        var writes = 0;
        final api = ApiClient(
          base: Uri.parse('http://localhost:8016'),
          client: MockClient((request) async {
            if (request.url.path == '/api/auth/token/') {
              return json({'access': 'access', 'refresh': 'refresh'});
            }
            if (request.url.path == '/api/auth/perfil/') {
              return json({
                'nombre': 'QA',
                'email': 'qa@example.invalid',
                'telefono': '',
              });
            }
            if (request.url.path == '/api/seguridad/mis-accesos/') {
              return json({
                'roles_globales': ['CIUDADANO'],
                'entidades': [],
              });
            }
            if (request.url.path == '/api/auth/foto-publica/') {
              if (request.method == 'POST') {
                writes++;
                return json({'foto_publica': descriptor}, 201);
              }
              return json({'foto_publica': null});
            }
            throw StateError('Unexpected ${request.url}');
          }),
        );
        final session = Session(api);
        await session.restore();
        await session.login('qa@example.invalid', 'qa-password');
        await tester.pumpWidget(
          MaterialApp(
            theme: lpnTheme(),
            home: AvatarScreen(
              session: session,
              choose: () async => Uint8List.fromList(pixel),
            ),
          ),
        );
        await tester.pumpAndSettle();
        await tester.tap(find.text('Elegir foto'));
        await tester.pumpAndSettle();
        expect(writes, 0);
        await tester.tap(find.text('Publicar foto'));
        await tester.pumpAndSettle();
        expect(writes, 0);
        expect(
          tester
              .widget<FilledButton>(
                find.widgetWithText(FilledButton, 'Publicar foto'),
              )
              .onPressed,
          isNull,
        );
        await tester.scrollUntilVisible(
          find.byType(Checkbox),
          100,
          scrollable: find.byType(Scrollable).first,
        );
        await tester.pumpAndSettle();
        await tester.tap(find.byType(Checkbox));
        await tester.pumpAndSettle();
        await tester.tap(find.text('Publicar foto'));
        await tester.pumpAndSettle();
        expect(writes, 1);
        expect(find.text('Foto publicada.'), findsOneWidget);
        expect(tester.takeException(), isNull);
        await tester.pumpWidget(const SizedBox.shrink());
        session.dispose();
        api.close();
      },
    );
  }
  testWidgets(
    'Store places product media to the left of decision information',
    (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: Scaffold(
            body: SizedBox(
              width: 430,
              child: ProductCatalogCard(
                row: const {
                  'nombre': 'Kit de paseo',
                  'categoria': 'Accesorios',
                  'tienda': 'Tienda QA',
                  'precio': '35000',
                  'existencias': 4,
                },
                origin: Uri.parse('https://api.example.invalid'),
                onOpen: () {},
              ),
            ),
          ),
        ),
      );
      final image = find.byType(ClipRRect).first;
      expect(
        tester.getRect(image).right,
        lessThan(tester.getRect(find.text('Kit de paseo')).left),
      );
      expect(tester.takeException(), isNull);
    },
  );
}
