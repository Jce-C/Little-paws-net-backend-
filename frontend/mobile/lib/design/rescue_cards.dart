import 'package:flutter/material.dart';

import '../rescue/rescue_api.dart';
import '../rescue/report_photo.dart';
import 'lpn_theme.dart';
import 'decision_card.dart';

class ReportDecisionCard extends StatelessWidget {
  const ReportDecisionCard({
    super.key,
    required this.report,
    required this.onOpen,
    this.origin,
    this.compact = false,
  });
  final AnimalReport report;
  final VoidCallback onOpen;
  final Uri? origin;
  final bool compact;
  Widget _info(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(report.type, style: Theme.of(context).textTheme.titleLarge),
      const SizedBox(height: 6),
      Text(
        report.rescueCase?.status ?? report.status,
        style: const TextStyle(
          fontWeight: FontWeight.w600,
          color: LpnColors.sage,
        ),
      ),
      if (report.city.isNotEmpty)
        Padding(
          padding: const EdgeInsets.only(top: 6),
          child: Row(
            children: [
              const Icon(Icons.location_on_outlined, size: 16),
              const SizedBox(width: 4),
              Expanded(child: Text(report.city)),
            ],
          ),
        ),
      const SizedBox(height: 10),
      Text(
        report.description,
        maxLines: 2,
        overflow: TextOverflow.ellipsis,
        style: const TextStyle(height: 1.4),
      ),
    ],
  );
  @override
  Widget build(BuildContext context) => Semantics(
    button: true,
    child: LayoutBuilder(
      builder: (context, box) {
        if (compact &&
            box.maxWidth >= 280 &&
            MediaQuery.textScalerOf(context).scale(14) <= 20) {
          return Card(
            clipBehavior: Clip.antiAlias,
            child: InkWell(
              onTap: onOpen,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: SizedBox(
                        width: 88,
                        child: ReportPhoto(
                          value: report.photo,
                          reportId: report.id,
                          origin: origin,
                          height: 132,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(child: _info(context)),
                    const SizedBox(width: 4),
                    const Icon(Icons.chevron_right, size: 20),
                  ],
                ),
              ),
            ),
          );
        }
        return DecisionCard(
          onTap: onOpen,
          media: ReportPhoto(
            value: report.photo,
            reportId: report.id,
            origin: origin,
            height: 140,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _info(context),
              const SizedBox(height: 12),
              const DecisionAction('Ver reporte'),
            ],
          ),
        );
      },
    ),
  );
}

class RescueCards extends StatelessWidget {
  const RescueCards({
    super.key,
    required this.reports,
    required this.onOpen,
    this.origin,
  });
  final List<AnimalReport> reports;
  final ValueChanged<AnimalReport> onOpen;
  final Uri? origin;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.fromLTRB(20, 8, 20, 16),
    child: LayoutBuilder(
      builder: (context, box) {
        final columns =
            box.maxWidth >= 320 &&
                MediaQuery.textScalerOf(context).scale(14) < 22
            ? 2
            : 1;
        final width = (box.maxWidth - (columns - 1) * 12) / columns;
        return Wrap(
          key: const Key('rescue-case-grid'),
          spacing: 12,
          runSpacing: 12,
          children: [
            for (final report in reports)
              SizedBox(
                width: width,
                child: ReportDecisionCard(
                  report: report,
                  origin: origin,
                  onOpen: () => onOpen(report),
                ),
              ),
          ],
        );
      },
    ),
  );
}

class RescueCategories extends StatelessWidget {
  const RescueCategories({
    super.key,
    required this.onStories,
    required this.onAdopt,
  });
  final VoidCallback onStories;
  final VoidCallback onAdopt;

  @override
  Widget build(BuildContext context) => Center(
    child: ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 393),
      child: Padding(
        padding: const EdgeInsets.fromLTRB(32, 20, 20, 24),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: _category(
                context,
                'Historias de rescate',
                'rescue-category',
                onStories,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _category(context, 'Adopta ya', 'adopt-category', onAdopt),
            ),
          ],
        ),
      ),
    ),
  );

  Widget _category(
    BuildContext context,
    String label,
    String asset,
    VoidCallback onTap,
  ) {
    return Card(
      margin: EdgeInsets.zero,
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: onTap,
        child: Semantics(
          button: true,
          label: label,
          excludeSemantics: true,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              AspectRatio(
                aspectRatio: 135 / 145,
                child: Image.asset(
                  'assets/$asset.webp',
                  fit: BoxFit.cover,
                  excludeFromSemantics: true,
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        label,
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    const Icon(Icons.arrow_forward, size: 16),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
