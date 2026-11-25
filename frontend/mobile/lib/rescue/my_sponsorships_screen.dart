import 'package:flutter/material.dart';

import '../auth/session.dart';
import '../core/api_client.dart';
import '../design/lpn_app_bar.dart';
import '../design/refined_surfaces.dart';
import '../explore/session_action_gate.dart';
import '../explore/bank_instructions.dart';
import '../adoption/adoption_screens.dart' show messageFor;

class MySponsorshipsScreen extends StatelessWidget {
  const MySponsorshipsScreen({super.key, required this.session});
  final Session session;
  @override
  Widget build(BuildContext context) => SessionActionGate(
    session: session,
    title: 'Mis compromisos',
    message: 'Inicia sesión para consultar tus compromisos.',
    form: (identity) => _History(key: identity, session: session),
  );
}

class _History extends StatefulWidget {
  const _History({super.key, required this.session});
  final Session session;
  @override
  State<_History> createState() => _HistoryState();
}

class _HistoryState extends State<_History> {
  final _rows = <Map<String, dynamic>>[];
  bool _loading = false;
  String? _next, _error;
  int _generation = 0;
  @override
  void initState() {
    super.initState();
    _load(reset: true);
  }

  Future<void> _load({bool reset = false}) async {
    if (_loading) return;
    final generation = ++_generation;
    final cursor = reset ? null : _next;
    setState(() {
      _loading = true;
      _error = null;
      if (reset) {
        _rows.clear();
        _next = null;
      }
    });
    try {
      final result = await widget.session.authorized(
        (token) => widget.session.api.get(
          '/api/apadrinamientos/mios/${cursor == null ? '' : '?antes=$cursor'}',
          token: token,
        ),
      );
      if (result is! Map || result['results'] is! List) {
        throw const ApiException('No pudimos interpretar tus compromisos.');
      }
      final rows = (result['results'] as List).map((value) {
        if (value is! Map<String, dynamic> ||
            value['id_apadrinamiento'] is! int ||
            (value['id_apadrinamiento'] as int) <= 0 ||
            value['reporte_id'] is! int ||
            value['organizacion'] is! String ||
            value['monto_comprometido'] is! String ||
            value['estado'] is! String) {
          throw const ApiException('No pudimos interpretar este compromiso.');
        }
        return value;
      }).toList();
      final next = result['next_cursor'];
      if (rows.length > 20 ||
          (next != null &&
              (next is! String ||
                  !RegExp(r'^[1-9][0-9]{0,9}$').hasMatch(next) ||
                  (cursor != null && int.parse(next) >= int.parse(cursor))))) {
        throw const ApiException('La página de compromisos no es válida.');
      }
      if (mounted && generation == _generation) {
        setState(() {
          final known = _rows.map((r) => r['id_apadrinamiento']).toSet();
          _rows.addAll(
            rows.where((r) => !known.contains(r['id_apadrinamiento'])),
          );
          _next = next as String?;
        });
      }
    } on Exception catch (e) {
      if (mounted && generation == _generation) {
        setState(
          () => _error = messageFor(e, 'No pudimos consultar tus compromisos.'),
        );
      }
    } finally {
      if (mounted && generation == _generation) {
        setState(() => _loading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Mis compromisos'),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text('Compromisos registrados, no pagos confirmados.'),
        Align(
          alignment: Alignment.centerRight,
          child: IconButton(
            tooltip: 'Actualizar compromisos',
            onPressed: _loading ? null : () => _load(reset: true),
            icon: const Icon(Icons.refresh),
          ),
        ),
        if (_loading) const LinearProgressIndicator(),
        if (_error != null) ...[
          Text(_error!),
          TextButton(
            onPressed: _loading ? null : () => _load(reset: _rows.isEmpty),
            child: const Text('Consultar de nuevo'),
          ),
        ],
        if (!_loading && _error == null && _rows.isEmpty)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 24),
            child: Text('Todavía no tienes compromisos registrados.'),
          ),
        for (final row in _rows)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: FormCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    row['organizacion'] as String,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Compromiso #${row['id_apadrinamiento']} para el reporte #${row['reporte_id']}',
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${row['monto_comprometido']} COP',
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  Text(row['estado'] as String),
                  if (DateTime.tryParse(
                        row['fecha_compromiso']?.toString() ?? '',
                      )
                      case final date?)
                    Text(
                      MaterialLocalizations.of(context)
                          .formatMediumDate(date.toLocal()),
                    ),
                  TextButton.icon(
                    onPressed: () => Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => SessionActionGate(
                          session: widget.session,
                          title: 'Cuenta del compromiso',
                          message: 'Inicia sesión para consultar esta cuenta.',
                          form: (identity) => Scaffold(
                            key: identity,
                            appBar: lpnAppBar(context, 'Cuenta del compromiso'),
                            body: SingleChildScrollView(
                              padding: const EdgeInsets.all(20),
                              child: BankInstructions(
                                session: widget.session,
                                path:
                                    '/api/apadrinamientos/${row['id_apadrinamiento']}/cuenta/',
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                    icon: const Icon(Icons.account_balance_outlined),
                    label: const Text('Ver cuenta'),
                  ),
                ],
              ),
            ),
          ),
        if (_next != null)
          TextButton(
            onPressed: _loading ? null : () => _load(),
            child: const Text('Cargar más compromisos'),
          ),
      ],
    ),
  );
}
