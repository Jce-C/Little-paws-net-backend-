import 'package:flutter/material.dart';

/// The ID keeps the tone stable across refreshes and pagination.
/// No blur, image texture or extra network resources per publication.
abstract final class CommunitySurface {
  static const tones = [
    Color(0xffffedc9),
    Color(0xffe7efdf),
    Color(0xfff5e2e4),
    Color(0xffece5f5),
    Color(0xffe2ecf7),
  ];

  static Color background(BuildContext context, int id) {
    final tone = tones[id.abs() % tones.length];
    final scheme = Theme.of(context).colorScheme;
    return scheme.brightness == Brightness.dark
        ? Color.alphaBlend(tone.withValues(alpha: .12), scheme.surface)
        : tone;
  }

  static BoxDecoration decoration(BuildContext context, int id) =>
      BoxDecoration(
        color: background(context, id),
        borderRadius: BorderRadius.circular(24),
        border: MediaQuery.highContrastOf(context)
            ? Border.all(color: Theme.of(context).colorScheme.onSurface)
            : null,
      );
}
