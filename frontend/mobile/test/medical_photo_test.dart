import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/pets/owned_pets_api.dart';

void main() {
  test(
    'Protected portrait accepts only bounded inline WebP, never remote URLs',
    () {
      final bytes = [
        ...ascii.encode('RIFF'),
        0,
        0,
        0,
        0,
        ...ascii.encode('WEBP'),
        0,
        0,
      ];
      final value = {
        'tipo': 'image/webp',
        'ancho': 160,
        'alto': 80,
        'datos': base64Encode(bytes),
      };
      expect(medicalPhoto(value), isNotNull);
      for (final invalid in [
        null,
        {'url': 'https://example.invalid/private'},
        {...value, 'datos': 'x' * 44001},
        {...value, 'alto': 161},
        {...value, 'tipo': 'image/svg+xml'},
        {...value, 'datos': 'invalid base64'},
      ]) {
        expect(medicalPhoto(invalid), isNull);
      }
    },
  );
}
