import 'lpn_app_bar.dart';

import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

abstract final class AccessPalette {
  static const sand = Color(0xfff7db9f);
  static const gold = Color(0xfff4c778);
  static const amber = Color(0xffedb464);
  static const welcome = Color(0xfff2c778);
  static const cream = Color(0xfffffdf9);
  static const purple = Color(0xff354c9a);
  static const brown = Color(0xff765719);
  static const ink = Color(0xff382c10);
}

class AccessBackground extends StatelessWidget {
  const AccessBackground({super.key, required this.child});
  final Widget child;
  @override
  Widget build(BuildContext context) =>
      CustomPaint(painter: const _AccessWaves(), child: child);
}

class _AccessWaves extends CustomPainter {
  const _AccessWaves();
  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawRect(Offset.zero & size, Paint()..color = AccessPalette.sand);
    final top = Path()
      ..lineTo(0, size.height * .26)
      ..cubicTo(
        size.width * .2,
        size.height * .38,
        size.width * .28,
        size.height * .17,
        size.width * .53,
        size.height * .3,
      )
      ..cubicTo(
        size.width * .7,
        size.height * .36,
        size.width * .85,
        size.height * .38,
        size.width,
        size.height * .37,
      )
      ..lineTo(size.width, 0)
      ..close();
    canvas.drawPath(top, Paint()..color = AccessPalette.gold);
    final bottom = Path()
      ..moveTo(0, size.height * .88)
      ..cubicTo(
        size.width * .18,
        size.height * .8,
        size.width * .57,
        size.height * 1.02,
        size.width * .83,
        size.height * .79,
      )
      ..quadraticBezierTo(
        size.width * .95,
        size.height * .65,
        size.width,
        size.height * .74,
      )
      ..lineTo(size.width, size.height)
      ..lineTo(0, size.height)
      ..close();
    canvas.drawPath(bottom, Paint()..color = AccessPalette.amber);
  }

  @override
  bool shouldRepaint(_AccessWaves oldDelegate) => false;
}

class ReferenceAccessHero extends StatelessWidget {
  const ReferenceAccessHero({
    super.key,
    this.register = false,
    this.compact = false,
  });
  final bool register, compact;
  @override
  Widget build(BuildContext context) => Padding(
    padding: EdgeInsets.fromLTRB(20, compact ? 16 : 70, 20, 0),
    child: Column(
      children: [
        FittedBox(
          fit: BoxFit.scaleDown,
          child: Text(
            'Little Paws Net',
            maxLines: 1,
            style: TextStyle(
              fontFamily: 'LPN Script',
              fontSize: compact ? 32 : 46,
              color: AccessPalette.cream,
            ),
          ),
        ),
        const SizedBox(height: 4),
        SvgPicture.asset(
          'assets/access/brand-access.svg',
          width: compact ? 52 : 80,
          height: compact ? 56 : 84,
          colorFilter: const ColorFilter.mode(
            AccessPalette.cream,
            BlendMode.srcIn,
          ),
          excludeFromSemantics: true,
        ),
        LayoutBuilder(
          builder: (context, box) {
            final height = compact
                ? (register ? 72.0 : 120.0)
                : (register ? 108.0 : 200.0);
            // The supplied cutout includes a transparent shadow below the paws.
            // Align its visible base with the next field, without moving the form.
            final paintedHeight = (box.maxWidth * 500 / 905).clamp(0.0, height);
            return Transform.translate(
              offset: Offset(0, paintedHeight * .115),
              transformHitTests: false,
              child: Image.asset(
                'assets/access/login-pets.webp',
                key: const Key('access-pets'),
                height: height,
                width: double.infinity,
                fit: BoxFit.contain,
                alignment: Alignment.bottomCenter,
                excludeFromSemantics: true,
              ),
            );
          },
        ),
      ],
    ),
  );
}

