import 'package:flutter/material.dart';

import '../design/refined_surfaces.dart';

/// Same hierarchy for the sender and the receiving organization.
class HelpOfferCard extends StatelessWidget {
  const HelpOfferCard({super.key, required this.row, this.received = false});
  final Map<String, dynamic> row;
  final bool received;
  @override
  Widget build(BuildContext context) {
    final volunteer = row['modalidad'] == 'voluntariado';
    final activity = row['actividad'];
    final message = row['mensaje'];
    final date = DateTime.tryParse('${row['fecha'] ?? ''}')?.toLocal();
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: FormCard(
        title: '${row[received ? 'nombre' : 'organizacion'] ?? 'Ofrecimiento'}',
        icon: volunteer ? Icons.schedule_outlined : Icons.inventory_2_outlined,
        tone: volunteer ? 1 : 0,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              volunteer ? 'Tiempo y voluntariado' : 'Ayuda en especie',
              style: Theme.of(context).textTheme.titleSmall,
            ),
            if (activity is String && activity.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(activity, style: Theme.of(context).textTheme.titleMedium),
            ],
            if (message is String && message.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(message),
            ],
            if (date != null) ...[
              const SizedBox(height: 12),
              Text(
                MaterialLocalizations.of(context).formatMediumDate(date),
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
