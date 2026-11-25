import 'package:flutter/material.dart';

import 'lpn_theme.dart';
import 'form_surfaces.dart';

const evaluationTints = LpnFormPalette.tones;
const evaluationIcons = [
  Icons.person_outline,
  Icons.home_outlined,
  Icons.favorite_border,
  Icons.pets_outlined,
  Icons.fact_check_outlined,
];

/// Quiet color grouping; controls retain their labels and normal touch targets.
class EvaluationPanel extends StatelessWidget {
  const EvaluationPanel({
    super.key,
    required this.step,
    required this.title,
    required this.child,
    this.description,
  });
  final int step;
  final String title;
  final String? description;
  final Widget child;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: evaluationTints[step],
      borderRadius: BorderRadius.circular(20),
      border: Border.all(color: LpnColors.controlEdge.withValues(alpha: .45)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: const BoxDecoration(
                color: LpnColors.paper,
                shape: BoxShape.circle,
              ),
              child: Icon(
                evaluationIcons[step],
                size: 20,
                color: LpnColors.sage,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Semantics(
                header: true,
                child: Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ),
            ),
          ],
        ),
        if (description != null) ...[
          const SizedBox(height: 8),
          Text(description!, style: Theme.of(context).textTheme.bodySmall),
        ],
        const Padding(
          padding: EdgeInsets.symmetric(vertical: 12),
          child: Divider(height: 1, color: Color(0x338a7c70)),
        ),
        child,
      ],
    ),
  );
}

class EvaluationProgress extends StatelessWidget {
  const EvaluationProgress({
    super.key,
    required this.step,
    required this.title,
  });
  final int step;
  final String title;
  @override
  Widget build(BuildContext context) => Semantics(
    label: 'Paso ${step + 1} de 5: $title',
    child: ExcludeSemantics(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Paso ${step + 1} de 5',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              for (var i = 0; i < 5; i++) ...[
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: i <= step ? LpnColors.sage : LpnColors.paper,
                    border: Border.all(
                      color: i <= step ? LpnColors.sage : LpnColors.controlEdge,
                    ),
                  ),
                  child: Icon(
                    i < step ? Icons.check : evaluationIcons[i],
                    size: 16,
                    color: i <= step ? LpnColors.paper : LpnColors.muted,
                  ),
                ),
                if (i < 4)
                  Expanded(
                    child: Container(
                      height: 2,
                      color: i < step ? LpnColors.sage : LpnColors.line,
                    ),
                  ),
              ],
            ],
          ),
        ],
      ),
    ),
  );
}
