import 'my_sponsorships_screen.dart';
import '../core/operation_key.dart';

import 'package:flutter/material.dart';

import '../auth/session.dart';
import '../core/api_client.dart';
import '../design/lpn_app_bar.dart';
import '../design/form_surfaces.dart';
import '../explore/session_action_gate.dart';
import '../explore/bank_instructions.dart';

class SponsorshipScreen extends StatelessWidget {
  const SponsorshipScreen({
    super.key,
    required this.session,
    required this.reportId,
  });
  final Session session;
  final int reportId;
  @override
  Widget build(BuildContext context) => SessionActionGate(
    session: session,
    title: 'Apadrinar este caso',
    message: 'Inicia sesión para apoyar este caso.',
    form: (identity) =>
        _SponsorshipForm(key: identity, session: session, reportId: reportId),
  );
}

class _SponsorshipForm extends StatefulWidget {
  const _SponsorshipForm({
    super.key,
    required this.session,
    required this.reportId,
  });
  final Session session;
  final int reportId;
  @override
  State<_SponsorshipForm> createState() => _SponsorshipFormState();
}

class _SponsorshipFormState extends State<_SponsorshipForm> {
  final _amount = TextEditingController();
  int? _id;
  bool _busy = false, _uncertain = false;
  String? _error;
  String? _operationKey;
  @override
  void dispose() {
    _amount.dispose();
    super.dispose();
  }

  Future<void> _commit({bool recover = false}) async {
    if (_busy || (_uncertain && !recover) || _id != null) return;
    if (recover && widget.session.account?.safeRetries != true) return;
    if (!RegExp(r'^[0-9]{1,10}(\.[0-9]{1,2})?$')
            .hasMatch(_amount.text.trim()) ||
        (double.tryParse(_amount.text) ?? 0) <= 0) {
      setState(() => _error = 'Escribe un monto positivo en COP.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    _operationKey ??= newOperationKey();
    try {
      final row = await widget.session.authorized(
        (token) => widget.session.api.post(
          '/api/apadrinamientos/',
          {
            'id_reporte': widget.reportId,
            'monto_comprometido': _amount.text.trim(),
          },
          token: token,
          operationKey: _operationKey,
        ),
      );
      if (row is! Map || row['id_apadrinamiento'] is! int) {
        throw const ApiException('No pudimos confirmar el compromiso.');
      }
      if (mounted) setState(() => _id = row['id_apadrinamiento'] as int);
    } on Exception catch (e) {
      if (mounted) {
        setState(() {
          _error = e is ApiException
              ? e.message
              : 'No pudimos confirmar el compromiso.';
          _uncertain =
              e is! ApiException || e.status == null || e.status! >= 500;
          if (!_uncertain) _operationKey = null;
          if (_uncertain) {
            _error = widget.session.account?.safeRetries == true
                ? 'No se confirmó el compromiso. Comprueba y completa la misma operación sin crear otro.'
                : 'Este servidor no admite reintentos seguros. Revisa Mis compromisos antes de registrar otro.';
          }
        });
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Apadrinar caso #${widget.reportId}'),
    bottomNavigationBar: _id != null
        ? null
        : LpnActionBar(
            avoidKeyboard: true,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                FilledButton(
                  onPressed:
                      _busy ||
                          (_uncertain &&
                              widget.session.account?.safeRetries != true)
                      ? null
                      : () => _commit(recover: _uncertain),
                  child: Text(
                    _busy
                        ? 'Registrando…'
                        : (_uncertain
                              ? 'Comprobar compromiso'
                              : 'Registrar compromiso'),
                  ),
                ),
                if (_uncertain)
                  TextButton(
                    onPressed: _busy
                        ? null
                        : () => Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) =>
                                  MySponsorshipsScreen(session: widget.session),
                            ),
                          ),
                    child: const Text('Ver mis compromisos'),
                  ),
              ],
            ),
          ),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        LpnFormSection(
          title: 'Tu compromiso',
          icon: Icons.volunteer_activism_outlined,
          tone: 1,
          children: [
            const Text(
              'Tu ayuda puede cambiar su historia.',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 12),
            const Text(
              'El compromiso no cobra dinero. Consulta únicamente la cuenta de la organización que tiene este caso.',
            ),
            const SizedBox(height: 20),
            if (_id == null)
              TextField(
                controller: _amount,
                enabled: !_busy && !_uncertain,
                keyboardType: const TextInputType.numberWithOptions(
                  decimal: true,
                ),
                decoration: const InputDecoration(
                  labelText: 'Monto del compromiso (COP)',
                ),
              )
            else ...[
              Text('Compromiso #$_id registrado'),
              const SizedBox(height: 16),
              BankInstructions(
                session: widget.session,
                path: '/api/apadrinamientos/$_id/cuenta/',
              ),
            ],
            if (_error != null)
              Padding(
                padding: const EdgeInsets.only(top: 16),
                child: Text(_error!, semanticsLabel: _error),
              ),
          ],
        ),
      ],
    ),
  );
}