ThemeData referenceAccessTheme(
  ThemeData base, {
  bool insetLabels = false,
}) => base.copyWith(
  scaffoldBackgroundColor: AccessPalette.sand,
  textTheme: base.textTheme.apply(
    bodyColor: AccessPalette.ink,
    displayColor: AccessPalette.ink,
  ),
  colorScheme: base.colorScheme.copyWith(
    primary: AccessPalette.purple,
    onPrimary: AccessPalette.cream,
    surface: AccessPalette.sand,
    onSurface: AccessPalette.ink,
  ),
  inputDecorationTheme: InputDecorationTheme(
    filled: true,
    fillColor: AccessPalette.brown,
    contentPadding: EdgeInsets.symmetric(
      horizontal: 24,
      vertical: insetLabels ? 12 : 17,
    ),
    floatingLabelBehavior: FloatingLabelBehavior.always,
    // At large type the visible caption is outside the capsule and can wrap.
    // Keep the native label for the editable field's complete semantic name;
    // do not draw a second copy or reserve floating-label height inside it.
    labelStyle: TextStyle(
      color: AccessPalette.brown,
      fontSize: insetLabels ? 0 : null,
      height: insetLabels ? .001 : null,
    ),
    floatingLabelStyle: TextStyle(
      color: insetLabels ? AccessPalette.cream : AccessPalette.brown,
      backgroundColor: insetLabels ? Colors.transparent : AccessPalette.sand,
      fontSize: insetLabels ? 0 : 18,
      height: insetLabels ? .001 : null,
      fontWeight: FontWeight.w600,
    ),
    hintStyle: const TextStyle(color: Color(0xfffef3c7)),
    suffixIconColor: const Color(0xfffef3c7),
    border: insetLabels
        ? const UnderlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(32)),
            borderSide: BorderSide.none,
          )
        : OutlineInputBorder(
            borderRadius: BorderRadius.circular(32),
            borderSide: BorderSide.none,
          ),
    enabledBorder: insetLabels
        ? const UnderlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(32)),
            borderSide: BorderSide.none,
          )
        : OutlineInputBorder(
            borderRadius: BorderRadius.circular(32),
            borderSide: BorderSide.none,
          ),
    focusedBorder: insetLabels
        ? const UnderlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(32)),
            borderSide: BorderSide(color: AccessPalette.cream, width: 2),
          )
        : OutlineInputBorder(
            borderRadius: BorderRadius.circular(32),
            borderSide: const BorderSide(color: AccessPalette.purple, width: 2),
          ),
    errorBorder: insetLabels
        ? UnderlineInputBorder(
            borderRadius: const BorderRadius.all(Radius.circular(32)),
            borderSide: BorderSide(color: base.colorScheme.error, width: 2),
          )
        : OutlineInputBorder(
            borderRadius: BorderRadius.circular(32),
            borderSide: BorderSide(color: base.colorScheme.error, width: 2),
          ),
    errorMaxLines: 3,
  ),
  filledButtonTheme: FilledButtonThemeData(
    style: FilledButton.styleFrom(
      backgroundColor: AccessPalette.purple,
      foregroundColor: AccessPalette.cream,
      minimumSize: const Size(48, 54),
      shape: const StadiumBorder(),
      textStyle: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 16,
        fontWeight: FontWeight.w700,
      ),
    ),
  ),
  textButtonTheme: TextButtonThemeData(
    style: TextButton.styleFrom(
      foregroundColor: AccessPalette.purple,
      textStyle: const TextStyle(
        fontFamily: 'Inter',
        fontSize: 14,
        fontWeight: FontWeight.w600,
      ),
    ),
  ),
);

AppBar referenceAccessAppBar(BuildContext context, String title) {
  final measured = lpnAppBar(context, title);
  return AppBar(
    title: measured.title,
    titleTextStyle: measured.titleTextStyle,
    toolbarHeight: measured.toolbarHeight,
    titleSpacing: measured.titleSpacing,
    centerTitle: true,
    backgroundColor: AccessPalette.gold,
    foregroundColor: AccessPalette.ink,
    surfaceTintColor: Colors.transparent,
  );
}
