import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/adoption/pet_gallery.dart';
import 'package:little_paws_net/core/api_client.dart';

Map<String, Object> photo(String path) => {
  'url': '$path?v=123',
  'ancho': 640,
  'alto': 480,
  'bytes': 2000,
};
Map<String, Object?> detail() => {
  'id_mascota': 4,
  'nombre': 'Mascota QA',
  'especie': 'Perro',
  'edad_meses': 20,
  'edad_estimada': true,
  'organizacion': 'Organización QA',
  'ciudad': 'Ciudad QA',
  'custodia_desde': '2026-11-18T00:00:00Z',
  'foto': photo('/api/adopcion/mascotas/4/foto/'),
};
void main() {
  test('Legacy cover stays compatible and gallery accepts only this pet public routes', () {
    expect(PetDetail.fromJson(detail()).photos.length, 1);
    final row = detail()
      ..['fotos'] = [
        photo('/api/adopcion/mascotas/4/foto/'),
        photo('/api/adopcion/mascotas/4/fotos/9/'),
      ];
    expect(PetDetail.fromJson(row).photos.length, 2);
    for (final path in [
      '/api/adopcion/mascotas/5/fotos/9/',
      '/api/seguridad/archivos/9/',
      'https://other.invalid/api/adopcion/mascotas/4/fotos/9/',
    ]) {
      row['fotos'] = [photo(path)];
      expect(() => PetDetail.fromJson(row), throwsA(isA<ApiException>()));
    }
    row['fotos'] = List.filled(7, photo('/api/adopcion/mascotas/4/foto/'));
    expect(() => PetDetail.fromJson(row), throwsA(isA<ApiException>()));
  });
  testWidgets(
    'Gallery swipes between authorized photos and announces position',
    (tester) async {
      final row = detail()
        ..['fotos'] = [
          photo('/api/adopcion/mascotas/4/foto/'),
          photo('/api/adopcion/mascotas/4/fotos/9/'),
        ];
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 320,
              child: PetGallery(
                detail: PetDetail.fromJson(row),
                origin: Uri.parse('https://backend.example.invalid'),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Foto 1 de 2'), findsOneWidget);
      await tester.drag(
        find.byKey(const Key('pet-photo-carousel')),
        const Offset(-300, 0),
      );
      await tester.pumpAndSettle();
      expect(find.text('Foto 2 de 2'), findsOneWidget);
      await tester.tap(find.byTooltip('Ver foto 1'));
      await tester.pumpAndSettle();
      expect(find.text('Foto 1 de 2'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
}
