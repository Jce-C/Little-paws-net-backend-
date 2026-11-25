import '../design/form_surfaces.dart';
import '../design/lpn_app_bar.dart';
import '../design/lpn_theme.dart';

import 'package:flutter/material.dart';

import '../adoption/adoption_screens.dart' show messageFor;
import 'session.dart';
import 'public_avatar.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key, required this.session});
  final Session session;

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: session,
    builder: (context, _) {
      final account = session.account;
      if (account == null) {
        return Scaffold(
          appBar: lpnAppBar(context, 'Mi perfil'),
          body: const Center(
            child: Text('Inicia sesión de nuevo para editar tu perfil.'),
          ),
        );
      }
      return _ProfileForm(
        key: ValueKey((session.identityRevision, account.email)),
        session: session,
        initial: account,
      );
    },
  );
}

class _ProfileForm extends StatefulWidget {
  const _ProfileForm({super.key, required this.session, required this.initial});
  final Session session;
  final Account initial;
  @override
  State<_ProfileForm> createState() => _ProfileFormState();
}

class _ProfileFormState extends State<_ProfileForm> {
  final _form = GlobalKey<FormState>();
  late final _name = TextEditingController(text: widget.initial.name)
    ..addListener(_changed);
  late final _phone = TextEditingController(text: widget.initial.phone)
    ..addListener(_changed);
  bool _saving = false;
  bool _leaving = false;
  bool _confirming = false;
  String? _error;

  bool get _dirty =>
      _name.text.trim() != widget.initial.name ||
      _phone.text.trim() != widget.initial.phone;

  void _changed() => setState(() {});

  @override
  void dispose() {
    _name.dispose();
    _phone.dispose();
    super.dispose();
  }

  Future<void> _leave() async {
    if (_saving || _confirming) return;
    if (!_dirty) {
      Navigator.pop(context);
      return;
    }
    _confirming = true;
    final discard = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('¿Descartar cambios?'),
        content: const Text(
          'Tu perfil conservará los datos guardados anteriormente.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Seguir editando'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Descartar'),
          ),
        ],
      ),
    );
    _confirming = false;
    if (!mounted || discard != true) return;
    setState(() => _leaving = true);
    await WidgetsBinding.instance.endOfFrame;
    if (mounted) Navigator.pop(context);
  }

  Future<void> _save() async {
    if (_saving || !_dirty || !validateLpnForm(_form)) return;
    FocusScope.of(context).unfocus();
    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      await widget.session.updateProfile(
        name: _name.text.trim() != widget.initial.name ? _name.text : null,
        phone: _phone.text.trim() != widget.initial.phone ? _phone.text : null,
      );
      if (!mounted) return;
      setState(() {
        _leaving = true;
        _saving = false;
      });
      await WidgetsBinding.instance.endOfFrame;
      if (!mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Tu perfil se actualizó.')));
      Navigator.pop(context);
    } on Exception catch (error) {
      if (mounted) {
        setState(() {
          _saving = false;
          _error = messageFor(
            error,
            'No pudimos guardar tu perfil. Intenta de nuevo.',
          );
        });
        await showDialog<void>(
          context: context,
          builder: (context) => AlertDialog(
            scrollable: true,
            title: const Text('Revisa tu perfil'),
            content: Text(_error!),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Cerrar'),
              ),
            ],
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) => PopScope(
    canPop: !_saving && (!_dirty || _leaving),
    onPopInvokedWithResult: (didPop, _) {
      if (!didPop) _leave();
    },
    child: Scaffold(
      appBar: lpnAppBar(
        context,
        'Mi perfil',
        actions: [
          IconButton(
            tooltip: _dirty
                ? 'Guarda tus datos antes de cambiar la foto'
                : 'Foto de perfil pública',
            onPressed: _saving || _dirty
                ? null
                : () => Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => AvatarScreen(session: widget.session),
                    ),
                  ),
            icon: const Icon(Icons.add_a_photo_outlined),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Form(
              key: _form,
              child: LpnFormScrollView(
                padding: const EdgeInsets.all(20),
                children: [
                  LpnFormSection(
                    title: 'Tu cuenta',
                    icon: Icons.person_outline,
                    tone: 0,
                    children: [
                      const Text(
                        'Actualiza tus datos de contacto. Tus roles y permisos se conservan.',
                      ),
                      const SizedBox(height: 16),
                      LpnInputSurface(
                        child: TextFormField(
                          key: const Key('profile-name'),
                          controller: _name,
                          enabled: !_saving,
                          maxLength: 150,
                          textCapitalization: TextCapitalization.words,
                          autofillHints: const [AutofillHints.name],
                          decoration: const InputDecoration(
                            labelText: 'Nombre completo',
                          ),
                          validator: (value) => (value ?? '').trim().isEmpty
                              ? 'Escribe tu nombre.'
                              : null,
                        ),
                      ),
                      const SizedBox(height: 16),
                      LpnInputSurface(
                        child: TextFormField(
                          key: const Key('profile-phone'),
                          controller: _phone,
                          enabled: !_saving,
                          maxLength: 20,
                          keyboardType: TextInputType.phone,
                          autofillHints: const [AutofillHints.telephoneNumber],
                          decoration: const InputDecoration(
                            labelText: 'Teléfono (opcional)',
                            helperText: 'Puedes dejarlo vacío para eliminarlo.',
                          ),
                          validator: (value) {
                            final text = (value ?? '').trim();
                            final digits = text
                                .replaceAll(RegExp(r'\D'), '')
                                .length;
                            return text.isNotEmpty &&
                                    (!RegExp(r'^[+0-9(). \-]+$')
                                            .hasMatch(text) ||
                                        digits < 7 ||
                                        digits > 15)
                                ? 'Usa entre 7 y 15 dígitos.'
                                : null;
                          },
                        ),
                      ),
                      const SizedBox(height: 20),
                      const Text(
                        'Correo de acceso',
                        style: TextStyle(fontWeight: FontWeight.w700),
                      ),
                      Text(widget.initial.email),
                      const Text(
                        'El correo no se cambia desde este formulario.',
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          SafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 12),
              child: Wrap(
                alignment: WrapAlignment.end,
                spacing: 12,
                runSpacing: 8,
                children: [
                  TextButton(
                    onPressed: _saving ? null : _leave,
                    child: const Text('Cancelar'),
                  ),
                  FilledButton.icon(
                    key: const Key('profile-save'),
                    onPressed: _saving || !_dirty ? null : _save,
                    icon: _saving
                        ? const SizedBox.square(
                            dimension: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.check),
                    label: Text(_saving ? 'Guardando…' : 'Guardar cambios'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    ),
  );
}
