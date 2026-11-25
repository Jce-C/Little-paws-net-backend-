import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import 'lpn_theme.dart';

/// Decorative geometry stays behind content; text always uses flow layout.
class OrganicSurface extends StatelessWidget {
  const OrganicSurface({
    super.key,
    required this.child,
    this.color = LpnColors.butter,
    this.padding = const EdgeInsets.all(24),
    this.scalloped = false,
    this.animate = false,
  });
  final Widget child;
  final Color color;
  final EdgeInsetsGeometry padding;
  final bool scalloped;
  final bool animate;

  @override
  Widget build(BuildContext context) => SubtleEntrance(
    enabled: animate,
    child: CustomPaint(
      painter: _OrganicPainter(color, scalloped),
      child: Padding(padding: padding, child: child),
    ),
  );
}

class SubtleEntrance extends StatelessWidget {
  const SubtleEntrance({super.key, required this.child, this.enabled = true});
  final Widget child;
  final bool enabled;
  @override
  Widget build(BuildContext context) {
    if (!enabled || MediaQuery.disableAnimationsOf(context)) return child;
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: const Duration(milliseconds: 280),
      curve: Curves.easeOutCubic,
      child: child,
      builder: (context, value, child) => Opacity(
        opacity: value,
        child: Transform.translate(
          offset: Offset(0, 10 * (1 - value)),
          child: child,
        ),
      ),
    );
  }
}

class _OrganicPainter extends CustomPainter {
  const _OrganicPainter(this.color, this.scalloped);
  final Color color;
  final bool scalloped;
  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;
    if (!scalloped) {
      canvas.drawRRect(
        RRect.fromRectAndRadius(rect, const Radius.circular(32)),
        Paint()..color = color,
      );
      canvas.save();
      canvas.clipRRect(
        RRect.fromRectAndRadius(rect, const Radius.circular(32)),
      );
      final center = Offset(size.width + 8, 8);
      final path = Path();
      for (var i = 0; i <= 240; i++) {
        final angle = i / 240 * math.pi * 2;
        final radius = 82 + 9 * math.sin(angle * 10);
        final point =
            center + Offset(math.cos(angle), math.sin(angle)) * radius;
        if (i == 0) {
          path.moveTo(point.dx, point.dy);
        } else {
          path.lineTo(point.dx, point.dy);
        }
      }
      canvas.drawPath(
        path..close(),
        Paint()..color = LpnColors.ink.withValues(alpha: .08),
      );
      canvas.restore();
      return;
    }
    final path = Path()..moveTo(0, 10);
    final count = math.max(4, (size.width / 42).round());
    final step = size.width / count;
    for (var i = 0; i < count; i++) {
      path.quadraticBezierTo(i * step + step / 4, -8, i * step + step / 2, 10);
      path.quadraticBezierTo(i * step + 3 * step / 4, 28, (i + 1) * step, 10);
    }
    path.lineTo(size.width, size.height - 10);
    for (var i = count; i > 0; i--) {
      path.quadraticBezierTo(
        i * step - step / 4,
        size.height + 8,
        i * step - step / 2,
        size.height - 10,
      );
      path.quadraticBezierTo(
        i * step - 3 * step / 4,
        size.height - 28,
        (i - 1) * step,
        size.height - 10,
      );
    }
    canvas.drawPath(path..close(), Paint()..color = color);
  }

  @override
  bool shouldRepaint(_OrganicPainter oldDelegate) =>
      color != oldDelegate.color || scalloped != oldDelegate.scalloped;
}

