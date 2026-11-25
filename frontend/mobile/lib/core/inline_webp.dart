import 'dart:convert';
import 'dart:typed_data';

Uint8List? inlineWebp(Object? value) {
  if (value is! Map || value['tipo'] != 'image/webp') return null;
  final data = value['datos'];
  if (data is! String || data.length > 44000) return null;
  for (final field in ['ancho', 'alto']) {
    final n = value[field];
    if (n is! int || n < 1 || n > 160) return null;
  }
  try {
    final bytes = base64Decode(data);
    if (bytes.length < 12 ||
        bytes.length > 32768 ||
        ascii.decode(bytes.sublist(0, 4), allowInvalid: true) != 'RIFF' ||
        ascii.decode(bytes.sublist(8, 12), allowInvalid: true) != 'WEBP') {
      return null;
    }
    return bytes;
  } on FormatException {
    return null;
  }
}
