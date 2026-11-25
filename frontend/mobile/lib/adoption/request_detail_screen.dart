import '../design/readable_text.dart';

import 'package:flutter/material.dart';

import '../auth/session.dart';
import '../design/lpn_app_bar.dart';
import '../design/refined_surfaces.dart';
import '../explore/session_action_gate.dart';
import '../core/inline_webp.dart';
import 'adoption_screens.dart' show StatusPanel, messageFor;
import 'questionnaire_screen.dart' show EvaluationSummary, evaluationVersion;

class RequestDetailScreen extends StatelessWidget {
  const RequestDetailScreen({
    super.key,
    required this.session,
    required this.id,
  });
  final Session session;
  final int id;
  @override
  Widget build(BuildContext context) => SessionActionGate(
    session: session,
    title: 'Detalle de solicitud',
    message: 'Inicia sesión para consultar tu solicitud.',
    form: (identity) => _RequestDetail(
      key: ValueKey((session.identityRevision, identity)),
      session: session,
      id: id,
    ),
  );
}

class _RequestDetail extends StatefulWidget {
  const _RequestDetail({super.key, required this.session, required this.id});
  final Session session;
  final int id;
  @override
  State<_RequestDetail> createState() => _RequestDetailState();
}

class _RequestDetailState extends State<_RequestDetail> {
  late Future<Object?> _data = _load();
  bool _refreshing = true;
  Future<Object?> _load() => widget.session
      .authorized(
        (token) => widget.session.api.get(
          '/api/adopcion/solicitudes/${widget.id}/',
          token: token,
        ),
      )
      .whenComplete(() {
        if (mounted) setState(() => _refreshing = false);
      });
  Future<void> _refresh() async {
    if (_refreshing) return;
    _refreshing = true;
    final next = _load();
    setState(() {
      _data = next;
    });
    try {
      await next;
    } on Exception {
      /* The error panel offers retry. */
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(
      context,
      'Solicitud #${widget.id}',
      actions: [
        IconButton(
          tooltip: 'Actualizar solicitud',
          onPressed: _refreshing ? null : _refresh,
          icon: const Icon(Icons.refresh),
        ),
      ],
    ),
    body: FutureBuilder<Object?>(
      future: _data,
      builder: (context, state) {
        if (state.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (state.hasError || state.data is! Map) {
          return StatusPanel(
            message: messageFor(
              state.error,
              'No pudimos consultar esta solicitud.',
            ),
            action: _refresh,
            actionLabel: 'Reintentar',
          );
        }
        final row = state.data as Map;
        if (row['id_solicitud_adopcion'] != widget.id) {
          return const StatusPanel(
            message: 'No pudimos verificar esta solicitud.',
          );
        }
        final photo = inlineWebp(row['foto_miniatura']);
        final requested = DateTime.tryParse(
          row['fecha_solicitud']?.toString() ?? '',
        );
        final resolved = DateTime.tryParse(
          row['fecha_resolucion']?.toString() ?? '',
        );
        final history = row['historial'] is List
            ? row['historial'] as List
            : const [];
        return ListView(
          padding: EdgeInsets.symmetric(
            vertical: 16,
            horizontal: ((MediaQuery.sizeOf(context).width - 640) / 2).clamp(
              16.0,
              double.infinity,
            ),
          ),
          children: [
            FormCard(
              title: row['mascota__nombre']?.toString() ?? 'Tu solicitud',
              icon: Icons.pets_outlined,
              tone: 0,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  if (photo != null)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Align(
                        alignment: AlignmentDirectional.centerStart,
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(16),
                          child: Image.memory(
                            photo,
                            width: 96,
                            height: 96,
                            fit: BoxFit.cover,
                            semanticLabel: 'Foto de la mascota de tu solicitud',
                          ),
                        ),
                      ),
                    ),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.info_outline, size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          row['estado_adopcion__nombre']?.toString() ??
                              'Estado no disponible',
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                      ),
                    ],
                  ),
                  if (requested != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        'Solicitada el ${MaterialLocalizations.of(context).formatMediumDate(requested.toLocal())}',
                      ),
                    ),
                  if (resolved != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        'Resuelta el ${MaterialLocalizations.of(context).formatMediumDate(resolved.toLocal())}',
                      ),
                    ),
                ],
              ),
            ),
            if (row['motivo_decision'] is String &&
                (row['motivo_decision'] as String).isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 20),
                child: FormCard(
                  title: 'Motivo de la decisión',
                  icon: Icons.notes_outlined,
                  tone: 2,
                  child: ReadableText(row['motivo_decision'] as String),
                ),
              ),
            const SizedBox(height: 24),
            if (row['evaluacion'] case final Map evaluation)
              if (evaluation['version'] == evaluationVersion &&
                  evaluation['respuestas'] is Map)
                ExpansionTile(
                  title: const Text('Tus respuestas iniciales'),
                  subtitle: const Text(
                    'Conservadas desde el envío de la solicitud',
                  ),
                  children: [
                    EvaluationSummary(
                      answers: Map<String, dynamic>.from(
                        evaluation['respuestas'] as Map,
                      ),
                    ),
                  ],
                ),
            const Text(
              'Historial de la solicitud',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 12),
            if (history.isEmpty)
              const Text('Todavía no hay movimientos adicionales.'),
            for (final event in history.whereType<Map>())
              Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: FormCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        event['estado_nuevo__nombre']?.toString() ?? '',
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                      if (DateTime.tryParse(
                            event['fecha_cambio']?.toString() ?? '',
                          ) !=
                          null)
                        Text(
                          MaterialLocalizations.of(context).formatMediumDate(
                            DateTime.parse(event['fecha_cambio'] as String)
                                .toLocal(),
                          ),
                        ),
                      const SizedBox(height: 8),
                      ReadableText(event['observacion']?.toString() ?? ''),
                    ],
                  ),
                ),
              ),
          ],
        );
      },
    ),
  );
}
