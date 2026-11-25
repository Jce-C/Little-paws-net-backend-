import '../design/form_surfaces.dart';
import '../design/refined_surfaces.dart';

import 'package:flutter/material.dart';

import '../auth/session.dart';
import 'session_action_gate.dart';
import '../core/api_client.dart';
import '../design/lpn_app_bar.dart';
import '../adoption/adoption_screens.dart' show messageFor;

class PublicMessageScreen extends StatelessWidget {
  const PublicMessageScreen({
    super.key,
    required this.api,
    required this.session,
    required this.path,
    required this.title,
    this.extra = const {},
    this.textKey = 'contenido',
    this.public = true,
    this.targetLabel,
  });
  final ApiClient api;
  final Session session;
  final String path, title, textKey;
  final Map<String, Object?> extra;
  final bool public;
  final String? targetLabel;
  @override
  Widget build(BuildContext context) => SessionActionGate(
    session: session,
    title: title,
    message: public
        ? 'Inicia sesión para publicar un mensaje.'
        : 'Inicia sesión para registrar tu interés.',
    form: (identity) => _MessageForm(key: identity, screen: this),
  );
}

class _MessageForm extends StatefulWidget {
  const _MessageForm({super.key, required this.screen});
  final PublicMessageScreen screen;
  @override
  State<_MessageForm> createState() => _PublicMessageScreenState();
}

class _PublicMessageScreenState extends State<_MessageForm> {
  final _text = TextEditingController();
  String? _identity;
  bool _busy = false, _uncertain = false, _canLeave = false;
  String? _error;
  DialogRoute<bool>? _discardRoute;
  @override
  void initState() {
    super.initState();
    _identity = widget.screen.session.account?.email;
    _text.addListener(_changed);
  }

  void _changed() => setState(() {});
  @override
  void dispose() {
    final dialog = _discardRoute;
    if (dialog != null) {
      // Disposal can happen while SessionActionGate is rebuilding the tree.
      // Remove only this form's dialog, never pop the new account's route.
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (dialog.isActive) dialog.navigator?.removeRoute(dialog);
      });
    }
    _text.removeListener(_changed);
    _text.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    if (_busy || _uncertain) return;
    if (_text.text.trim().isEmpty) {
      setState(() => _error = 'Escribe un mensaje antes de enviarlo.');
      return;
    }
    if (_identity == null ||
        _identity != widget.screen.session.account?.email) {
      setState(
        () => _error = 'La cuenta cambió. Abre el formulario nuevamente para confirmar con quién publicas.',
      );
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final result = await widget.screen.session.authorized(
        (token) => widget.screen.api.post(widget.screen.path, {
          ...widget.screen.extra,
          widget.screen.textKey: _text.text.trim(),
        }, token: token),
      );
      if (result is! Map || result['id'] is! int) {
        throw const ApiException('No pudimos confirmar el resultado.');
      }
      if (mounted) {
        _canLeave = true;
        Navigator.of(context).pop(true);
      }
    } on Exception catch (e) {
      if (mounted) {
        setState(() {
          _uncertain =
              e is! ApiException || e.status == null || e.status! >= 500;
          _error = _uncertain
              ? 'No pudimos confirmar el envío. Vuelve al listado para comprobarlo antes de enviar otra vez.'
              : messageFor(e, 'No pudimos enviar el mensaje.');
        });
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _discard() async {
    if (_discardRoute != null) return;
    final navigator = Navigator.of(context, rootNavigator: true);
    final route = DialogRoute<bool>(
      context: context,
      themes: InheritedTheme.capture(from: context, to: navigator.context),
      builder: (context) => AlertDialog(
        title: Text(
          _uncertain ? 'Volver al listado' : '¿Descartar el borrador?',
        ),
        content: Text(
          _uncertain
              ? 'No pudimos confirmar si se guardó. Al volver se actualizará el listado; compruébalo antes de enviar otra vez.'
              : 'El texto aún no se ha guardado. Puedes seguir editándolo.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Seguir editando'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: Text(_uncertain ? 'Volver y comprobar' : 'Descartar'),
          ),
        ],
      ),
    );
    _discardRoute = route;
    bool? discard;
    try {
      discard = await navigator.push(route);
    } finally {
      _discardRoute = null;
    }
    if (discard == true && mounted) {
      _canLeave = true;
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) => PopScope(
    canPop: !_busy && (_canLeave || _text.text.trim().isEmpty),
    onPopInvokedWithResult: (didPop, _) {
      if (!didPop && !_busy) _discard();
    },
    child: Scaffold(
      appBar: lpnAppBar(context, widget.screen.title),
      bottomNavigationBar: LpnKeyboardSafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (_error != null)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Semantics(
                    liveRegion: true,
                    child: Text(
                      _error!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                  ),
                ),
              FilledButton(
                onPressed: _busy || _uncertain ? null : _send,
                child: Text(_busy ? 'Enviando…' : 'Enviar'),
              ),
            ],
          ),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text(
            widget.screen.title,
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 16),
          FormCard(
            title: 'Destinatario y privacidad',
            icon: Icons.person_outline,
            tone: 0,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (widget.screen.targetLabel != null) ...[
                  Text(
                    widget.screen.targetLabel!,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 12),
                ],
                Text(
                  'Envías el mensaje como ${widget.screen.session.account?.name ?? "tu cuenta"}',
                ),
                const SizedBox(height: 12),
                Text(
                  widget.screen.public
                      ? 'Tu nombre y tu mensaje serán públicos. No incluyas información privada de otras personas.'
                      : 'Se registra tu interés. No equivale a una aceptación ni a una donación recibida.',
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          FormCard(
            title: 'Tu mensaje',
            icon: Icons.chat_bubble_outline,
            tone: 2,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Ideas para empezar',
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                const SizedBox(height: 8),
                DraftSuggestions(
                  values: widget.screen.public
                      ? const [
                          'Una historia de rescate',
                          'Consejos de cuidado',
                          'Una pregunta a la comunidad',
                        ]
                      : const [
                          'Quiero conocer más',
                          'Puedo ofrecer mi tiempo',
                          'Puedo apoyar con insumos',
                        ],
                  enabled: !_busy && !_uncertain,
                  onSelected: (value) {
                    if (_text.text.trim().isNotEmpty) {
                      _text.text = '${_text.text}\n$value: ';
                    } else {
                      _text.text = '$value: ';
                    }
                    _text.selection = TextSelection.collapsed(
                      offset: _text.text.length,
                    );
                  },
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _text,
                  enabled: !_busy && !_uncertain,
                  minLines: 5,
                  maxLines: 12,
                  maxLength:
                      widget.screen.path.contains('/comentarios/') ||
                          !widget.screen.public
                      ? 2000
                      : 5000,
                  decoration: const InputDecoration(labelText: 'Tu mensaje'),
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}
