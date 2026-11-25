import '../design/readable_text.dart';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../auth/session.dart';
import '../adoption/adoption_screens.dart' show messageFor;
import '../design/refined_surfaces.dart';

class BankInstructions extends StatefulWidget {
  const BankInstructions({
    super.key,
    required this.session,
    required this.path,
  });
  final Session session;
  final String path;
  @override
  State<BankInstructions> createState() => _BankInstructionsState();
}

class _BankInstructionsState extends State<BankInstructions> {
  late Future<Object?> _data = _load();
  Future<Object?> _load() => widget.session.authorized(
    (token) => widget.session.api.get(widget.path, token: token),
  );
  @override
  Widget build(BuildContext context) => FutureBuilder<Object?>(
    future: _data,
    builder: (context, state) {
      if (state.connectionState != ConnectionState.done) {
        return const Padding(
          padding: EdgeInsets.all(16),
          child: LinearProgressIndicator(),
        );
      }
      if (state.hasError || state.data is! Map) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              messageFor(
                state.error,
                'No hay instrucciones bancarias publicadas.',
              ),
            ),
            TextButton.icon(
              onPressed: () => setState(() {
                _data = _load();
              }),
              icon: const Icon(Icons.refresh),
              label: const Text('Consultar de nuevo'),
            ),
          ],
        );
      }
      final row = state.data as Map;
      return FormCard(
        title: 'Datos para el aporte',
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (row['prueba'] == true)
              const Padding(
                padding: EdgeInsets.only(bottom: 12),
                child: Text(
                  'DATOS FICTICIOS. No realices transferencias.',
                  style: TextStyle(fontWeight: FontWeight.w700),
                ),
              ),
            for (final e in {
              'organizacion': 'Organización',
              'titular': 'Titular',
              'banco': 'Banco',
              'tipo_cuenta': 'Tipo de cuenta',
              'numero_cuenta': 'Número de cuenta',
              'identificacion_titular': 'Identificación del titular',
            }.entries)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(e.value, style: const TextStyle(fontSize: 13)),
                    const SizedBox(height: 4),
                    ReadableText(
                      row[e.key] is String && row[e.key].toString().isNotEmpty
                          ? row[e.key].toString()
                          : 'No publicado',
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
            if (row['numero_cuenta'] is String)
              TextButton.icon(
                onPressed: () async {
                  await Clipboard.setData(
                    ClipboardData(text: row['numero_cuenta'] as String),
                  );
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Número de cuenta copiado')),
                    );
                  }
                },
                icon: const Icon(Icons.copy_outlined),
                label: const Text('Copiar número de cuenta'),
              ),
            Text(
              row['nota'] is String
                  ? row['nota'] as String
                  : 'La transferencia se realiza fuera de la aplicación.',
            ),
          ],
        ),
      );
    },
  );
}
