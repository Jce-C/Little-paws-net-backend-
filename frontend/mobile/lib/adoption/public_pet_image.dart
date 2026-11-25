import 'package:flutter/material.dart';

import 'adoption_api.dart';

class PublicPetImage extends StatefulWidget {
  const PublicPetImage({
    super.key,
    required this.pet,
    required this.origin,
    this.decodeWidth = 640,
    this.fit = BoxFit.cover,
  });
  final Pet pet;
  final Uri origin;
  final int decodeWidth;
  final BoxFit fit;
  @override
  State<PublicPetImage> createState() => _PublicPetImageState();
}

class _PublicPetImageState extends State<PublicPetImage> {
  int _attempt = 0;
  ImageProvider<Object> get _provider {
    final photo = widget.pet.photo!;
    final width = photo.width < widget.decodeWidth
        ? photo.width
        : widget.decodeWidth;
    return ResizeImage.resizeIfNeeded(
      width,
      null,
      NetworkImage(widget.origin.resolveUri(photo.path).toString()),
    );
  }

  Future<void> _retry() async {
    await _provider.evict();
    if (mounted) setState(() => _attempt++);
  }

  @override
  Widget build(BuildContext context) {
    if (widget.pet.photo == null) return const PetPlaceholder();
    return Image(
      key: ValueKey('${widget.pet.photo!.path}:$_attempt'),
      image: _provider,
      width: double.infinity,
      height: double.infinity,
      fit: widget.fit,
      filterQuality: FilterQuality.medium,
      semanticLabel: 'Fotografía de ${widget.pet.name}',
      gaplessPlayback: false,
      frameBuilder: (context, child, frame, synchronous) =>
          frame != null || synchronous
          ? child
          : const ColoredBox(
              color: Color(0xffe7ecfa),
              child: Center(
                child: CircularProgressIndicator(
                  semanticsLabel: 'Cargando fotografía',
                ),
              ),
            ),
      errorBuilder: (context, error, stack) => Stack(
        fit: StackFit.expand,
        children: [
          const PetPlaceholder(),
          Align(
            alignment: Alignment.bottomRight,
            child: IconButton(
              onPressed: _retry,
              tooltip: 'Reintentar fotografía',
              icon: const Icon(Icons.refresh),
            ),
          ),
        ],
      ),
    );
  }
}

class PetPlaceholder extends StatelessWidget {
  const PetPlaceholder({super.key});

  @override
  Widget build(BuildContext context) => ColoredBox(
    color: const Color(0xffe7ecfa),
    child: Center(
      child: Icon(
        Icons.pets,
        size: 44,
        color: Theme.of(context).colorScheme.primary,
        semanticLabel: 'Sin foto disponible',
      ),
    ),
  );
}
