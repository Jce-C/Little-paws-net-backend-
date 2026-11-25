import 'package:flutter/material.dart';

import 'lpn_theme.dart';

/// Previous access styling, isolated from the current application shell.
ThemeData lpnAccessTheme({bool reduceTransparency = false}) {
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
  final shape = RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(15.5),
  );
  return base.copyWith(
    scaffoldBackgroundColor: LpnColors.canvas,
    extensions: [LpnMaterials(reduceTransparency: reduceTransparency)],
    textTheme: base.textTheme.copyWith(
      headlineSmall: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 22,
        fontWeight: FontWeight.w700,
        height: 1.25,
        letterSpacing: -.65,
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
    cardTheme: CardThemeData(
      color: LpnColors.paper,
      surfaceTintColor: Colors.transparent,
      shadowColor: const Color(0x18423222),
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 6),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(24),
        side: const BorderSide(color: Color(0xfff5f5f5)),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: LpnColors.control,
        foregroundColor: LpnColors.ink,
        elevation: 5,
        shadowColor: const Color(0x99423222),
        side: const BorderSide(color: LpnColors.controlEdge),
        minimumSize: const Size(48, 39),
        tapTargetSize: MaterialTapTargetSize.padded,
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
        shape: shape,
        textStyle: const TextStyle(
          fontFamily: 'Inter',
          fontWeight: FontWeight.w700,
          fontSize: 16,
        ),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(48, 39),
        tapTargetSize: MaterialTapTargetSize.padded,
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
        backgroundColor: LpnColors.paper,
        elevation: 2,
        shadowColor: const Color(0x80423222),
        side: const BorderSide(color: LpnColors.controlEdge),
        shape: shape,
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
      filled: true,
      fillColor: const Color(0xf2fff9ec),
      floatingLabelBehavior: FloatingLabelBehavior.always,
      labelStyle: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 14,
        fontWeight: FontWeight.w600,
        color: LpnColors.muted,
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(15.5)),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15.5),
        borderSide: const BorderSide(color: LpnColors.controlEdge),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(15.5),
        borderSide: const BorderSide(color: LpnColors.ink, width: 2),
      ),
      helperMaxLines: 3,
    ),
    chipTheme: base.chipTheme.copyWith(
      backgroundColor: LpnColors.paper,
      selectedColor: LpnColors.sageSoft,
      side: const BorderSide(color: LpnColors.line),
      shape: const StadiumBorder(),
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
        side: const BorderSide(color: Color(0xfff5f5f5)),
      ),
      textStyle: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 14,
        color: LpnColors.ink,
      ),
    ),
    dialogTheme: DialogThemeData(
      backgroundColor: const Color(0xffddc5ab),
      surfaceTintColor: Colors.transparent,
      shadowColor: const Color(0x80754812),
      elevation: 8,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(24),
        side: const BorderSide(color: Colors.white),
      ),
    ),
    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith(
        (states) => states.contains(WidgetState.disabled)
            ? LpnColors.line
            : const Color(0xfff5cf9b),
      ),
      trackColor: WidgetStateProperty.resolveWith(
        (states) => states.contains(WidgetState.selected)
            ? const Color(0xffddc5ab)
            : LpnColors.paper,
      ),
      trackOutlineColor: WidgetStateProperty.all(const Color(0xffad8255)),
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
