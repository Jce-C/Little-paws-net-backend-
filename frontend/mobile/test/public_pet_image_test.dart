import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/adoption/public_pet_image.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';

Map<String, Object?> data({Object? photo}) => {
  'id_mascota': 4,
  'nombre': 'Luna',
  'especie': 'Perro',
  'foto': photo,
};
Map<String, Object?> descriptor({
  String url = '/api/adopcion/mascotas/4/foto/?v=1234',
}) => {'url': url, 'ancho': 640, 'alto': 480, 'bytes': 8000};
Widget view(Pet pet) => MaterialApp(
  theme: lpnTheme(),
  home: Scaffold(
    body: Center(
      child: SizedBox(
        width: 210,
        height: 170,
        child: PublicPetImage(
          pet: pet,
          origin: Uri.parse('http://localhost:8016'),
        ),
      ),
    ),
  ),
);

class _ProbeClient extends Fake implements HttpClient {
  final List<Uri> requests = [];
  @override
  set autoUncompress(bool value) {}
  @override
  Future<HttpClientRequest> getUrl(Uri url) async {
    requests.add(url);
    throw const SocketException('Sin conexión de prueba');
  }
}

class _ProbeOverrides extends HttpOverrides {
  _ProbeOverrides(this.client);
  final HttpClient client;
  @override
  HttpClient createHttpClient(SecurityContext? context) => client;
}

void main() {
  test('Missing photo stays compatible and valid descriptor keeps only public data', () {
    expect(Pet.fromJson(data()).photo, isNull);
    final photo = Pet.fromJson(data(photo: descriptor())).photo!;
    expect(photo.width, 640);
    expect(photo.height, 480);
    expect(photo.bytes, 8000);
    expect(photo.path.toString(), '/api/adopcion/mascotas/4/foto/?v=1234');
  });

  test(
    'Photo rejects external URLs, private routes and inconsistent dimensions',
    () {
      for (final invalid in [
        descriptor(
          url: 'https://other.invalid/api/adopcion/mascotas/4/foto/?v=1',
        ),
        descriptor(url: '//other.invalid/foto/?v=1'),
        descriptor(url: '/api/adopcion/mascotas/5/foto/?v=1'),
        descriptor(url: '/api/seguridad/documentos/1/?v=1'),
        descriptor(url: '/api/adopcion/mascotas/4/foto/?v=1&token=x'),
        descriptor(url: '/api/adopcion/mascotas/4/foto/?v=1&v=2'),
        descriptor(url: '/api/adopcion/mascotas/4/foto/?v=abc'),
        {...descriptor(), 'ancho': 1281},
        {...descriptor(), 'alto': 0},
        {...descriptor(), 'bytes': 524289},
        {...descriptor(), 'ancho': '640'},
      ]) {
        expect(
          () => Pet.fromJson(data(photo: invalid)),
          throwsA(isA<ApiException>()),
        );
      }
    },
  );

  testWidgets('A missing photo creates no network image request', (
    tester,
  ) async {
    final probe = _ProbeClient();
    await HttpOverrides.runWithHttpOverrides(() async {
      await tester.pumpWidget(view(Pet.fromJson(data())));
      await tester.pumpAndSettle();
      expect(find.byType(PetPlaceholder), findsOneWidget);
      expect(find.byType(Image), findsNothing);
      expect(probe.requests, isEmpty);
    }, _ProbeOverrides(probe));
  });

  testWidgets(
    'Failed photo offers explicit retry and removal stops rendering it',
    (tester) async {
      final probe = _ProbeClient();
      await HttpOverrides.runWithHttpOverrides(() async {
        final pet = Pet.fromJson(data(photo: descriptor()));
        await tester.pumpWidget(view(pet));
        await tester.pumpAndSettle();
        expect(find.byTooltip('Reintentar fotografía'), findsOneWidget);
        expect(probe.requests.length, 1);
        expect(
          probe.requests.single.toString(),
          'http://localhost:8016/api/adopcion/mascotas/4/foto/?v=1234',
        );
        await tester.tap(find.byTooltip('Reintentar fotografía'));
        await tester.pumpAndSettle();
        expect(probe.requests.length, 2);
        await tester.pumpWidget(view(Pet.fromJson(data())));
        await tester.pumpAndSettle();
        expect(find.byType(Image), findsNothing);
        expect(find.byTooltip('Reintentar fotografía'), findsNothing);
        expect(probe.requests.length, 2);
        expect(tester.takeException(), isNull);
      }, _ProbeOverrides(probe));
    },
  );
}
