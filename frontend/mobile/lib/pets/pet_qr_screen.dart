import '../design/lpn_app_bar.dart';

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../adoption/adoption_screens.dart' show messageFor;
import 'owned_pets_api.dart';

/// Only the server issues this identifier. It never grants clinical access.
class PetQrScreen extends StatelessWidget {
  const PetQrScreen({super.key, required this.api, required this.petId});
  final OwnedPetsApi api;
  final int petId;

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'QR de la mascota'),
    body: ListenableBuilder(
      listenable: api.session,
      builder: (context, _) => api.session.signedIn
          ? _QrBody(
              key: ValueKey((
                api.session.identityRevision,
                api.session.account!.email,
                petId,
              )),
              api: api,
              petId: petId,
            )
          : const Center(
              child: Text('Inicia sesión de nuevo para generar un QR.'),
            ),
    ),
  );
}

class _QrBody extends StatefulWidget {
  const _QrBody({super.key, required this.api, required this.petId});
  final OwnedPetsApi api;
  final int petId;
  @override
  State<_QrBody> createState() => _QrBodyState();
}

class _QrBodyState extends State<_QrBody> with WidgetsBindingObserver {
  PetQr? _qr;
  Timer? _expiry;
  String? _message;
  bool _busy = false;
  int _request = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    _request++;
    _expiry?.cancel();
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state != AppLifecycleState.resumed && (_qr != null || _busy)) {
      _request++;
      _expiry?.cancel();
      setState(() {
        _qr = null;
        _busy = false;
        _message = 'Se ocultó el QR al salir de la app. Si lo necesitas, genera otro; el anterior dejará de funcionar.';
      });
    }
  }

  Future<void> _generate() async {
    if (_busy) return;
    if (_qr != null) {
      final replace = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('¿Reemplazar el QR?'),
          content: const Text(
            'El código anterior dejará de funcionar inmediatamente.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancelar'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Generar otro'),
            ),
          ],
        ),
      );
      if (!mounted || replace != true || _busy) return;
    }
    final request = ++_request;
    _expiry?.cancel();
    setState(() {
      _qr = null;
      _message = null;
      _busy = true;
    });
    try {
      final qr = await widget.api.generateQr(widget.petId);
      if (!mounted || request != _request) return;
      setState(() => _qr = qr);
      _expiry = Timer(qr.expires.difference(DateTime.now()), () {
        if (!mounted) return;
        setState(() {
          _qr = null;
          _message = 'El QR venció. Genera otro cuando lo necesites.';
        });
      });
    } on Exception catch (error) {
      if (!mounted || request != _request) return;
      setState(
        () => _message = messageFor(
          error,
          'No pudimos generar el QR. Intenta de nuevo.',
        ),
      );
    } finally {
      if (mounted && request == _request) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Column(
    children: [
      Expanded(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            const Icon(Icons.qr_code_2, size: 36),
            const SizedBox(height: 12),
            Text(
              'Identificación temporal',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            const Text(
              'Este QR identifica a la mascota durante 24 horas. No contiene su historial médico ni datos de contacto. El profesional necesita su cuenta y autorización vigente para registrar una atención.',
            ),
            const SizedBox(height: 16),
            if (_qr case final qr?) ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Center(
                        child: ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 280),
                          child: AspectRatio(
                            aspectRatio: 1,
                            child: QrImageView(
                              data: qr.code,
                              backgroundColor: Colors.white,
                              padding: const EdgeInsets.all(20),
                              semanticsLabel:
                                  'QR temporal de identificación de tu mascota',
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Vence: ${MaterialLocalizations.of(context).formatMediumDate(qr.expires.toLocal())}, ${MaterialLocalizations.of(context).formatTimeOfDay(TimeOfDay.fromDateTime(qr.expires.toLocal()))}',
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
            ],
            if (_message != null) ...[
              Semantics(liveRegion: true, child: Text(_message!)),
              const SizedBox(height: 12),
            ],
            const SizedBox(height: 12),
            const Text(
              'Cada generación invalida el QR anterior. El código se muestra solo aquí: no se guarda en el teléfono y se oculta al salir de la app. Ocultarlo no lo revoca en el servidor; vence o se reemplaza al generar otro.',
            ),
          ],
        ),
      ),
      SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 12),
          child: SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: _busy ? null : _generate,
              icon: _busy
                  ? const SizedBox.square(
                      dimension: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.qr_code_2),
              label: Text(
                _busy
                    ? 'Generando…'
                    : _qr == null
                    ? 'Generar QR'
                    : 'Generar otro QR',
              ),
            ),
          ),
        ),
      ),
    ],
  );
}
