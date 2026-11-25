import 'package:flutter/material.dart';

import '../design/decision_card.dart';
import '../design/lpn_theme.dart';

/// Only the bounded, same-organization public endpoint may supply this image.
class OrganizationLogoData {
  const OrganizationLogoData._(this.path);
  final Uri path;
  static OrganizationLogoData? fromRow(Map<String, dynamic> row) {
    final id = row['id'];
    final value = row['logo'];
    if (id is! int || id < 1 || value is! Map) return null;
    final url = value['url'];
    final width = value['ancho'];
    final height = value['alto'];
    final bytes = value['bytes'];
    if (url is! String ||
        width is! int ||
        height is! int ||
        bytes is! int ||
        width < 1 ||
        width > 512 ||
        height < 1 ||
        height > 512 ||
        bytes < 1 ||
        bytes > 96 * 1024 ||
        !RegExp('^/api/red/organizaciones/$id/logo/(\\?v=[0-9]{1,20})?\$')
            .hasMatch(url)) {
      return null;
    }
    final path = Uri.tryParse(url);
    if (path == null ||
        path.hasScheme ||
        path.hasAuthority ||
        path.hasFragment) {
      return null;
    }
    return OrganizationLogoData._(path);
  }
}

class OrganizationLogo extends StatelessWidget {
  const OrganizationLogo({super.key, required this.row, required this.origin});
  final Map<String, dynamic> row;
  final Uri origin;
  @override
  Widget build(BuildContext context) {
    final logo = OrganizationLogoData.fromRow(row);
    final fallback = Icon(
      row['tipo'] == 'Veterinaria'
          ? Icons.local_hospital_outlined
          : row['tipo'] == 'Tienda'
          ? Icons.storefront_outlined
          : Icons.volunteer_activism_outlined,
      size: 28,
      color: LpnColors.sage,
    );
    return ExcludeSemantics(
      child: Container(
        key: ValueKey('organization-logo-${row['id']}-${logo?.path}'),
        width: 64,
        height: 64,
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: LpnColors.paper,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: LpnColors.line),
        ),
        child: logo == null
            ? fallback
            : Image.network(
                origin.resolveUri(logo.path).toString(),
                fit: BoxFit.contain,
                cacheWidth: (64 * MediaQuery.devicePixelRatioOf(context))
                    .ceil()
                    .clamp(64, 512),
                gaplessPlayback: false,
                frameBuilder: (context, child, frame, synchronous) =>
                    frame != null || synchronous ? child : fallback,
                errorBuilder: (context, error, stack) => fallback,
              ),
      ),
    );
  }
}

class OrganizationIdentity extends StatelessWidget {
  const OrganizationIdentity({
    super.key,
    required this.row,
    required this.origin,
  });
  final Map<String, dynamic> row;
  final Uri origin;
  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) {
      final heading = DecisionHeading(
        title: '${row['nombre'] ?? 'Organización'}',
        contextLine: [
          row['tipo'],
          row['ciudad'],
        ].whereType<String>().where((v) => v.trim().isNotEmpty).join('\n'),
      );
      final logo = OrganizationLogo(row: row, origin: origin);
      if (constraints.maxWidth < 300 ||
          MediaQuery.textScalerOf(context).scale(16) > 22) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Align(alignment: AlignmentDirectional.centerStart, child: logo),
            const SizedBox(height: 12),
            heading,
          ],
        );
      }
      return Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          logo,
          const SizedBox(width: 16),
          Expanded(child: heading),
        ],
      );
    },
  );
}
