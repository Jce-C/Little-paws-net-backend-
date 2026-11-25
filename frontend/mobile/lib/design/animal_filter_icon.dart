import 'package:flutter/material.dart';

/// Small native vector heads; no image downloads or extra icon dependency.
class AnimalFilterIcon extends StatelessWidget {
  const AnimalFilterIcon({
    super.key,
    required this.species,
    required this.color,
  });
  final String species;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final name = species.toLowerCase();
    final cat = name.contains('gato');
    if (!cat && !name.contains('perro')) {
      return Icon(Icons.pets_outlined, size: 20, color: color);
    }
    return ExcludeSemantics(
      child: CustomPaint(
        size: const Size(20, 20),
        painter: _HeadPainter(cat: cat, color: color),
      ),
    );
  }
}

class _HeadPainter extends CustomPainter {
  const _HeadPainter({required this.cat, required this.color});
  final bool cat;
  final Color color;
  @override
  void paint(Canvas canvas, Size size) {
    canvas.save();
    canvas.scale(size.width / 24, size.height / 24);
    final pen = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.7
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    final head = cat
        ? (Path()
            ..moveTo(4, 12)
            ..lineTo(4, 3)
            ..lineTo(9, 7)
            ..quadraticBezierTo(12, 6, 15, 7)
            ..lineTo(20, 3)
            ..lineTo(20, 12)
            ..cubicTo(23, 23, 1, 23, 4, 12))
        : (Path()
            ..moveTo(7, 8)
            ..quadraticBezierTo(12, 4, 17, 8)
            ..cubicTo(23, 2, 25, 18, 19, 16)
            ..cubicTo(18, 24, 6, 24, 5, 16)
            ..cubicTo(-1, 18, 1, 2, 7, 8));
    canvas.drawPath(head, pen);
    canvas.drawCircle(const Offset(8, 12), .9, Paint()..color = color);
    canvas.drawCircle(const Offset(16, 12), .9, Paint()..color = color);
    canvas.drawPath(
      Path()
        ..moveTo(10, 16)
        ..lineTo(12, 18)
        ..lineTo(14, 16),
      pen,
    );
    canvas.restore();
  }

  @override
  bool shouldRepaint(_HeadPainter oldDelegate) =>
      oldDelegate.cat != cat || oldDelegate.color != color;
}
