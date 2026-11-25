import 'package:flutter/material.dart';

import 'adoption_api.dart';
import 'public_pet_image.dart';

class PetGallery extends StatefulWidget {
  const PetGallery({super.key, required this.detail, required this.origin});
  final PetDetail detail;
  final Uri origin;
  @override
  State<PetGallery> createState() => _PetGalleryState();
}

class _PetGalleryState extends State<PetGallery> {
  final _controller = PageController();
  int _page = 0;
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final photos = widget.detail.photos;
    return Column(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(28),
          child: photos.isEmpty
              ? const SizedBox(
                  height: 120,
                  width: double.infinity,
                  child: PetPlaceholder(),
                )
              : AspectRatio(
                  aspectRatio: 1.2,
                  child: PageView.builder(
                    key: const Key('pet-photo-carousel'),
                    controller: _controller,
                    itemCount: photos.length,
                    allowImplicitScrolling: true,
                    onPageChanged: (index) => setState(() => _page = index),
                    itemBuilder: (context, index) => PublicPetImage(
                      pet: Pet(
                        id: widget.detail.pet.id,
                        name: widget.detail.pet.name,
                        species: widget.detail.pet.species,
                        photo: photos[index],
                      ),
                      origin: widget.origin,
                      decodeWidth: 1280,
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
        ),
        const SizedBox(height: 8),
        if (photos.isEmpty)
          const Text(
            'Foto pública aún no disponible',
            style: TextStyle(fontSize: 14),
          )
        else
          Semantics(
            liveRegion: true,
            child: Text(
              'Foto ${_page + 1} de ${photos.length}',
              style: const TextStyle(fontSize: 14),
            ),
          ),
        if (photos.length > 1)
          Wrap(
            alignment: WrapAlignment.center,
            children: [
              for (var index = 0; index < photos.length; index++)
                IconButton(
                  tooltip: 'Ver foto ${index + 1}',
                  isSelected: _page == index,
                  icon: Icon(
                    _page == index
                        ? Icons.radio_button_checked
                        : Icons.radio_button_unchecked,
                    size: 16,
                  ),
                  onPressed: () {
                    if (MediaQuery.disableAnimationsOf(context)) {
                      _controller.jumpToPage(index);
                    } else {
                      _controller.animateToPage(
                        index,
                        duration: Duration(
                          milliseconds: MediaQuery.disableAnimationsOf(context)
                              ? 0
                              : 240,
                        ),
                        curve: Curves.easeOutCubic,
                      );
                    }
                  },
                ),
            ],
          ),
      ],
    );
  }
}
