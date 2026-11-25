import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/explore/product_photo.dart';
import 'package:little_paws_net/design/refined_surfaces.dart';

Map<String, dynamic> product({String? url}) => {
  'id_producto': 4,
  'nombre': 'Producto QA',
  'precio': '10000',
  'existencias': 2,
  'categoria': 'Alimento',
  'tienda': 'Tienda QA',
  'foto': {
    'url': url ?? '/api/catalogo/productos/4/foto/?v=123',
    'ancho': 1280,
    'alto': 640,
    'bytes': 4000,
  },
};

void main() {
  test(
    'Accepts only this product relative public image and bounded metadata',
    () {
      expect(ProductPhoto.fromRow(product())!.width, 1280);
      for (final url in [
        'https://evil.invalid/api/catalogo/productos/4/foto/?v=123',
        '//evil.invalid/api/catalogo/productos/4/foto/?v=123',
        '/api/catalogo/productos/5/foto/?v=123',
        '/api/seguridad/archivos/4/?v=123',
        '/api/catalogo/productos/4/foto/?v=123&v=456',
        '/api/catalogo/productos/4/foto/?v=123&token=private',
        '/api/catalogo/productos/4/foto/?v=123#private',
        '/api/catalogo/productos/4/foto/',
        '/api/catalogo/productos/4/../4/foto/?v=123',
      ]) {
        expect(ProductPhoto.fromRow(product(url: url)), isNull, reason: url);
      }
      for (final field in ['ancho', 'alto', 'bytes']) {
        final row = product();
        (row['foto'] as Map)[field] = field == 'bytes' ? 524289 : 1281;
        expect(ProductPhoto.fromRow(row), isNull);
        (row['foto'] as Map)[field] = 0;
        expect(ProductPhoto.fromRow(row), isNull);
      }
      expect(ProductPhoto.fromRow(product()..remove('foto')), isNull);
      expect(ProductPhoto.fromRow(product()..['foto'] = 'malformed'), isNull);
    },
  );

  testWidgets(
    'Legacy product remains legible and opens with no photo request',
    (tester) async {
      var opened = 0;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MediaQuery(
              data: const MediaQueryData(textScaler: TextScaler.linear(1.5)),
              child: SizedBox(
                width: 320,
                child: ListView(
                  children: [
                    ProductCatalogCard(
                      row: product()..remove('foto'),
                      origin: Uri.parse('https://example.invalid'),
                      onOpen: () => opened++,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
      expect(find.byType(ProductPhotoPlaceholder), findsOneWidget);
      expect(find.byType(Image), findsNothing);
      expect(find.text('Producto QA'), findsOneWidget);
      await tester.tap(find.text('Ver producto'));
      expect(opened, 1);
      expect(tester.takeException(), isNull);
    },
  );
}
