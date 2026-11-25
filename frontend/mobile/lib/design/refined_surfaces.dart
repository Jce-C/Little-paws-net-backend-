import '../explore/cop_amount.dart';
import '../explore/product_presentation.dart';

import 'package:flutter/material.dart';

import 'lpn_theme.dart';
import 'form_surfaces.dart';
import 'decision_card.dart';
import '../explore/product_photo.dart';

/// A shared page backdrop; the illustration is not a scroll-list header.
class HomeBackdrop extends StatelessWidget {
  const HomeBackdrop({super.key, required this.child});
  final Widget child;
  static double clearance(BuildContext context) =>
      (MediaQuery.sizeOf(context).width * .54).clamp(168.0, 240.0);
  @override
  Widget build(BuildContext context) => ColoredBox(
    color: LpnColors.canvas,
    child: SizedBox.expand(key: const Key('home-page-backdrop'), child: child),
  );
}

class IntegratedHomeHeader extends StatelessWidget {
  const IntegratedHomeHeader({super.key});
  @override
  Widget build(BuildContext context) => Column(
    key: const Key('integrated-home-header'),
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      SizedBox(
        height: HomeBackdrop.clearance(context),
        child: ShaderMask(
          blendMode: BlendMode.dstIn,
          shaderCallback: (rect) => const LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Colors.white, Colors.white, Colors.transparent],
            stops: [0, .72, 1],
          ).createShader(rect),
          child: Image.asset(
            'assets/home-pets.webp',
            fit: BoxFit.cover,
            alignment: const Alignment(0, .1),
            excludeFromSemantics: true,
          ),
        ),
      ),
      const Padding(
        padding: EdgeInsets.fromLTRB(20, 12, 20, 32),
        child: EditorialIntro(
          eyebrow: 'Tu red de protección animal',
          title: 'Conecta.\nCuida. Acompaña.',
          description: 'Un hogar, una ayuda, una nueva oportunidad.',
        ),
      ),
    ],
  );
}

/// Reading and input surfaces are distinct from the warm page canvas.
class FormCard extends StatelessWidget {
  const FormCard({
    super.key,
    required this.child,
    this.title,
    this.subtitle,
    this.icon = Icons.info_outline,
    this.tone = 2,
  });
  final Widget child;
  final String? title, subtitle;
  final IconData icon;
  final int tone;
  @override
  Widget build(BuildContext context) => title != null
      ? LpnFormSection(
          title: title!,
          icon: icon,
          tone: tone,
          description: subtitle,
          children: [child],
        )
      : Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: LpnFormPalette.tones[tone % 5],
            gradient: LpnMaterials.solid(context)
                ? null
                : LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [LpnFormPalette.tones[tone % 5], LpnColors.paper],
                  ),
            boxShadow: LpnMaterials.solid(context)
                ? null
                : const [
                    BoxShadow(
                      color: Color(0x08423222),
                      blurRadius: 16,
                      offset: Offset(0, 4),
                    ),
                  ],
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: LpnColors.controlEdge.withValues(alpha: .45),
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (subtitle != null) ...[
                Text(subtitle!),
                const SizedBox(height: 12),
              ],
              child,
            ],
          ),
        );
}

class EditorialIntro extends StatelessWidget {
  const EditorialIntro({
    super.key,
    required this.eyebrow,
    required this.title,
    this.description,
  });
  final String eyebrow, title;
  final String? description;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        eyebrow.toUpperCase(),
        style: const TextStyle(
          fontSize: 11,
          letterSpacing: 1.2,
          fontWeight: FontWeight.w700,
          color: LpnColors.sage,
        ),
      ),
      const SizedBox(height: 8),
      Text(title, style: Theme.of(context).textTheme.headlineSmall),
      if (description != null) ...[
        const SizedBox(height: 12),
        Text(description!, style: Theme.of(context).textTheme.bodySmall),
      ],
    ],
  );
}

