import 'dart:ui';

import 'package:flutter/material.dart';

abstract final class LpnColors {
  static const butter = Color(0xfff1c57e);
  static const blush = Color(0xfff6e0ce);
  static const charcoal = Color(0xff2b2c33);
  static const welcome = Color(0xfff8e9d0);
  static const canvas = Color(0xfffff8f3);
  static const paper = Color(0xfffffcfa);
  static const ink = Color(0xff302a27);
  static const muted = Color(0xff594d45);
  static const sage = Color(0xff354f9a);
  static const sageSoft = Color(0xffe7ecfa);
  static const line = Color(0xffe8ddd4);
  static const control = Color(0xfff5ebe3);
  static const controlEdge = Color(0xff8a7c70);
}

abstract final class LpnRadii {
  static const control = 14.0;
}

@immutable
class LpnMaterials extends ThemeExtension<LpnMaterials> {
  const LpnMaterials({this.reduceTransparency = false});
  final bool reduceTransparency;
  static bool solid(BuildContext context) =>
      MediaQuery.highContrastOf(context) ||
      (Theme.of(context).extension<LpnMaterials>()?.reduceTransparency ??
          false);
  @override
  LpnMaterials copyWith({bool? reduceTransparency}) => LpnMaterials(
    reduceTransparency: reduceTransparency ?? this.reduceTransparency,
  );
  @override
  LpnMaterials lerp(covariant LpnMaterials? other, double t) =>
      t < .5 ? this : other ?? this;
}

ThemeData lpnTheme({bool reduceTransparency = false}) {
  final colors = ColorScheme.fromSeed(
    seedColor: LpnColors.sage,
    primary: LpnColors.sage,
    onPrimary: LpnColors.paper,
    secondaryContainer: LpnColors.sageSoft,
    onSecondaryContainer: LpnColors.sage,
    surface: LpnColors.canvas,
    onSurface: LpnColors.ink,
    outline: const Color(0xff8b806e),
    outlineVariant: LpnColors.line,
  );
  final base = ThemeData(fontFamily: 'Inter', colorScheme: colors);

  return base.copyWith(
    scaffoldBackgroundColor: LpnColors.canvas,
    extensions: [LpnMaterials(reduceTransparency: reduceTransparency)],
    textTheme: base.textTheme.copyWith(
      headlineSmall: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 28,
        fontWeight: FontWeight.w600,
        height: 1.05,
        letterSpacing: -.7,
        color: LpnColors.ink,
      ),
      titleLarge: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 18,
        fontWeight: FontWeight.w700,
        height: 1.3,
        letterSpacing: -.4,
        color: LpnColors.ink,
      ),
      titleMedium: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 16,
        fontWeight: FontWeight.w600,
        height: 1.4,
        color: LpnColors.ink,
      ),
      bodyMedium: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 16,
        height: 1.5,
        color: LpnColors.ink,
      ),
      bodySmall: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 14,
        height: 1.5,
        color: LpnColors.muted,
      ),
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: LpnColors.canvas,
      foregroundColor: LpnColors.ink,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
      scrolledUnderElevation: 0,
      centerTitle: false,
    ),
    listTileTheme: const ListTileThemeData(
      contentPadding: EdgeInsets.all(16),
      minVerticalPadding: 12,
      titleTextStyle: TextStyle(
        fontFamily: 'Inter',
        fontSize: 18,
        height: 1.3,
        fontWeight: FontWeight.w700,
        color: LpnColors.ink,
      ),
      subtitleTextStyle: TextStyle(
        fontFamily: 'Inter',
        fontSize: 14,
        height: 1.5,
        color: LpnColors.muted,
      ),
    ),
    cardTheme: CardThemeData(
      color: LpnColors.paper,
      surfaceTintColor: Colors.transparent,
      shadowColor: const Color(0x18423222),
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 6),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: LpnColors.line),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: LpnColors.charcoal,
        foregroundColor: LpnColors.paper,
        elevation: 0,
        side: const BorderSide(color: LpnColors.charcoal),
        minimumSize: const Size(48, 48),
        tapTargetSize: MaterialTapTargetSize.padded,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        textStyle: const TextStyle(
          fontFamily: 'Inter',
          fontWeight: FontWeight.w700,
          fontSize: 16,
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(48, 48),
        tapTargetSize: MaterialTapTargetSize.padded,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        backgroundColor: LpnColors.paper,
        elevation: 0,
        side: const BorderSide(color: LpnColors.controlEdge),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        foregroundColor: LpnColors.ink,
        textStyle: const TextStyle(
          fontFamily: 'Inter',
          fontSize: 14,
          fontWeight: FontWeight.w700,
        ),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        minimumSize: const Size(48, 48),
        foregroundColor: LpnColors.sage,
        textStyle: const TextStyle(
          fontFamily: 'Inter',
          fontSize: 14,
          fontWeight: FontWeight.w700,
        ),
      ),
    ),
    iconButtonTheme: IconButtonThemeData(
      style: IconButton.styleFrom(
        minimumSize: const Size(48, 48),
        foregroundColor: LpnColors.ink,
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      isDense: true,
      constraints: const BoxConstraints(minHeight: 48),
      filled: true,
      fillColor: LpnColors.paper,
      floatingLabelBehavior: FloatingLabelBehavior.always,
      labelStyle: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: LpnColors.muted,
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(LpnRadii.control),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(LpnRadii.control),
        borderSide: const BorderSide(color: LpnColors.controlEdge),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(LpnRadii.control),
        borderSide: const BorderSide(color: LpnColors.ink, width: 2),
      ),
      helperMaxLines: 3,
    ),
    chipTheme: base.chipTheme.copyWith(
      backgroundColor: LpnColors.paper,
      selectedColor: LpnColors.sageSoft,
      side: const BorderSide(color: LpnColors.line),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      labelPadding: const EdgeInsets.symmetric(horizontal: 6),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: Colors.transparent,
      surfaceTintColor: Colors.transparent,
      elevation: 0,
      indicatorColor: LpnColors.sageSoft,
      labelTextStyle: WidgetStateProperty.resolveWith(
        (states) => TextStyle(
          fontFamily: 'Inter',
          fontSize: 11,
          fontWeight: states.contains(WidgetState.selected)
              ? FontWeight.w700
              : FontWeight.w500,
          color: LpnColors.ink,
        ),
      ),
    ),
    popupMenuTheme: PopupMenuThemeData(
      color: LpnColors.paper,
      surfaceTintColor: Colors.transparent,
      elevation: 8,
      shadowColor: const Color(0x80423222),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(24),
        side: const BorderSide(color: LpnColors.line),
      ),
      textStyle: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 14,
        color: LpnColors.ink,
      ),
    ),
    dialogTheme: DialogThemeData(
      backgroundColor: LpnColors.paper,
      surfaceTintColor: Colors.transparent,
      shadowColor: const Color(0x18423222),
      elevation: 8,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(24),
        side: const BorderSide(color: LpnColors.line),
      ),
    ),
    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith(
        (states) => states.contains(WidgetState.disabled)
            ? LpnColors.line
            : states.contains(WidgetState.selected)
            ? LpnColors.paper
            : LpnColors.ink,
      ),
      trackColor: WidgetStateProperty.resolveWith(
        (states) => states.contains(WidgetState.selected)
            ? LpnColors.sage
            : LpnColors.paper,
      ),
      trackOutlineColor: WidgetStateProperty.all(LpnColors.controlEdge),
    ),
    dividerTheme: const DividerThemeData(color: LpnColors.line, thickness: 1),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: LpnColors.ink,
      contentTextStyle: const TextStyle(color: LpnColors.paper),
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
    ),
  );
}

