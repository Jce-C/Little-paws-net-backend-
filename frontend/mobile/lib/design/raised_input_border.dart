import 'package:flutter/material.dart';

/// Paints the shadow on InputDecorator's control bounds, excluding help/errors.
class RaisedInputBorder extends OutlineInputBorder {
  const RaisedInputBorder({
    super.borderSide,
    super.borderRadius,
    super.gapPadding,
  });

  @override
  RaisedInputBorder copyWith({
    BorderSide? borderSide,
    BorderRadius? borderRadius,
    double? gapPadding,
  }) => RaisedInputBorder(
    borderSide: borderSide ?? this.borderSide,
    borderRadius: borderRadius ?? this.borderRadius,
    gapPadding: gapPadding ?? this.gapPadding,
  );

  @override
  void paintInterior(
    Canvas canvas,
    Rect rect,
    Paint paint, {
    TextDirection? textDirection,
  }) {
    canvas.drawShadow(
      getOuterPath(
        rect,
        textDirection: textDirection,
      ).shift(const Offset(0, 3)),
      const Color(0x20423222),
      4,
      true,
    );
    super.paintInterior(canvas, rect, paint, textDirection: textDirection);
  }

  @override
  ShapeBorder? lerpFrom(ShapeBorder? a, double t) {
    if (a is RaisedInputBorder) {
      return RaisedInputBorder(
        borderSide: BorderSide.lerp(a.borderSide, borderSide, t),
        borderRadius: BorderRadius.lerp(a.borderRadius, borderRadius, t)!,
        gapPadding: a.gapPadding + (gapPadding - a.gapPadding) * t,
      );
    }
    return super.lerpFrom(a, t);
  }

  @override
  ShapeBorder? lerpTo(ShapeBorder? b, double t) {
    if (b is RaisedInputBorder) return b.lerpFrom(this, t);
    return super.lerpTo(b, t);
  }

  @override
  bool operator ==(Object other) =>
      other is RaisedInputBorder && super == other;
  @override
  int get hashCode =>
      Object.hash(runtimeType, borderSide, borderRadius, gapPadding);
}
