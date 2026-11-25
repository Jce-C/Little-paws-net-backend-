import 'package:flutter/material.dart';

import '../design/lpn_theme.dart';

class ReportPhoto extends StatelessWidget {
  const ReportPhoto({
    super.key,
    required this.value,
    required this.reportId,
    this.origin,
    this.height = 140,
  });
  final Object? value;
  final int reportId;
  final Uri? origin;
  final double height;
  @override
  Widget build(BuildContext context) {
    final row = value;
    String? path;
    if (row is Map &&
        row['url'] == '/api/reportes/$reportId/foto/' &&
        row['bytes'] is int &&
        (row['bytes'] as int) > 0 &&
        (row['bytes'] as int) <= 128 * 1024 &&
        row['ancho'] is int &&
        row['alto'] is int &&
        (row['ancho'] as int) > 0 &&
        (row['ancho'] as int) <= 960 &&
        (row['alto'] as int) > 0 &&
        (row['alto'] as int) <= 960) {
      path = row['url'] as String;
    }
    Widget fallback() => ColoredBox(
      color: LpnColors.sageSoft,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.pets_outlined, size: 36, color: LpnColors.sage),
            const SizedBox(height: 8),
            const Text(
              'Sin fotografía',
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: LpnColors.ink,
              ),
            ),
          ],
        ),
      ),
    );
    return SizedBox(
      height: height,
      width: double.infinity,
      child: path == null || origin == null
          ? fallback()
          : Image.network(
              origin!.resolve(path).toString(),
              fit: BoxFit.cover,
              semanticLabel: 'Fotografía del animal reportado',
              errorBuilder: (_, error, stack) => fallback(),
            ),
    );
  }
}
