import 'package:flutter/material.dart';

/// Static information remains readable by web screen readers and selectable.
class ReadableText extends StatelessWidget {
  const ReadableText(this.data, {super.key, this.style, this.semanticsLabel});
  final String data;
  final TextStyle? style;
  final String? semanticsLabel;
  @override
  Widget build(BuildContext context) => SelectionArea(
    child: Text(data, style: style, semanticsLabel: semanticsLabel),
  );
}
