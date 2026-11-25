import 'package:flutter/material.dart';

import '../design/lpn_theme.dart';
import 'adoption_api.dart';

/// Figma 128:502 facts, with flexible height for real values and system text.
class PublicPetFacts extends StatelessWidget {
  const PublicPetFacts({super.key, required this.detail});
  final PetDetail detail;

  Widget _fact(
    String label,
    String value, {
    IconData icon = Icons.pets_outlined,
  }) => Container(
    padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(
      color: LpnColors.sageSoft,
      borderRadius: BorderRadius.circular(24),
    ),
    child: Row(
      children: [
        Icon(icon, size: 22, color: LpnColors.ink),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 14,
                  height: 1.4,
                  color: LpnColors.ink,
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, box) {
      final columns =
          box.maxWidth >= 320 &&
              MediaQuery.textScalerOf(context).scale(10) <= 16
          ? 2
          : 1;
      final width = (box.maxWidth - (columns - 1) * 20) / columns;
      return Wrap(
        spacing: 20,
        runSpacing: 12,
        children: [
          SizedBox(
            width: width,
            child: _fact('EDAD', detail.ageLabel, icon: Icons.cake_outlined),
          ),
          SizedBox(
            width: width,
            child: _fact(
              'TAMAÑO',
              detail.size ?? 'Sin registrar',
              icon: Icons.straighten_outlined,
            ),
          ),
          if (detail.sex != null)
            SizedBox(width: width, child: _fact('SEXO', detail.sex!)),
        ],
      );
    },
  );
}

/// Only verified public facts are shown; no invented rescue or medical events.
class PublicPetStory extends StatelessWidget {
  const PublicPetStory({super.key, required this.detail});
  final PetDetail detail;

  Widget _step({
    required Widget marker,
    required Widget child,
    required bool last,
  }) => IntrinsicHeight(
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SizedBox(
          width: 35,
          child: Column(
            children: [
              marker,
              if (!last)
                Expanded(
                  child: Center(
                    child: Container(width: 2, color: const Color(0xff603d00)),
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Padding(
            padding: EdgeInsets.only(top: 8, bottom: last ? 0 : 20),
            child: child,
          ),
        ),
      ],
    ),
  );

  @override
  Widget build(BuildContext context) {
    final solid =
        MediaQuery.highContrastOf(context) ||
        (Theme.of(context).extension<LpnMaterials>()?.reduceTransparency ??
            false);
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 520),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'SU HISTORIA',
              style: TextStyle(
                fontSize: 15,
                height: 1.4,
                color: Color(0xff5f513f),
              ),
            ),
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 22),
              constraints: const BoxConstraints(minHeight: 0),
              decoration: BoxDecoration(
                // Resolve the reference's half-opacity cream on the canvas,
                // keeping the shadow behind it from tinting the entire card.
                color: solid
                    ? LpnColors.paper
                    : Color.alphaBlend(
                        const Color(0x80fcf0d3),
                        LpnColors.canvas,
                      ),
                borderRadius: BorderRadius.circular(28),
                border: Border.all(color: Colors.white),
                boxShadow: solid
                    ? null
                    : const [
                        BoxShadow(
                          color: Color(0x14754812),
                          offset: Offset(0, 4),
                          blurRadius: 10,
                          spreadRadius: 5,
                        ),
                      ],
              ),
              child: DefaultTextStyle.merge(
                style: const TextStyle(
                  fontSize: 14,
                  height: 1.5,
                  color: Color(0xff5f513f),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    _step(
                      marker: Image.asset(
                        'assets/history-paw.png',
                        width: 35,
                        height: 35,
                        fit: BoxFit.cover,
                        alignment: Alignment.bottomCenter,
                        excludeFromSemantics: true,
                      ),
                      last: false,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Bajo el cuidado de'),
                          Text(detail.organization),
                          const SizedBox(height: 4),
                          Text(
                            'Desde ${MaterialLocalizations.of(context).formatMediumDate(detail.custodySince.toLocal())}',
                          ),
                          Text('Ciudad: ${detail.city}'),
                        ],
                      ),
                    ),
                    _step(
                      marker: Image.asset(
                        'assets/history-dot.png',
                        width: 28,
                        height: 27,
                        excludeFromSemantics: true,
                      ),
                      last: true,
                      child: const Text('Disponible para adopción'),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
