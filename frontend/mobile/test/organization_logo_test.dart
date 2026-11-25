import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/explore/organization_logo.dart';
import 'package:little_paws_net/explore/organization_public_info.dart';
import 'package:little_paws_net/explore/explore_screens.dart';

Map<String, dynamic> organization({Object? logo}) => {
  'id': 7,
  'nombre': 'Organización de protección animal de ejemplo',
  'tipo': 'Fundación',
  'ciudad': 'Riohacha',
  'logo': logo,
  'perfil_publico': {
    'descripcion': 'Descripción pública autorizada.',
    'servicios': 'Orientación para adopción y bienestar animal.',
    'telefono': '+57 300 123 4567',
    'correo': 'publico@example.invalid',
    'sitio_web': 'https://example.invalid/',
  },
  'whatsapp': 'Contacto interno que nunca debe usarse',
};
Map<String, dynamic> logo() => {
  'url': '/api/red/organizaciones/7/logo/?v=1795380000123456',
  'ancho': 512,
  'alto': 256,
  'bytes': 20000,
};

void main() {
  test('Logo accepts only its own bounded public route, never external or private paths', () {
    expect(
      OrganizationLogoData.fromRow(organization(logo: logo()))!.path.path,
      '/api/red/organizaciones/7/logo/',
    );
    expect(OrganizationLogoData.fromRow(organization()), isNull);
    for (final change in [
      {'url': 'https://example.invalid/logo.webp'},
      {'url': '/api/red/organizaciones/8/logo/'},
      {'url': '/media/private/logo.webp'},
      {'url': '/api/red/organizaciones/7/logo/?v=1&token=private'},
      {'ancho': 513},
      {'alto': 0},
      {'bytes': 96 * 1024 + 1},
    ]) {
      expect(
        OrganizationLogoData.fromRow(
          organization(logo: {...logo(), ...change}),
        ),
        isNull,
      );
    }
  });

  for (final sample in [
    (320.0, 1.0),
    (320.0, 2.0),
    (430.0, 1.0),
    (720.0, 2.0),
  ]) {
    testWidgets(
      'Organization identity keeps full name and fixed logo space at $sample',
      (tester) async {
        tester.view.physicalSize = Size(sample.$1, 1000);
        tester.view.devicePixelRatio = 1;
        addTearDown(tester.view.resetPhysicalSize);
        addTearDown(tester.view.resetDevicePixelRatio);
        await tester.pumpWidget(
          MaterialApp(
            theme: lpnTheme(),
            home: MediaQuery(
              data: MediaQueryData(
                size: Size(sample.$1, 1000),
                textScaler: TextScaler.linear(sample.$2),
              ),
              child: Scaffold(
                body: ListView(
                  padding: const EdgeInsets.all(20),
                  children: [
                    OrganizationIdentity(
                      row: organization(),
                      origin: Uri.parse('https://example.invalid'),
                    ),
                    OrganizationPublicInfo(row: organization(), compact: true),
                  ],
                ),
              ),
            ),
          ),
        );
        await tester.pumpAndSettle();
        expect(find.text(organization()['nombre']), findsOneWidget);
        expect(find.byIcon(Icons.volunteer_activism_outlined), findsOneWidget);
        expect(
          tester.getSize(find.byType(OrganizationLogo)),
          const Size(64, 64),
        );
        expect(find.text('+57 300 123 4567'), findsNothing);
        expect(tester.takeException(), isNull);
      },
    );
  }

  testWidgets(
    'Directory detail needs no additional API query and never shows internal contacts',
    (tester) async {
      var requests = 0;
      final api = ApiClient(
        base: Uri.parse('http://localhost:8016'),
        client: MockClient((request) async {
          requests++;
          return http.Response(
            jsonEncode([organization()]),
            200,
            headers: {'content-type': 'application/json; charset=utf-8'},
          );
        }),
      );
      addTearDown(api.close);
      await tester.pumpWidget(
        MaterialApp(
          theme: lpnTheme(),
          home: PublicListScreen(
            api: api,
            path: '/api/red/organizaciones/',
            title: 'Nuestra red',
            kind: 'organizations',
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(requests, 1);
      final action = find.text('Ver contacto y servicios');
      await tester.scrollUntilVisible(action, 150);
      await tester.tap(action);
      await tester.pumpAndSettle();
      expect(find.text('+57 300 123 4567'), findsOneWidget);
      expect(find.text('Contacto interno que nunca debe usarse'), findsNothing);
      expect(requests, 1);
      await tester.pageBack();
      await tester.pumpAndSettle();
      await tester.tap(find.byTooltip('Actualizar directorio'));
      await tester.pumpAndSettle();
      expect(requests, 2);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('Copy contact uses the explicitly public value only', (
    tester,
  ) async {
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
    await tester.pumpWidget(
      MaterialApp(
        theme: lpnTheme(),
        home: Scaffold(
          body: ListView(
            children: [OrganizationPublicInfo(row: organization())],
          ),
        ),
      ),
    );
    await tester.tap(find.byTooltip('Copiar teléfono público'));
    await tester.pumpAndSettle();
    expect(copied, '+57 300 123 4567');
    expect(find.text('Teléfono público copiado.'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