/// A bounded navigation material, not a filter over the content of every card.
class GlassSurface extends StatelessWidget {
  const GlassSurface({
    super.key,
    required this.child,
    this.radius = 24,
    this.padding = EdgeInsets.zero,
  });
  final Widget child;
  final double radius;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    final opaque =
        media.highContrast ||
        media.disableAnimations ||
        (Theme.of(context).extension<LpnMaterials>()?.reduceTransparency ??
            false);
    final content = DecoratedBox(
      decoration: BoxDecoration(
        color: opaque ? LpnColors.paper : null,
        gradient: opaque
            ? null
            : const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xf2fffdf7), Color(0xe6fff3d9)],
              ),
        borderRadius: BorderRadius.circular(radius),
        border: radius == 0
            ? const Border(bottom: BorderSide(color: LpnColors.line))
            : Border.all(
                color: opaque
                    ? const Color(0xff8b806e)
                    : const Color(0xffdfd5c2),
              ),
      ),
      child: Padding(padding: padding, child: child),
    );
    return DecoratedBox(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(radius),
        boxShadow: const [
          BoxShadow(
            color: Color(0x14423222),
            blurRadius: 24,
            spreadRadius: 0,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(radius),
        child: opaque
            ? content
            : BackdropFilter(
                filter: ImageFilter.blur(sigmaX: 8, sigmaY: 8),
                child: content,
              ),
      ),
    );
  }
}

/// Form inputs share quiet outlines; navigation retains the glass material.
class LpnInputSurface extends StatelessWidget {
  const LpnInputSurface({super.key, required this.child});
  final Widget child;
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Theme(
      data: theme.copyWith(
        inputDecorationTheme: theme.inputDecorationTheme.copyWith(
          filled: true,
          fillColor: LpnColors.paper,
        ),
      ),
      child: child,
    );
  }
}
