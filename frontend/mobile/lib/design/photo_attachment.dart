import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

class PhotoAttachment extends StatefulWidget {
  const PhotoAttachment({
    super.key,
    required this.value,
    required this.onChanged,
    this.enabled = true,
    this.public = false,
    this.choose,
    this.onBusyChanged,
  });
  final Uint8List? value;
  final ValueChanged<Uint8List?> onChanged;
  final ValueChanged<bool>? onBusyChanged;
  final bool enabled, public;
  final Future<Uint8List?> Function(ImageSource)? choose;
  @override
  State<PhotoAttachment> createState() => _PhotoAttachmentState();
}

class _PhotoAttachmentState extends State<PhotoAttachment> {
  bool _busy = false;
  String? _error;
  Future<void> _pick(ImageSource source) async {
    if (_busy || !widget.enabled) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    widget.onBusyChanged?.call(true);
    try {
      Uint8List? bytes;
      if (widget.choose != null) {
        bytes = await widget.choose!(source);
      } else {
        final file = await ImagePicker().pickImage(
          source: source,
          maxWidth: 1200,
          maxHeight: 1200,
          imageQuality: 80,
        );
        if (file != null) bytes = await file.readAsBytes();
      }
      if (!mounted || !widget.enabled || bytes == null) return;
      if (bytes.isEmpty || bytes.length > 5 * 1024 * 1024) throw Exception();
      widget.onChanged(bytes);
    } on Exception {
      if (mounted) {
        setState(
          () => _error = 'No pudimos abrir la foto. Revisa los permisos o selecciona otra imagen de hasta 5 MB.',
        );
      }
    } finally {
      if (mounted) {
        widget.onBusyChanged?.call(false);
        setState(() => _busy = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      if (widget.value != null)
        ClipRRect(
          borderRadius: BorderRadius.circular(18),
          child: Image.memory(
            widget.value!,
            height: 160,
            fit: BoxFit.contain,
            semanticLabel: 'Vista previa de la fotografía',
            errorBuilder: (_, error, stack) => const Padding(
              padding: EdgeInsets.all(16),
              child: Text('No se puede previsualizar esta imagen.'),
            ),
          ),
        ),
      Wrap(
        spacing: 8,
        runSpacing: 4,
        children: [
          OutlinedButton.icon(
            onPressed: widget.enabled && !_busy
                ? () => _pick(ImageSource.camera)
                : null,
            icon: const Icon(Icons.camera_alt_outlined),
            label: const Text('Tomar fotografía'),
          ),
          OutlinedButton.icon(
            onPressed: widget.enabled && !_busy
                ? () => _pick(ImageSource.gallery)
                : null,
            icon: const Icon(Icons.photo_library_outlined),
            label: const Text('Seleccionar de galería'),
          ),
          if (widget.value != null)
            TextButton.icon(
              onPressed: widget.enabled && !_busy
                  ? () => widget.onChanged(null)
                  : null,
              icon: const Icon(Icons.delete_outline),
              label: const Text('Quitar foto'),
            ),
        ],
      ),
      if (widget.public)
        const Text(
          'La foto se mostrará con el reporte público. Evita rostros, placas y datos personales.',
        ),
      if (_busy) const LinearProgressIndicator(),
      if (_error != null) Text(_error!, semanticsLabel: _error),
    ],
  );
}
