import 'dart:ui' show ImageFilter;

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import 'lpn_theme.dart';

/// Capsule and elevated contextual action share one layout and safe area.
class LpnNavigation extends StatelessWidget {
  const LpnNavigation({
    super.key,
    required this.selected,
    required this.onSelected,
    required this.onPrimary,
  });
  final int selected;
  final ValueChanged<int> onSelected;
  final VoidCallback onPrimary;
  static const labels = ['Inicio', 'Adoptar', 'Solicitudes', 'Mi cuenta'];
  static const icons = [
    Icons.home_outlined,
    Icons.pets_outlined,
    Icons.list_alt_outlined,
    Icons.person_outline,
  ];

  Widget _destination(
    BuildContext context,
    int index, {
    bool compact = false,
  }) => Semantics(
    button: true,
    focusable: true,
    selected: selected == index,
    label: '${labels[index]}\nPestaña ${index + 1} de ${labels.length}',
    onTap: () {
      if (selected != index) onSelected(index);
    },
    child: ExcludeSemantics(
      child: InkWell(
        key: ValueKey('navigation-$index'),
        onTap: () {
          if (selected != index) onSelected(index);
        },
        child: AnimatedContainer(
          duration: Duration(
            milliseconds: MediaQuery.disableAnimationsOf(context) ? 0 : 220,
          ),
          curve: Curves.easeOutCubic,
          decoration: BoxDecoration(
            color: compact && selected == index
                ? Colors.white.withValues(alpha: .16)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(24),
          ),
          constraints: const BoxConstraints(minHeight: 48, minWidth: 48),
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icons[index], size: 20, color: LpnColors.paper),
              const SizedBox(height: 4),
              Text(
                labels[index],
                textAlign: TextAlign.center,
                maxLines: compact ? 2 : 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 11,
                  height: 1.3,
                  color: LpnColors.paper,
                  fontWeight: selected == index
                      ? FontWeight.w700
                      : FontWeight.w400,
                ),
              ),
              const SizedBox(height: 4),
              Container(
                width: 18,
                height: 2,
                decoration: BoxDecoration(
                  color: selected == index
                      ? LpnColors.butter
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(1),
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );

  @override
  Widget build(BuildContext context) => SafeArea(
    top: false,
    child: Padding(
      padding: const EdgeInsets.fromLTRB(16, 6, 16, 8),
      child: LayoutBuilder(
        builder: (context, box) {
          final enlarged =
              box.maxWidth < 288 ||
              box.maxWidth < 600 &&
                  MediaQuery.textScalerOf(context).scale(12) > 18;
          final left = [
            for (var i = 0; i < 2; i++)
              _destination(context, i, compact: enlarged),
          ];
          final right = [
            for (var i = 2; i < 4; i++)
              _destination(context, i, compact: enlarged),
          ];
          return Stack(
            clipBehavior: Clip.none,
            alignment: Alignment.topCenter,
            children: [
              Padding(
                padding: const EdgeInsets.only(top: 24),
                child: ClipPath(
                  key: const Key('navigation-capsule'),
                  clipper: NavigationNotch(compact: enlarged),
                  child: _NavigationGlass(
                    child: Material(
                      color: Colors.transparent,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        child: LayoutBuilder(
                          builder: (context, space) {
                            final itemWidth = (space.maxWidth - 72) / 4;
                            final indicatorLeft = selected < 2
                                ? selected * itemWidth
                                : selected * itemWidth + 72;
                            return Stack(
                              children: [
                                if (!enlarged)
                                  AnimatedPositioned(
                                    key: const Key('navigation-selection'),
                                    duration: Duration(
                                      milliseconds:
                                          MediaQuery.disableAnimationsOf(
                                            context,
                                          )
                                          ? 0
                                          : 260,
                                    ),
                                    curve: Curves.easeOutCubic,
                                    left: indicatorLeft,
                                    top: 5,
                                    bottom: 5,
                                    width: itemWidth,
                                    child: DecoratedBox(
                                      decoration: BoxDecoration(
                                        color: Colors.white.withValues(
                                          alpha: .16,
                                        ),
                                        border: Border.all(
                                          color: Colors.white.withValues(
                                            alpha: .2,
                                          ),
                                        ),
                                        borderRadius: BorderRadius.circular(24),
                                      ),
                                    ),
                                  ),
                                Row(
                                  crossAxisAlignment: CrossAxisAlignment.center,
                                  children: [
                                    if (enlarged)
                                      Expanded(
                                        child: Column(
                                          mainAxisSize: MainAxisSize.min,
                                          children: left,
                                        ),
                                      )
                                    else ...[
                                      for (final item in left)
                                        Expanded(child: item),
                                    ],
                                    if (!enlarged) const SizedBox(width: 72),
                                    if (enlarged)
                                      Expanded(
                                        child: Column(
                                          mainAxisSize: MainAxisSize.min,
                                          children: right,
                                        ),
                                      )
                                    else ...[
                                      for (final item in right)
                                        Expanded(child: item),
                                    ],
                                  ],
                                ),
                              ],
                            );
                          },
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              SizedBox(
                width: 56,
                height: 56,
                child: IconButton.filled(
                  key: const Key('navigation-primary'),
                  tooltip: selected == 2
                      ? 'Nueva solicitud de adopción'
                      : 'Crear reporte',
                  onPressed: onPrimary,
                  style: IconButton.styleFrom(
                    backgroundColor: LpnColors.paper,
                    foregroundColor: LpnColors.ink,
                    shape: const CircleBorder(),
                    padding: const EdgeInsets.all(12),
                  ),
                  icon: AnimatedSwitcher(
                    duration: Duration(
                      milliseconds: MediaQuery.disableAnimationsOf(context)
                          ? 0
                          : 180,
                    ),
                    child: selected == 2
                        ? const Icon(
                            Icons.add,
                            key: ValueKey('new-adoption'),
                            size: 28,
                          )
                        : SvgPicture.asset(
                            'assets/brand-organic.svg',
                            key: const ValueKey('report-dog'),
                            width: 24,
                            height: 28,
                            excludeFromSemantics: true,
                          ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    ),
  );
}

/// A real cut-out leaves the page visible between the capsule and the button.
class NavigationNotch extends CustomClipper<Path> {
  const NavigationNotch({this.compact = false});
  final bool compact;
  @override
  Path getClip(Size size) {
    final host = Offset.zero & size;
    final guest = Rect.fromCircle(
      center: Offset(size.width / 2, 4),
      radius: 34,
    );
    final notch = const CircularNotchedRectangle().getOuterPath(host, guest);
    final capsule = Path()
      ..addRRect(
        RRect.fromRectAndRadius(
          host,
          Radius.circular(compact ? 24 : size.height / 2),
        ),
      );
    return Path.combine(PathOperation.intersect, notch, capsule);
  }

  @override
  bool shouldReclip(NavigationNotch oldClipper) =>
      oldClipper.compact != compact;
}

/// One bounded blur for navigation, with an opaque accessible fallback.
class _NavigationGlass extends StatelessWidget {
  const _NavigationGlass({required this.child});
  final Widget child;
  @override
  Widget build(BuildContext context) {
    final solid = LpnMaterials.solid(context);
    final surface = DecoratedBox(
      decoration: BoxDecoration(
        color: LpnColors.charcoal.withValues(alpha: solid ? 1 : .86),
        gradient: solid
            ? null
            : LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  const Color(0xff3e3f48).withValues(alpha: .92),
                  LpnColors.charcoal.withValues(alpha: .88),
                ],
              ),
      ),
      child: child,
    );
    return solid
        ? surface
        : BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
            child: surface,
          );
  }
}
