import '../design/lpn_app_bar.dart';
import '../design/form_surfaces.dart';
import '../design/lpn_theme.dart';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../adoption/adoption_screens.dart' show messageFor;
import '../core/api_client.dart' show ApiException;
import 'rescue_api.dart';

class AnonymousReportScreen extends StatefulWidget {
  const AnonymousReportScreen({
    super.key,
    required this.api,
    this.reportId,
    this.privateCode,
  });
  final RescueApi api;
  final int? reportId;
  final String? privateCode;
  @override
  State<AnonymousReportScreen> createState() => _AnonymousReportScreenState();
}

class _AnonymousReportScreenState extends State<AnonymousReportScreen> {
  final _form = GlobalKey<FormState>();
  late final _id = TextEditingController(
    text: widget.reportId?.toString() ?? '',
  );
  late final _code = TextEditingController(text: widget.privateCode ?? '');
  final _description = TextEditingController();
  final _contact = TextEditingController();
  String? _error;
  bool _sending = false;
  bool _uncertain = false;
  bool _discarding = false;
  bool get _dirty =>
      _description.text.trim().isNotEmpty ||
      _contact.text.trim().isNotEmpty ||
      _clearContact;

  Future<void> _cancel() async {
    if (_sending || _discarding) return;
    final leave =
        !_dirty ||
        await showDialog<bool>(
              context: context,
              builder: (context) => AlertDialog(
                title: const Text('¿Descartar los cambios?'),
                content: const Text(
                  'Saldrás del editor sin enviar más cambios. Lo que escribiste aquí no se conservará.',
                ),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(context, false),
                    child: const Text('Seguir editando'),
                  ),
                  FilledButton(
                    onPressed: () => Navigator.pop(context, true),
                    child: const Text('Descartar cambios'),
                  ),
                ],
              ),
            ) ==
            true;
    if (!mounted || !leave) return;
    setState(() => _discarding = true);
    await WidgetsBinding.instance.endOfFrame;
    if (mounted) await Navigator.of(context).maybePop();
  }

  bool _clearContact = false;

  @override
  void dispose() {
    for (final controller in [_id, _code, _description, _contact]) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _showError(String message) => showDialog<void>(
    context: context,
    builder: (context) => AlertDialog(
      scrollable: true,
      title: Text(_uncertain ? 'Verifica el cambio' : 'Revisa los datos'),
      content: Text(message),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cerrar'),
        ),
      ],
    ),
  );

  Future<void> _submit({bool close = false}) async {
    if (_sending || _uncertain || !validateLpnForm(_form)) return;
    if (!close &&
        !_clearContact &&
        _description.text.trim().isEmpty &&
        _contact.text.trim().isEmpty) {
      await _showError(
        'Escribe una descripción o un contacto nuevo para guardar cambios.',
      );
      return;
    }
    FocusScope.of(context).unfocus();
    if (close) {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('¿Cerrar este reporte?'),
          content: const Text(
            'Solo se puede cerrar si aún no fue aceptado. Una vez cerrado, dejará de admitir cambios con la clave privada.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancelar'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Cerrar reporte'),
            ),
          ],
        ),
      );
      if (!mounted || confirmed != true) return;
    }
    setState(() {
      _sending = true;
      _error = null;
    });
    try {
      final result = await widget.api.manageAnonymous(
        reportId: int.parse(_id.text),
        code: _code.text,
        description: _description.text,
        contact: _contact.text,
        clearContact: _clearContact,
        close: close,
      );
      if (!mounted) return;
      _code.clear();
      await Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => _AnonymousResultScreen(result: result),
        ),
      );
    } on Exception catch (error) {
      if (mounted) {
        setState(() {
          _uncertain =
              error is! ApiException ||
              error.status == null ||
              error.status! >= 500;
          _error = _uncertain
              ? 'El servidor podría haber guardado el cambio. Conservamos tus datos y no repetiremos el envío. Comprueba el reporte en Rescate antes de intentarlo de nuevo.'
              : messageFor(
                  error,
                  'No pudimos guardar el cambio. Revisa los datos.',
                );
        });
        await _showError(_error!);
      }
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  @override
  Widget build(BuildContext context) => PopScope(
    canPop: _discarding,
    onPopInvokedWithResult: (didPop, result) {
      if (!didPop) _cancel();
    },
    child: Scaffold(
      appBar: lpnAppBar(context, 'Reporte sin cuenta'),
      body: Form(
        key: _form,
        child: Column(
          children: [
            Expanded(
              child: LpnFormScrollView(
                padding: EdgeInsets.symmetric(
                  vertical: 16,
                  horizontal: ((MediaQuery.sizeOf(context).width - 640) / 2)
                      .clamp(16.0, double.infinity),
                ),
                children: [
                  LpnFormSection(
                    title: 'Información del reporte',
                    tone: 0,
                    icon: Icons.key_outlined,
                    description: 'Identifica el reporte con el número y la clave que recibiste.',
                    children: [
                      LpnInputSurface(
                        child: TextFormField(
                          key: const Key('anonymous-report-id'),
                          controller: _id,
                          enabled: !_sending && !_uncertain,
                          keyboardType: TextInputType.number,
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly,
                          ],
                          maxLength: 10,
                          decoration: const InputDecoration(
                            labelText: 'Número de reporte',
                            counterText: '',
                          ),
                          validator: (value) {
                            final number = int.tryParse(value ?? '');
                            return number == null ||
                                    number <= 0 ||
                                    number > 2147483647
                                ? 'Escribe un número de reporte válido.'
                                : null;
                          },
                        ),
                      ),
                      const SizedBox(height: 12),
                      LpnInputSurface(
                        child: TextFormField(
                          key: const Key('anonymous-report-code'),
                          controller: _code,
                          enabled: !_sending && !_uncertain,
                          obscureText: true,
                          autocorrect: false,
                          enableSuggestions: false,
                          enableIMEPersonalizedLearning: false,
                          keyboardType: TextInputType.visiblePassword,
                          maxLength: 128,
                          decoration: const InputDecoration(
                            labelText: 'Clave privada',
                            counterText: '',
                            helperText:
                                'No se guarda en el dispositivo ni se publica.',
                            helperMaxLines: 3,
                          ),
                          validator: (value) => (value ?? '').trim().isEmpty
                              ? 'Pega la clave que recibiste al enviar el reporte.'
                              : null,
                        ),
                      ),
                      const SizedBox(height: 20),
                    ],
                  ),
                  const SizedBox(height: 20),
                  LpnFormSection(
                    title: 'Datos que deseas actualizar',
                    tone: 1,
                    icon: Icons.edit_outlined,
                    description: 'Deja en blanco lo que no quieras reemplazar. Solo admite cambios mientras esté pendiente.',
                    children: [
                      LpnInputSurface(
                        child: TextFormField(
                          key: const Key('anonymous-report-description'),
                          controller: _description,
                          enabled: !_sending && !_uncertain,
                          minLines: 3,
                          maxLines: 5,
                          maxLength: 5000,
                          decoration: const InputDecoration(
                            labelText: 'Nueva descripción (opcional)',
                          ),
                        ),
                      ),
                      const Text(
                        'La descripción es pública. No incluyas teléfonos ni datos personales.',
                      ),
                      const SizedBox(height: 16),
                      LpnInputSurface(
                        child: TextFormField(
                          key: const Key('anonymous-report-contact'),
                          controller: _contact,
                          enabled: !_sending && !_uncertain && !_clearContact,
                          maxLength: 150,
                          decoration: const InputDecoration(
                            labelText: 'Nuevo contacto privado (opcional)',
                          ),
                        ),
                      ),
                      CheckboxListTile(
                        key: const Key('anonymous-report-clear-contact'),
                        contentPadding: EdgeInsets.zero,
                        value: _clearContact,
                        title: const Text(
                          'Eliminar el contacto privado del reporte',
                        ),
                        onChanged: _sending || _uncertain
                            ? null
                            : (value) => setState(
                                () => _clearContact = value ?? false,
                              ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  const LpnFormSection(
                    title: 'Confirmación de cambios',
                    tone: 2,
                    icon: Icons.fact_check_outlined,
                    children: [
                      Text(
                        'Guardar reemplaza únicamente los datos indicados. Cancelar conserva el reporte sin cambios.',
                      ),
                    ],
                  ),
                ],
              ),
            ),
            LpnActionBar(
              child: Wrap(
                alignment: WrapAlignment.end,
                spacing: 8,
                runSpacing: 4,
                children: [
                  TextButton(
                    key: const Key('anonymous-report-cancel'),
                    onPressed: _sending ? null : _cancel,
                    child: Text(_uncertain ? 'Salir del editor' : 'Cancelar'),
                  ),
                  TextButton(
                    key: const Key('anonymous-report-close'),
                    onPressed: _sending || _uncertain
                        ? null
                        : () => _submit(close: true),
                    child: const Text('Cerrar reporte'),
                  ),
                  FilledButton(
                    key: const Key('anonymous-report-save'),
                    style: FilledButton.styleFrom(
                      textStyle: const TextStyle(
                        fontFamily: 'Inter',
                        fontSize: 14,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    onPressed: _sending || _uncertain ? null : _submit,
                    child: Text(_sending ? 'Guardando…' : 'Guardar cambios'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

class _AnonymousResultScreen extends StatelessWidget {
  const _AnonymousResultScreen({required this.result});
  final ReportReceipt result;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Cambio confirmado'),
    body: ListView(
      padding: const EdgeInsets.all(24),
      children: [
        const Icon(Icons.check_circle_outline, size: 64),
        const SizedBox(height: 16),
        Text(
          'Reporte #${result.id}',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        const SizedBox(height: 12),
        Text('Estado: ${result.status}'),
        const SizedBox(height: 12),
        const Text(
          'El servidor confirmó la operación. La clave privada no se muestra en esta pantalla.',
        ),
        const SizedBox(height: 24),
        FilledButton(
          onPressed: () =>
              Navigator.of(context).popUntil((route) => route.isFirst),
          child: const Text('Volver a rescates'),
        ),
      ],
    ),
  );
}
