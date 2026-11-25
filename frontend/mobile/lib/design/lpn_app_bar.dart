import 'dart:math' as math;

import 'package:flutter/material.dart';

/// Section heading from Figma, measured with the actual font and text scaler.
/// A fixed toolbar clips titles such as Notificaciones at 200% on small phones.
AppBar lpnAppBar(
  BuildContext context,
  String title, {
  List<Widget>? actions,
  Widget? leading,
}) {
  final style = Theme.of(context).textTheme.titleLarge!.copyWith(
    fontSize: 15,
    fontWeight: FontWeight.w600,
    height: 1.4,
    letterSpacing: 0,
  );
  final backWidth = Navigator.of(context).canPop() ? kToolbarHeight : 0.0;
  final available = math.max(
    1.0,
    MediaQuery.sizeOf(context).width -
        MediaQuery.paddingOf(context).horizontal -
        backWidth -
        32 -
        (actions?.length ?? 0) * 48,
  );
  final painter = TextPainter(
    text: TextSpan(text: title, style: style),
    textDirection: Directionality.of(context),
    textScaler: MediaQuery.textScalerOf(context),
    maxLines: 3,
    ellipsis: '…',
  )..layout(maxWidth: available);
  final height = math.max(kToolbarHeight, painter.height + 16);
  painter.dispose();
  return AppBar(
    leading: leading,
    title: Text(title, maxLines: 3, overflow: TextOverflow.ellipsis),
    titleTextStyle: style,
    titleSpacing: 16,
    centerTitle: true,
    toolbarHeight: height,
    actions: actions,
  );
}