class FeatureRow extends StatelessWidget {
  const FeatureRow({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.color = LpnColors.sageSoft,
  });
  final IconData icon;
  final String title, subtitle;
  final VoidCallback onTap;
  final Color color;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: Material(
      color: color,
      borderRadius: BorderRadius.circular(28),
      child: InkWell(
        borderRadius: BorderRadius.circular(28),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              CircleAvatar(
                backgroundColor: Colors.white.withValues(alpha: .65),
                foregroundColor: LpnColors.ink,
                child: Icon(icon),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    ),
  );
}

class FeatureDeck extends StatelessWidget {
  const FeatureDeck({
    super.key,
    required this.children,
    this.quickActions = false,
    this.shortcuts = const [],
  });
  final bool quickActions;
  final List<FeatureRow> shortcuts;
  final List<FeatureRow> children;
  Widget _tile(BuildContext context, FeatureRow feature) => _CardReveal(
    order: children.indexOf(feature),
    child: Semantics(
      button: true,
      label: '${feature.title}. ${feature.subtitle}',
      onTap: feature.onTap,
      child: ExcludeSemantics(
        child: DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(24),
            gradient:
                MediaQuery.highContrastOf(context) ||
                    (Theme.of(context)
                            .extension<LpnMaterials>()
                            ?.reduceTransparency ??
                        false)
                ? null
                : LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      Color.alphaBlend(
                        feature.color.withValues(alpha: .62),
                        LpnColors.paper,
                      ),
                      feature.color,
                    ],
                  ),
            color: feature.color,
            border: Border.all(
              color: MediaQuery.highContrastOf(context)
                  ? LpnColors.sage
                  : LpnColors.paper,
              width: 1.5,
            ),
            boxShadow: LpnMaterials.solid(context)
                ? null
                : const [
                    BoxShadow(
                      color: Color(0x10423222),
                      blurRadius: 16,
                      offset: Offset(0, 5),
                    ),
                  ],
          ),
          child: Material(
            color: Colors.transparent,
            borderRadius: BorderRadius.circular(24),
            child: InkWell(
              borderRadius: BorderRadius.circular(22),
              onTap: feature.onTap,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(22),
                child: Stack(
                  children: [
                    Positioned(
                      right: -12,
                      bottom: 12,
                      child: IgnorePointer(
                        child: ExcludeSemantics(
                          child: Opacity(
                            opacity: .07,
                            child: SvgPicture.asset(
                              'assets/brand-organic.svg',
                              width: 126,
                              height: 126,
                            ),
                          ),
                        ),
                      ),
                    ),
                    Positioned(
                      right: -18,
                      top: -22,
                      child: IgnorePointer(
                        child: Container(
                          key: ValueKey('feature-orbit-${feature.title}'),
                          width: 88,
                          height: 88,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: LpnColors.paper.withValues(alpha: .65),
                              width: 18,
                            ),
                          ),
                          child: const Center(
                            child: Icon(Icons.north_east_rounded, size: 17),
                          ),
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(9),
                                decoration: BoxDecoration(
                                  color: LpnColors.paper.withValues(alpha: .72),
                                  borderRadius: BorderRadius.circular(14),
                                ),
                                child: Icon(
                                  feature.icon,
                                  size: 23,
                                  color: LpnColors.sage,
                                ),
                              ),
                              const Spacer(),
                            ],
                          ),
                          const SizedBox(height: 16),
                          Text(
                            feature.title,
                            style: const TextStyle(
                              fontSize: 18,
                              height: 1.3,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            feature.subtitle,
                            style: const TextStyle(
                              fontSize: 14,
                              height: 1.4,
                              color: LpnColors.muted,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    ),
  );
  Widget _grid(BuildContext context) => LayoutBuilder(
    builder: (context, box) {
      if (box.maxWidth < 300 ||
          MediaQuery.textScalerOf(context).scale(14) > 21) {
        return Column(
          children: [
            for (final feature in children)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _tile(context, feature),
              ),
          ],
        );
      }
      return Column(
        children: [
          for (var index = 0; index < children.length; index += 2)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: IntrinsicHeight(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Expanded(child: _tile(context, children[index])),
                    const SizedBox(width: 12),
                    Expanded(
                      child: index + 1 < children.length
                          ? _tile(context, children[index + 1])
                          : const SizedBox.shrink(),
                    ),
                  ],
                ),
              ),
            ),
        ],
      );
    },
  );
  @override
  Widget build(BuildContext context) => Column(
    children: [
      if (quickActions)
        Padding(
          padding: const EdgeInsets.only(bottom: 20),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              for (final (i, feature) in shortcuts.indexed)
                Expanded(
                  child: Column(
                    children: [
                      IconButton.filledTonal(
                        key: ValueKey('home-quick-$i'),
                        tooltip: feature.title,
                        style: IconButton.styleFrom(
                          backgroundColor: feature.color,
                          foregroundColor: LpnColors.ink,
                          minimumSize: const Size(48, 48),
                        ),
                        onPressed: feature.onTap,
                        icon: Icon(feature.icon),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        const ['Adoptar', 'Rescates', 'Ayudar', 'Red'][i],
                        textAlign: TextAlign.center,
                        style: const TextStyle(fontSize: 12, height: 1.3),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ),
      _grid(context),
    ],
  );
}

class _CardReveal extends StatelessWidget {
  const _CardReveal({required this.order, required this.child});
  final int order;
  final Widget child;
  @override
  Widget build(BuildContext context) {
    if (MediaQuery.disableAnimationsOf(context)) return child;
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: const Duration(milliseconds: 460),
      curve: Interval(
        (order * .06).clamp(0, .36),
        1,
        curve: Curves.easeOutCubic,
      ),
      child: child,
      builder: (context, value, child) => Opacity(
        opacity: value,
        child: Transform.translate(
          offset: Offset(0, 12 * (1 - value)),
          child: child,
        ),
      ),
    );
  }
}
