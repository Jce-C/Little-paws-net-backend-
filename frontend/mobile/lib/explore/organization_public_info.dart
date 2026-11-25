import '../design/readable_text.dart';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../design/lpn_app_bar.dart';
import '../design/refined_surfaces.dart';
import 'organization_logo.dart';

/// Public editorial fields only; never infer contact details from internal data.
class OrganizationPublicInfo extends StatelessWidget {
  const OrganizationPublicInfo({
    super.key,
    required this.row,
    this.compact = false,
  });
  final Map<String, dynamic> row;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final value = row['perfil_publico'];
    final profile = value is Map ? value : const <String, Object?>{};
    String text(String key, int max) {
      final value = profile[key];
      return value is String && value.runes.length <= max ? value.trim() : '';
    }

    final editorial = text('descripcion', 2000);
    final legacy = row['descripcion'];
    final description = editorial.isNotEmpty
        ? editorial
        : legacy is String
        ? legacy
        : '';
    final fields = [
      ('Servicios', text('servicios', 1000)),
      ('Teléfono público', text('telefono', 32)),
      ('Correo público', text('correo', 254)),
      ('Sitio web', text('sitio_web', 200)),
    ].where((field) => field.$2.isNotEmpty).toList();
    if (compact) {
      final services = text('servicios', 1000);
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (description.isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(description, maxLines: 3, overflow: TextOverflow.ellipsis),
          ],
          if (services.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              services,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
          if (fields.isEmpty) ...[
            const SizedBox(height: 8),
            Text(
              'Contacto y servicios: no publicados en el catálogo.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ],
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (description.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(description),
        ],
        if ('${row['direccion'] ?? ''}'.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text('${row['direccion']}'),
        ],
        for (final field in fields) ...[
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: Text(
                  field.$1,
                  style: Theme.of(context).textTheme.labelLarge,
                ),
              ),
              if (field.$1 != 'Servicios')
                IconButton(
                  tooltip: 'Copiar ${field.$1.toLowerCase()}',
                  icon: const Icon(Icons.copy_outlined, size: 18),
                  onPressed: () async {
                    await Clipboard.setData(ClipboardData(text: field.$2));
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('${field.$1} copiado.')),
                      );
                    }
                  },
                ),
            ],
          ),
          const SizedBox(height: 2),
          ReadableText(field.$2),
        ],
        if (fields.isEmpty) ...[
          const SizedBox(height: 8),
          Text(
            'Contacto y servicios: no publicados en el catálogo.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ],
    );
  }
}

/// Uses the already public directory record: navigation needs no second API
/// query and never falls back to internal membership/contact information.
class OrganizationDetailScreen extends StatelessWidget {
  const OrganizationDetailScreen({
    super.key,
    required this.row,
    required this.origin,
  });
  final Map<String, dynamic> row;
  final Uri origin;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Organización'),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        FormCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              OrganizationIdentity(row: row, origin: origin),
              const SizedBox(height: 16),
              OrganizationPublicInfo(row: row),
            ],
          ),
        ),
        const SizedBox(height: 16),
        const Text(
          'Se muestran únicamente los datos publicados por la organización. Confirma directamente la disponibilidad de sus servicios.',
        ),
      ],
    ),
  );
}
