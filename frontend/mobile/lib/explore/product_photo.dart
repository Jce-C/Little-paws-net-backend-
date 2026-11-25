import 'package:flutter/material.dart';

/// Only accepts the bounded public photo route belonging to this product.
/// Missing or malformed optional photos never hide the product information.
class ProductPhoto {
  const ProductPhoto._(this.path, this.width);
  final Uri path;
  final int width;

  static ProductPhoto? fromRow(Map<String, dynamic> row) {
    final value = row['foto'];
    final id = row['id_producto'];
    if (id is! int || id <= 0 || value is! Map) return null;
    final url = value['url'];
    final width = value['ancho'];
    final height = value['alto'];
    final bytes = value['bytes'];
    if (url is! String ||
        width is! int ||
        height is! int ||
        bytes is! int ||
        width < 1 ||
        height < 1 ||
        width > 1280 ||
        height > 1280 ||
        bytes < 1 ||
        bytes > 512 * 1024) {
      return null;
    }
    final path = Uri.tryParse(url);
    if (path == null ||
        path.hasScheme ||
        path.hasAuthority ||
        path.hasFragment ||
        path.path != '/api/catalogo/productos/$id/foto/' ||
        url != '${path.path}?v=${path.queryParameters['v']}' ||
        path.queryParametersAll.length != 1 ||
        path.queryParametersAll['v']?.length != 1 ||
        !RegExp(r'^\d{1,20}$').hasMatch(path.queryParameters['v'] ?? '')) {
      return null;
    }
    return ProductPhoto._(path, width);
  }
}

class PublicProductImage extends StatefulWidget {
  const PublicProductImage({
    super.key,
    required this.row,
    required this.origin,
  });
  final Map<String, dynamic> row;
  final Uri origin;
  @override
  State<PublicProductImage> createState() => _PublicProductImageState();
}

class _PublicProductImageState extends State<PublicProductImage> {
  int _attempt = 0;

  @override
  Widget build(BuildContext context) {
    final photo = ProductPhoto.fromRow(widget.row);
    if (photo == null) return const ProductPhotoPlaceholder();
    final provider = ResizeImage.resizeIfNeeded(
      photo.width < 640 ? photo.width : 640,
      null,
      NetworkImage(widget.origin.resolveUri(photo.path).toString()),
    );
    return Image(
      key: ValueKey('${photo.path}:$_attempt'),
      image: provider,
      fit: BoxFit.contain,
      width: double.infinity,
      height: double.infinity,
      semanticLabel: 'Fotografía de ${widget.row['nombre'] ?? 'producto'}',
      frameBuilder: (context, child, frame, synchronous) =>
          frame != null || synchronous
          ? child
          : const Center(
              child: CircularProgressIndicator(
                semanticsLabel: 'Cargando fotografía',
              ),
            ),
      errorBuilder: (context, error, stack) => Stack(
        fit: StackFit.expand,
        children: [
          const ProductPhotoPlaceholder(failed: true),
          Align(
            alignment: Alignment.bottomRight,
            child: IconButton(
              tooltip: 'Reintentar fotografía',
              onPressed: () async {
                await provider.evict();
                if (mounted) setState(() => _attempt++);
              },
              icon: const Icon(Icons.refresh),
            ),
          ),
        ],
      ),
    );
  }
}

class ProductPhotoPlaceholder extends StatelessWidget {
  const ProductPhotoPlaceholder({super.key, this.failed = false});
  final bool failed;
  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) {
      final compact = constraints.maxHeight < 160 || constraints.maxWidth < 160;
      final label = failed
          ? 'No se pudo cargar la foto'
          : 'Sin fotografía publicada';
      return Semantics(
        label: label,
        child: ColoredBox(
          color: const Color(0xffe7ecfa),
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.shopping_bag_outlined, size: 32),
                if (!compact) ...[
                  const SizedBox(height: 8),
                  Text(
                    label,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ],
            ),
          ),
        ),
      );
    },
  );
}
