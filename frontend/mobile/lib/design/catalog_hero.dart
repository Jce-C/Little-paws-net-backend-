import 'package:flutter/material.dart';

import 'lpn_theme.dart';
import 'animal_filter_icon.dart';

/// Content and filters stay outside the illustration.
class CatalogHero extends StatelessWidget {
  const CatalogHero({
    super.key,
    required this.species,
    required this.selected,
    required this.onSelected,
    this.counter,
  });
  final List<String> species;
  final String selected;
  final ValueChanged<String> onSelected;
  final String? counter;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      Padding(
        padding: const EdgeInsets.fromLTRB(20, 8, 20, 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'ADOPTAR',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                letterSpacing: .8,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Un hogar cambia\ntoda una vida.',
              style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.w600,
                height: 1.05,
                letterSpacing: -1.2,
              ),
            ),
            if (counter != null) ...[
              const SizedBox(height: 12),
              Text(counter!, style: Theme.of(context).textTheme.bodySmall),
            ],
          ],
        ),
      ),
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: SizedBox(
            height: ((MediaQuery.sizeOf(context).width - 40) * 414 / 736).clamp(
              96,
              (MediaQuery.sizeOf(context).height * .23).clamp(96, 240),
            ),
            child: Image.asset(
              'assets/adoption-banner.webp',
              key: const Key('catalog-hero'),
              fit: BoxFit.contain,
              semanticLabel: 'Un perro y un gato contemplan el atardecer',
            ),
          ),
        ),
      ),
      if (species.isNotEmpty)
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Row(
              children: [
                for (final value in ['', ...species])
                  Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      avatar: AnimalFilterIcon(
                        species: value,
                        color: value == selected
                            ? LpnColors.paper
                            : LpnColors.ink,
                      ),
                      label: Text(value.isEmpty ? 'Todos' : value),
                      selected: value == selected,
                      onSelected: (_) {
                        if (value != selected) onSelected(value);
                      },
                      showCheckmark: false,
                      materialTapTargetSize: MaterialTapTargetSize.padded,
                      selectedColor: LpnColors.charcoal,
                      labelStyle: TextStyle(
                        fontSize: 14,
                        color: value == selected
                            ? LpnColors.paper
                            : LpnColors.ink,
                      ),
                      side: BorderSide(
                        color: value == selected
                            ? LpnColors.charcoal
                            : LpnColors.controlEdge,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
    ],
  );
}
