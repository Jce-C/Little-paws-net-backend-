import 'package:flutter/foundation.dart';

import '../design/access_reference.dart';
import '../design/form_surfaces.dart';

import 'package:flutter/material.dart';

import '../core/api_client.dart';
import 'session.dart';
import 'account_overview.dart';

Future<bool> openLogin(BuildContext context, Session session) async =>
    await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => LoginScreen(session: session)),
    ) ??
    false;

class AccountScreen extends StatelessWidget {
  const AccountScreen({super.key, required this.session});
  final Session session;

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: session,
    builder: (context, child) {
      final account = session.account;
      return ListView(
        padding: EdgeInsets.fromLTRB(
          24,
          24,
          24,
          24 + MediaQuery.paddingOf(context).bottom,
        ),
        children: [
          const Text(
            'PERFIL',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 15, height: 1.4),
          ),
          const SizedBox(height: 20),
          Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 520),
              child: session.restoring
                  ? const Center(child: CircularProgressIndicator())
                  : account == null
                  ? Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        const Text(
                          'Accede para gestionar tus solicitudes de adopción.',
                        ),
                        const SizedBox(height: 16),
                        FilledButton(
                          onPressed: () => openLogin(context, session),
                          child: const Text('Iniciar sesión'),
                        ),
                      ],
                    )
                  : AccountOverview(
                      key: ValueKey((session.identityRevision, account.email)),
                      session: session,
                      account: account,
                    ),
            ),
          ),
        ],
      );
    },
  );
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({
    super.key,
    required this.session,
    this.initialRegister = false,
  });
  final Session session;
  final bool initialRegister;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _form = GlobalKey<FormState>();
  final _scroll = ScrollController();
  final _name = TextEditingController();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _confirmation = TextEditingController();
  final _passwordFocus = FocusNode();
  final _confirmationFocus = FocusNode();
  late bool _register = widget.initialRegister;
  bool _submitting = false;
  bool _attempted = false;
  bool _hidden = true;
  bool _remember = false;
  bool _rememberTouched = false;
  String? _error;

  Future<void> _rememberChanged(bool? value) async {
    _rememberTouched = true;
    setState(() => _remember = value == true);
    try {
      await widget.session.setRememberPreference(_remember);
    } on Exception {
      if (mounted) {
        setState(() => _remember = false);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'No pudimos guardar la preferencia en este dispositivo.',
            ),
          ),
        );
      }
    }
  }

  @override
  void initState() {
    super.initState();
    widget.session.loadRememberPreference().then((value) {
      if (mounted && !_rememberTouched) setState(() => _remember = value);
    });
  }

  @override
  void dispose() {
    _passwordFocus.dispose();
    _confirmationFocus.dispose();
    _scroll.dispose();
    _name.dispose();
    _email.dispose();
    _password.dispose();
    _confirmation.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_submitting) return;
    setState(() => _attempted = true);
    if (!validateLpnForm(_form)) return;
    FocusScope.of(context).unfocus();
    setState(() {
      _submitting = true;
      _error = null;
    });
    try {
      if (_register) {
        await widget.session.register(
          _name.text,
          _email.text,
          _password.text,
          remember: _remember,
        );
      } else {
        await widget.session.login(
          _email.text,
          _password.text,
          remember: _remember,
        );
      }
      if (mounted) Navigator.of(context).pop(true);
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } on Exception {
      if (mounted) {
        setState(
          () => _error = 'No pudimos confirmar el acceso. Intenta de nuevo.',
        );
      }
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Widget _fieldSurface(String label, {required Widget child}) {
    if (MediaQuery.textScalerOf(context).scale(18) <= 24) {
      return Semantics(container: true, child: child);
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 0, 20, 8),
          child: ExcludeSemantics(
            child: Text(
              label,
              key: ValueKey('access-caption-$label'),
              style: const TextStyle(
                color: AccessPalette.brown,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
        child,
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final compact =
        MediaQuery.sizeOf(context).height < 800 ||
        MediaQuery.viewInsetsOf(context).bottom > 0 ||
        MediaQuery.textScalerOf(context).scale(16) > 24;
    return Theme(
      data: referenceAccessTheme(
        Theme.of(context),
        insetLabels: MediaQuery.textScalerOf(context).scale(18) > 24,
      ),
      child: PopScope(
        canPop: !_submitting,
        child: Scaffold(
          bottomNavigationBar: compact
              ? LpnKeyboardSafeArea(
                  child: ColoredBox(
                    color: AccessPalette.sand,
                    child: Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 32,
                        vertical: 12,
                      ),
                      child: FilledButton(
                        key: const Key('account-submit'),
                        onPressed: _submitting ? null : _submit,
                        child: Text(
                          _submitting
                              ? 'Un momento…'
                              : _register
                              ? 'Crear cuenta'
                              : 'Ingresar',
                        ),
                      ),
                    ),
                  ),
                )
              : null,
          backgroundColor: AccessPalette.sand,
          appBar: referenceAccessAppBar(
            context,
            _register ? 'Crear cuenta' : 'Iniciar sesión',
          ),
          body: AccessBackground(
            key: const Key('access-wave'),
            child: SafeArea(
              child: Align(
                alignment: Alignment.topCenter,
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 520),
                  child: Form(
                    key: _form,
                    autovalidateMode: _attempted
                        ? AutovalidateMode.onUserInteraction
                        : AutovalidateMode.disabled,
                    child: ListView(
                      controller: _scroll,
                      shrinkWrap: false,
                      padding: const EdgeInsets.only(bottom: 28),
                      children: [
                        ReferenceAccessHero(
                          register: _register,
                          compact: compact,
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 20),
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 12),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                if (_register) ...[
                                  _fieldSurface(
                                    'Nombre completo',
                                    child: TextFormField(
                                      key: const Key('account-name'),
                                      textInputAction: TextInputAction.next,
                                      style: const TextStyle(
                                        color: Color(0xfffef3c7),
                                      ),
                                      controller: _name,
                                      enabled: !_submitting,
                                      textCapitalization:
                                          TextCapitalization.words,
                                      autofillHints: const [AutofillHints.name],
                                      decoration: const InputDecoration(
                                        labelText: 'Nombre completo',
                                      ),
                                      validator: (value) =>
                                          (value ?? '').trim().isEmpty
                                          ? 'Escribe tu nombre.'
                                          : null,
                                    ),
                                  ),
                                  const SizedBox(height: 16),
                                ],
                                _fieldSurface(
                                  'Correo electrónico',
                                  child: TextFormField(
                                    key: const Key('account-email'),
                                    textInputAction: TextInputAction.next,
                                    onFieldSubmitted: (_) =>
                                        _passwordFocus.requestFocus(),
                                    style: const TextStyle(
                                      color: Color(0xfffef3c7),
                                    ),
                                    controller: _email,
                                    enabled: !_submitting,
                                    keyboardType: TextInputType.emailAddress,
                                    autofillHints: const [AutofillHints.email],
                                    decoration: const InputDecoration(
                                      labelText: 'Correo electrónico',
                                    ),
                                    validator: (value) =>
                                        !(value ?? '').trim().contains('@')
                                        ? 'Escribe un correo válido.'
                                        : null,
                                  ),
                                ),
                                const SizedBox(height: 16),
                                _fieldSurface(
                                  'Contraseña',
                                  child: TextFormField(
                                    key: const Key('account-password'),
                                    focusNode: _passwordFocus,
                                    textInputAction: _register
                                        ? TextInputAction.next
                                        : TextInputAction.done,
                                    style: const TextStyle(
                                      color: Color(0xfffef3c7),
                                    ),
                                    controller: _password,
                                    enabled: !_submitting,
                                    obscureText: _hidden,
                                    autofillHints: [
                                      _register
                                          ? AutofillHints.newPassword
                                          : AutofillHints.password,
                                    ],
                                    decoration: InputDecoration(
                                      labelText: 'Contraseña',
                                      suffixIcon: IconButton(
                                        tooltip: _hidden
                                            ? 'Mostrar contraseña'
                                            : 'Ocultar contraseña',
                                        onPressed: () =>
                                            setState(() => _hidden = !_hidden),
                                        icon: Icon(
                                          _hidden
                                              ? Icons.visibility_outlined
                                              : Icons.visibility_off_outlined,
                                        ),
                                      ),
                                    ),
                                    onFieldSubmitted: (_) {
                                      if (!_register) {
                                        _submit();
                                      } else {
                                        _confirmationFocus.requestFocus();
                                      }
                                    },
                                    validator: (value) => (value ?? '').isEmpty
                                        ? 'Escribe tu contraseña.'
                                        : _register && (value ?? '').length < 12
                                        ? 'Usa al menos 12 caracteres.'
                                        : null,
                                  ),
                                ),
                                if (_register) ...[
                                  const SizedBox(height: 12),
                                  const Text(
                                    'Usa al menos 12 caracteres.',
                                    style: TextStyle(fontSize: 12),
                                  ),
                                  const SizedBox(height: 16),
                                  _fieldSurface(
                                    'Confirmar contraseña',
                                    child: TextFormField(
                                      key: const Key(
                                        'account-confirm-password',
                                      ),
                                      textInputAction: TextInputAction.done,
                                      focusNode: _confirmationFocus,
                                      style: const TextStyle(
                                        color: Color(0xfffef3c7),
                                      ),
                                      controller: _confirmation,
                                      enabled: !_submitting,
                                      obscureText: _hidden,
                                      autofillHints: const [
                                        AutofillHints.newPassword,
                                      ],
                                      decoration: const InputDecoration(
                                        labelText: 'Confirmar contraseña',
                                      ),
                                      validator: (value) =>
                                          value != _password.text
                                          ? 'Las contraseñas no coinciden.'
                                          : null,
                                      onFieldSubmitted: (_) => _submit(),
                                    ),
                                  ),
                                ],
                                if (!_register)
                                  Wrap(
                                    alignment: WrapAlignment.spaceBetween,
                                    crossAxisAlignment:
                                        WrapCrossAlignment.center,
                                    children: [
                                      Tooltip(
                                        message: kIsWeb
                                            ? 'Recuerda esta elección. Por seguridad, la sesión del navegador permanece solo mientras la app está abierta.'
                                            : 'Guardar sesión en el almacenamiento seguro del dispositivo',
                                        child: Row(
                                          mainAxisSize: MainAxisSize.min,
                                          children: [
                                            Checkbox(
                                              value: _remember,
                                              onChanged: _submitting
                                                  ? null
                                                  : _rememberChanged,
                                            ),
                                            const Flexible(
                                              child: Text(
                                                'Recordarme',
                                                style: TextStyle(fontSize: 13),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                      TextButton(
                                        onPressed: _submitting
                                            ? null
                                            : () => showDialog<void>(
                                                context: context,
                                                builder: (context) =>
                                                    AlertDialog(
                                                      title: const Text(
                                                        'Recuperar acceso',
                                                      ),
                                                      content: const Text(
                                                        'Solicita a un administrador de la plataforma que restablezca tu acceso. No compartas tu contraseña. La recuperación automática por correo aún no está habilitada.',
                                                      ),
                                                      actions: [
                                                        TextButton(
                                                          onPressed: () =>
                                                              Navigator.pop(
                                                                context,
                                                              ),
                                                          child: const Text(
                                                            'Entendido',
                                                          ),
                                                        ),
                                                      ],
                                                    ),
                                              ),
                                        child: const Text(
                                          '¿Olvidaste tu clave?',
                                          style: TextStyle(fontSize: 13),
                                        ),
                                      ),
                                    ],
                                  ),
                                if (_error != null) ...[
                                  const SizedBox(height: 12),
                                  Semantics(
                                    liveRegion: true,
                                    child: Text(
                                      _error!,
                                      style: TextStyle(
                                        color: Theme.of(context)
                                            .colorScheme
                                            .error,
                                      ),
                                    ),
                                  ),
                                ],
                                const SizedBox(height: 20),
                                if (!compact)
                                  Center(
                                    child: SizedBox(
                                      width: double.infinity,
                                      child: FilledButton(
                                        key: const Key('account-submit'),
                                        onPressed: _submitting ? null : _submit,
                                        child: Text(
                                          _submitting
                                              ? 'Un momento…'
                                              : _register
                                              ? 'Crear cuenta'
                                              : 'Ingresar',
                                        ),
                                      ),
                                    ),
                                  ),
                                TextButton(
                                  onPressed: _submitting
                                      ? null
                                      : () {
                                          FocusScope.of(context).unfocus();
                                          setState(() {
                                            _register = !_register;
                                            _attempted = false;
                                            _error = null;
                                          });
                                          WidgetsBinding.instance
                                              .addPostFrameCallback((_) {
                                                if (mounted &&
                                                    _scroll.hasClients) {
                                                  _scroll.jumpTo(0);
                                                }
                                              });
                                        },
                                  child: Text(
                                    _register
                                        ? 'Ya tengo una cuenta'
                                        : 'Registrarme',
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