/// Suggestions populate the draft only. They never send or imply acceptance.
class DraftSuggestions extends StatelessWidget {
  const DraftSuggestions({
    super.key,
    required this.values,
    required this.onSelected,
    this.enabled = true,
  });
  final List<String> values;
  final ValueChanged<String> onSelected;
  final bool enabled;
  @override
  Widget build(BuildContext context) => Wrap(
    spacing: 8,
    runSpacing: 4,
    children: [
      for (final value in values)
        ActionChip(
          label: Text(value, style: const TextStyle(fontSize: 13)),
          onPressed: enabled ? () => onSelected(value) : null,
          backgroundColor: LpnColors.sageSoft,
          side: const BorderSide(color: LpnColors.line),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
        ),
    ],
  );
}

class AdoptionReadiness extends StatelessWidget {
  const AdoptionReadiness({
    super.key,
    this.specialCare = '',
    this.spaceNeeds = '',
  });
  final String specialCare, spaceNeeds;
  @override
  Widget build(BuildContext context) => FormCard(
    title: 'Antes de adoptar',
    subtitle: 'Revisa estos compromisos y confirma con la organización los cuidados de esta mascota.',
    child: Column(
      children: [
        for (final entry in [
          (
            Icons.home_outlined,
            'Espacio seguro',
            spaceNeeds.isNotEmpty
                ? spaceNeeds
                : 'Un lugar adecuado, protegido y adaptado a sus necesidades.',
          ),
          (
            Icons.favorite_border,
            'Responsabilidad',
            'Alimentación, compañía, protección y bienestar durante toda su vida.',
          ),
          (
            Icons.savings_outlined,
            'Recursos',
            'Alimento, vacunas, controles veterinarios y atención imprevista.',
          ),
          (
            Icons.medical_services_outlined,
            'Cuidados especiales',
            specialCare.isNotEmpty ? specialCare : 'Cuidados no publicados. Consulta con la organización; no significa que no los necesite.',
          ),
        ])
          Padding(
            padding: const EdgeInsets.only(bottom: 14),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(entry.$1, size: 21, color: LpnColors.sage),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        entry.$2,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        entry.$3,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
      ],
    ),
  );
}

class ProductCatalogCard extends StatelessWidget {
  const ProductCatalogCard({
    super.key,
    required this.row,
    required this.origin,
    required this.onOpen,
  });
  final Map<String, dynamic> row;
  final Uri origin;
  final VoidCallback onOpen;
  @override
  Widget build(BuildContext context) => Card(
    clipBehavior: Clip.antiAlias,
    child: InkWell(
      onTap: onOpen,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: LayoutBuilder(
          builder: (context, constraints) {
            final info = Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${row['nombre'] ?? 'Producto'}',
                  style: const TextStyle(
                    fontSize: 20,
                    height: 1.2,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  '${row['categoria'] ?? 'Producto'}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                if ('${row['tienda'] ?? ''}'.isNotEmpty)
                  Text(
                    '${row['tienda']}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                const SizedBox(height: 12),
                Text(
                  CopAmount.parse(row['precio'])?.formatted ??
                      'Precio no disponible',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Text(
                  productStock(row) == null
                      ? 'Disponibilidad no confirmada'
                      : productStock(row) == 0
                      ? 'Agotado'
                      : '${productStock(row)} disponibles',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 12),
                const DecisionAction('Ver producto'),
              ],
            );
            final image = ClipRRect(
              borderRadius: BorderRadius.circular(18),
              child: SizedBox.square(
                dimension: 112,
                child: PublicProductImage(row: row, origin: origin),
              ),
            );
            if (constraints.maxWidth < 260 ||
                MediaQuery.textScalerOf(context).scale(14) >= 22) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [image, const SizedBox(height: 16), info],
              );
            }
            return Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                image,
                const SizedBox(width: 16),
                Expanded(child: info),
              ],
            );
          },
        ),
      ),
    ),
  );
}
