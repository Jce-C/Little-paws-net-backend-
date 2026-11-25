import 'package:flutter/material.dart';

import 'lpn_theme.dart';

/// A content hierarchy, not a fixed-height template. Media and reading areas
/// remain separate; each domain supplies its own decision data and action.
class DecisionCard extends StatelessWidget {
  const DecisionCard({super.key, this.media, required this.child, this.onTap});
  final Widget? media;
  final Widget child;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) => Card(
    clipBehavior: Clip.antiAlias,
    child: InkWell(
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          ?media,
          Padding(padding: const EdgeInsets.all(16), child: child),
        ],
      ),
    ),
  );
}

class DecisionHeading extends StatelessWidget {
  const DecisionHeading({super.key, required this.title, this.contextLine});
  final String title;
  final String? contextLine;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      Text(
        title,
        style: Theme.of(context).textTheme.titleLarge
            ?.copyWith(fontSize: 20, height: 1.25, fontWeight: FontWeight.w700),
      ),
      if (contextLine != null && contextLine!.isNotEmpty) ...[
        const SizedBox(height: 4),
        Text(
          contextLine!,
          style: Theme.of(context).textTheme.bodyMedium
              ?.copyWith(height: 1.4, color: LpnColors.muted),
        ),
      ],
    ],
  );
}

/// A visual cue inside an already actionable card, not a nested tap target.
class DecisionAction extends StatelessWidget {
  const DecisionAction(this.label, {super.key});
  final String label;
  @override
  Widget build(BuildContext context) => Container(
    constraints: const BoxConstraints(minHeight: 48),
    padding: const EdgeInsets.symmetric(vertical: 12),
    decoration: BoxDecoration(
      border: Border(top: BorderSide(color: LpnColors.line)),
    ),
    child: Row(
      children: [
        Expanded(
          child: Text(
            label,
            style: const TextStyle(
              fontSize: 14,
              height: 1.4,
              fontWeight: FontWeight.w700,
              color: LpnColors.ink,
            ),
          ),
        ),
        const SizedBox(width: 8),
        const Icon(Icons.arrow_forward_rounded, size: 20, color: LpnColors.ink),
      ],
    ),
  );
}
