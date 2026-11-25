import 'package:flutter/material.dart';

import '../core/api_client.dart';
import '../design/form_surfaces.dart';
import '../design/adoption_form_style.dart';
import '../design/lpn_app_bar.dart';
import '../design/refined_surfaces.dart';
import '../design/readable_text.dart';
import '../design/lpn_theme.dart';
import '../explore/session_action_gate.dart';
import 'adoption_api.dart';
import 'adoption_screens.dart' show messageFor;

const evaluationVersion = 'adopcion-evaluacion-v1';
const evaluationNotice =
    'Autorizo a la organización responsable de esta adopción a consultar estas '
    'respuestas privadas para evaluar mi solicitud y contactarme sobre este proceso. '
    'No autorizo publicidad ni entrenamiento de IA. No debo incluir datos de otras personas.';

class AdoptionQuestion {
  const AdoptionQuestion(
    this.id,
    this.label, {
    this.options,
    this.limit = 150,
    this.minimum = 1,
    this.number = false,
    this.email = false,
    this.help,
  });
  final String id, label;
  final Map<Object, String>? options;
  final int limit, minimum;
  final bool number, email;
  final String? help;
  bool visible(Map<String, Object?> values) => switch (id) {
    'autorizacion_propietario' => values['tenencia'] == 'arrendada',
    'cantidad_mascotas' ||
    'otras_mascotas' ||
    'esterilizacion' => values['mascotas_actuales'] == true,
    'experiencia' => values['experiencia_previa'] == true,
    _ => true,
  };
}

const evaluationTitles = [
  'Contacto',
  'Vivienda y hogar',
  'Cuidados',
  'Experiencia',
  'Revisar y enviar',
];
const yesNo = <Object, String>{true: 'Sí', false: 'No'};
const evaluationQuestions = <List<AdoptionQuestion>>[
  [
    AdoptionQuestion('nombre', 'Nombres y apellidos'),
    AdoptionQuestion('documento', 'Documento de identidad', limit: 40),
    AdoptionQuestion('telefono', 'Teléfono de contacto', limit: 30),
    AdoptionQuestion('email', 'Correo electrónico', limit: 254, email: true),
    AdoptionQuestion('direccion', 'Dirección de residencia', limit: 300),
  ],
  [
    AdoptionQuestion(
      'vivienda',
      'Tipo de vivienda',
      options: {'casa': 'Casa', 'apartamento': 'Apartamento', 'otra': 'Otra'},
    ),
    AdoptionQuestion(
      'tenencia',
      'La vivienda es',
      options: {
        'propia': 'Propia',
        'arrendada': 'Arrendada',
        'otra': 'Otra situación',
      },
    ),
    AdoptionQuestion(
      'autorizacion_propietario',
      '¿El propietario permite animales?',
      options: {'si': 'Sí', 'no': 'No', 'pendiente': 'Debo confirmarlo'},
    ),
    AdoptionQuestion(
      'seguridad_espacio',
      '¿Cómo protegerás el espacio?',
      limit: 600,
      help: 'Por ejemplo, mallas en ventanas, balcones o cerramientos.',
    ),
    AdoptionQuestion(
      'personas_hogar',
      '¿Cuántas personas viven contigo, incluyéndote?',
      limit: 2,
      number: true,
    ),
    AdoptionQuestion(
      'acuerdo_hogar',
      '¿Todas están de acuerdo con adoptar?',
      options: yesNo,
    ),
  ],
  [
    AdoptionQuestion(
      'tiempo_cuidado',
      'Disponibilidad para cuidar',
      options: {
        'diario': 'Tengo tiempo cada día',
        'compartido': 'Compartiremos el cuidado',
        'por_organizar': 'Necesito organizarlo',
      },
    ),
    AdoptionQuestion(
      'recursos_cuidado',
      'Alimentación y atención veterinaria',
      options: {
        'disponibles': 'Puedo cubrirlas',
        'con_apoyo': 'Cuento con apoyo',
        'por_organizar': 'Necesito organizar los recursos',
      },
    ),
    AdoptionQuestion(
      'cuidados_especiales',
      'Cuidados especiales de esta mascota',
      options: {
        'si': 'Puedo asumirlos',
        'necesito_orientacion': 'Necesito orientación',
      },
    ),
    AdoptionQuestion(
      'seguimiento',
      'Seguimiento de la organización',
      options: {
        'si': 'Estoy de acuerdo en coordinarlo',
        'necesito_informacion': 'Quiero conocer las condiciones',
      },
    ),
  ],
  [
    AdoptionQuestion(
      'mascotas_actuales',
      '¿Tienes otras mascotas?',
      options: yesNo,
    ),
    AdoptionQuestion(
      'cantidad_mascotas',
      '¿Cuántas mascotas tienes?',
      limit: 2,
      number: true,
    ),
    AdoptionQuestion(
      'otras_mascotas',
      'Especies y edades',
      limit: 600,
      help: 'No incluyas datos de otras personas.',
    ),
    AdoptionQuestion(
      'esterilizacion',
      '¿Están esterilizadas?',
      options: {
        'si': 'Todas',
        'no': 'Ninguna',
        'parcial': 'Algunas',
        'no_se': 'No lo sé',
      },
    ),
    AdoptionQuestion(
      'experiencia_previa',
      '¿Has tenido mascotas antes?',
      options: yesNo,
    ),
    AdoptionQuestion('experiencia', '¿Qué ocurrió con ellas?', limit: 1000),
    AdoptionQuestion(
      'motivo',
      '¿Por qué quieres adoptar?',
      limit: 2000,
      minimum: 10,
    ),
  ],
];

/// Shared readable summary for the draft and the applicant's saved receipt.
class EvaluationSummary extends StatelessWidget {
  const EvaluationSummary({super.key, required this.answers, this.onEdit});
  final Map<String, dynamic> answers;
  final ValueChanged<int>? onEdit;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      for (var step = 0; step < evaluationQuestions.length; step++)
        Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: EvaluationPanel(
            step: step,
            title: evaluationTitles[step],
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                for (final question in evaluationQuestions[step])
                  if (answers.containsKey(question.id))
                    Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            question.label,
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                          const SizedBox(height: 4),
                          ReadableText(
                            question.options?[answers[question.id]] ??
                                '${answers[question.id]}',
                            style: const TextStyle(fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),
                if (onEdit != null)
                  Align(
                    alignment: AlignmentDirectional.centerEnd,
                    child: TextButton(
                      onPressed: () => onEdit!(step),
                      child: const Text('Editar'),
                    ),
                  ),
              ],
            ),
          ),
        ),
    ],
  );
}

class AdoptionQuestionnaireScreen extends StatelessWidget {
  const AdoptionQuestionnaireScreen({
    super.key,
    required this.pet,
    required this.api,
  });
  final Pet pet;
  final AdoptionApi api;
  @override
  Widget build(BuildContext context) => SessionActionGate(
    session: api.session,
    title: 'Solicitud de adopción',
    message: 'Inicia sesión para completar tu solicitud.',
    form: (identity) => _Questionnaire(key: identity, pet: pet, api: api),
  );
}

class _Questionnaire extends StatefulWidget {
  const _Questionnaire({super.key, required this.pet, required this.api});
  final Pet pet;
  final AdoptionApi api;
  @override
  State<_Questionnaire> createState() => _QuestionnaireState();
}

class _QuestionnaireState extends State<_Questionnaire> {
  final _form = GlobalKey<FormState>();
  final _scroll = ScrollController();
  final _values = <String, Object?>{};
  final _fields = <String, TextEditingController>{};
  int _step = 0;
  bool _sending = false,
      _uncertain = false,
      _leaving = false,
      _dirty = false,
      _confirming = false;
  bool _correct = false, _consent = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    final account = widget.api.session.account!;
    final initial = {
      'nombre': account.name,
      'telefono': account.phone,
      'email': account.email,
    };
    for (final question in evaluationQuestions.expand((group) => group)) {
      if (question.options == null) {
        final controller = TextEditingController(
          text: initial[question.id] ?? '',
        );
        controller.addListener(() {
          _dirty = true;
        });
        _fields[question.id] = controller;
      }
    }
  }

  @override
  void dispose() {
    for (final field in _fields.values) {
      field.dispose();
    }
    _scroll.dispose();
    super.dispose();
  }

  Map<String, dynamic> get _answers {
    final answers = <String, dynamic>{..._values};
    for (final question in evaluationQuestions.expand((group) => group)) {
      if (!question.visible(_values)) {
        answers.remove(question.id);
        continue;
      }
      if (question.options == null) {
        final text = _fields[question.id]!.text.trim();
        answers[question.id] = question.number ? int.tryParse(text) : text;
      }
    }
    return answers;
  }

  void _move(int step) {
    FocusScope.of(context).unfocus();
    setState(() {
      _step = step;
      _error = null;
      if (step < 4) {
        _correct = false;
        _consent = false;
      }
    });
    if (_scroll.hasClients) _scroll.jumpTo(0);
  }

  void _next() {
    if (_sending || _uncertain || !validateLpnForm(_form)) return;
    _move(_step + 1);
  }

  Future<void> _leave() async {
    if (_sending || _leaving || _confirming) return;
    if (_uncertain) {
      await _finish(true);
      return;
    }
    if (_dirty) {
      _confirming = true;
      final discard = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('¿Descartar la solicitud?'),
          content: const Text(
            'Tus respuestas aún no se han enviado. Si sales, se perderá este borrador.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Seguir completando'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Descartar'),
            ),
          ],
        ),
      );
      _confirming = false;
      if (discard != true || !mounted) return;
    }
    await _finish(false);
  }

  Future<void> _finish(bool sent) async {
    if (!mounted) return;
    setState(() => _leaving = true);
    await WidgetsBinding.instance.endOfFrame;
    if (mounted) Navigator.of(context).pop(sent);
  }

  Future<void> _send() async {
    if (_sending || _uncertain || !_correct || !_consent) return;
    setState(() {
      _sending = true;
      _error = null;
    });
    try {
      final id = await widget.api.requestEvaluation(widget.pet.id, {
        ..._answers,
        'datos_correctos': true,
        'autoriza_evaluacion': true,
        'version': evaluationVersion,
      });
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Solicitud #$id enviada.')));
      await _finish(true);
    } on Exception catch (error) {
      if (!mounted) return;
      setState(() {
        _uncertain =
            error is! ApiException ||
            error.status == null ||
            error.status! >= 500;
        _error = _uncertain
            ? 'No pudimos confirmar el envío. Revisa Mis solicitudes antes de volver a enviar; tu solicitud podría haberse guardado.'
            : messageFor(
                error,
                'Revisa las respuestas. No pudimos enviar la solicitud.',
              );
      });
      await showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          scrollable: true,
          title: Text(_uncertain ? 'Verifica el envío' : 'Revisa la solicitud'),
          content: Text(_error!),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cerrar'),
            ),
          ],
        ),
      );
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  void _answer(AdoptionQuestion question, Object? value) => setState(() {
    _values[question.id] = value;
    _dirty = true;
    for (final item in evaluationQuestions.expand((group) => group)) {
      if (!item.visible(_values)) {
        _values.remove(item.id);
        _fields[item.id]?.clear();
      }
    }
  });

  Widget _field(AdoptionQuestion question) {
    final options = question.options;
    Widget input;
    if (options != null &&
        options.values.every((label) => label.length <= 15)) {
      input = FormField<Object>(
        key: ValueKey('evaluation-${question.id}'),
        initialValue: _values[question.id],
        autovalidateMode: AutovalidateMode.onUserInteraction,
        validator: (value) => value == null ? 'Selecciona una opción.' : null,
        builder: (field) => Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Wrap(
              spacing: 6,
              runSpacing: 4,
              children: [
                for (final entry in options.entries)
                  Semantics(
                    selected: field.value == entry.key,
                    child: OutlinedButton.icon(
                      key: ValueKey(
                        'evaluation-option-${question.id}-${entry.key}',
                      ),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 6,
                        ),
                        textStyle: const TextStyle(
                          fontFamily: 'Inter',
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                        backgroundColor: field.value == entry.key
                            ? evaluationTints[_step]
                            : LpnColors.paper,
                        foregroundColor: LpnColors.ink,
                        side: BorderSide(
                          color: field.value == entry.key
                              ? LpnColors.sage
                              : LpnColors.controlEdge,
                          width: field.value == entry.key ? 1.5 : 1,
                        ),
                      ),
                      onPressed: _sending || _uncertain
                          ? null
                          : () {
                              field.didChange(entry.key);
                              _answer(question, entry.key);
                            },
                      icon: Icon(
                        field.value == entry.key
                            ? Icons.check_circle_outline
                            : question.id == 'vivienda'
                            ? switch (entry.key) {
                                'casa' => Icons.cottage_outlined,
                                'apartamento' => Icons.apartment_outlined,
                                _ => Icons.home_work_outlined,
                              }
                            : Icons.radio_button_unchecked,
                        size: 14,
                      ),
                      label: Text(entry.value),
                    ),
                  ),
              ],
            ),
            if (field.hasError)
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text(
                  field.errorText!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ),
          ],
        ),
      );
    } else if (options != null) {
      input = DropdownButtonFormField<Object>(
        key: ValueKey('evaluation-${question.id}'),
        initialValue: _values[question.id],
        autovalidateMode: AutovalidateMode.onUserInteraction,
        isExpanded: true,
        isDense: true,
        itemHeight: null,
        selectedItemBuilder: (context) => [
          for (final label in options.values)
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: Text(label, maxLines: 1, overflow: TextOverflow.ellipsis),
            ),
        ],
        decoration: const InputDecoration(
          hintText: 'Selecciona una opción',
          constraints: BoxConstraints(minHeight: 48),
          contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        ),
        items: [
          for (final entry in options.entries)
            DropdownMenuItem(
              value: entry.key,
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Text(entry.value),
              ),
            ),
        ],
        validator: (value) => value == null ? 'Selecciona una opción.' : null,
        onChanged: _sending || _uncertain
            ? null
            : (value) => _answer(question, value),
      );
    } else {
      input = TextFormField(
        key: ValueKey('evaluation-${question.id}'),
        controller: _fields[question.id],
        autovalidateMode: AutovalidateMode.onUserInteraction,
        enabled: !_sending && !_uncertain,
        maxLength: question.limit,
        enableIMEPersonalizedLearning: false,
        autocorrect: !const {
          'documento',
          'email',
          'telefono',
        }.contains(question.id),
        minLines: question.limit >= 600 ? 3 : 1,
        maxLines: question.limit >= 600 ? 5 : 1,
        keyboardType: question.number
            ? TextInputType.number
            : question.email
            ? TextInputType.emailAddress
            : TextInputType.text,
        textCapitalization: question.email || question.number
            ? TextCapitalization.none
            : TextCapitalization.sentences,
        decoration: InputDecoration(
          counterText: '',
          helperText: question.help,
          helperMaxLines: 4,
        ),
        validator: (value) {
          final text = (value ?? '').trim();
          if (text.length < question.minimum) {
            return question.minimum > 1
                ? 'Escribe al menos ${question.minimum} caracteres.'
                : 'Completa este dato.';
          }
          if (question.number &&
              ((int.tryParse(text) ?? 0) < 1 ||
                  (int.tryParse(text) ?? 51) > 50)) {
            return 'Indica un número entre 1 y 50.';
          }
          if (question.email &&
              !RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(text)) {
            return 'Revisa el correo electrónico.';
          }
          return null;
        },
      );
    }
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: LpnFieldLabel(label: question.label, child: input),
    );
  }

  @override
  Widget build(BuildContext context) => PopScope(
    canPop: _leaving,
    onPopInvokedWithResult: (didPop, _) {
      if (didPop || _sending) return;
      if (_step > 0 && !_uncertain) {
        _move(_step - 1);
      } else {
        _leave();
      }
    },
    child: Scaffold(
      appBar: lpnAppBar(
        context,
        'Adoptar a ${widget.pet.name}',
        leading: BackButton(
          onPressed: _sending
              ? null
              : () {
                  if (_step > 0 && !_uncertain) {
                    _move(_step - 1);
                  } else {
                    _leave();
                  }
                },
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: Form(
              key: _form,
              child: LpnFormScrollView(
                controller: _scroll,
                padding: EdgeInsets.symmetric(
                  vertical: 16,
                  horizontal: ((MediaQuery.sizeOf(context).width - 640) / 2)
                      .clamp(16.0, double.infinity),
                ),
                children: [
                  EvaluationProgress(
                    step: _step,
                    title: evaluationTitles[_step],
                  ),
                  const SizedBox(height: 16),
                  if (_step < 4)
                    EvaluationPanel(
                      step: _step,
                      title: evaluationTitles[_step],
                      description: _step == 0
                          ? widget.api.session.account!.demo
                                ? 'Usa únicamente datos ficticios. Esta simulación no envía solicitudes a organizaciones reales.'
                                : 'Se compartirán solo con la organización que evalúa esta adopción. No adjuntes documentos aquí.'
                          : null,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          for (final question in evaluationQuestions[_step])
                            if (question.visible(_values)) _field(question),
                        ],
                      ),
                    )
                  else ...[
                    Text(
                      'Revisa tu solicitud',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Revisa tus respuestas y confirma al final. La organización decidirá la adopción.',
                    ),
                    const SizedBox(height: 20),
                    EvaluationSummary(
                      answers: _answers,
                      onEdit: _sending || _uncertain ? null : _move,
                    ),
                    const FormCard(
                      title: 'Uso de tus respuestas',
                      child: Text(evaluationNotice),
                    ),
                    const SizedBox(height: 16),
                    CheckboxListTile(
                      key: const Key('evaluation-correct'),
                      value: _correct,
                      controlAffinity: ListTileControlAffinity.leading,
                      contentPadding: EdgeInsets.zero,
                      title: const Text(
                        'Confirmo que los datos son correctos.',
                      ),
                      onChanged: _sending || _uncertain
                          ? null
                          : (value) =>
                                setState(() => _correct = value ?? false),
                    ),
                    CheckboxListTile(
                      key: const Key('evaluation-consent'),
                      value: _consent,
                      controlAffinity: ListTileControlAffinity.leading,
                      contentPadding: EdgeInsets.zero,
                      title: const Text(
                        'Autorizo evaluar esta solicitud con mis respuestas.',
                      ),
                      onChanged: _sending || _uncertain
                          ? null
                          : (value) =>
                                setState(() => _consent = value ?? false),
                    ),
                  ],
                ],
              ),
            ),
          ),
          LpnActionBar(
            child: Wrap(
              alignment: WrapAlignment.end,
              spacing: 12,
              runSpacing: 8,
              children: [
                TextButton(
                  onPressed: _sending ? null : _leave,
                  child: const Text('Cancelar'),
                ),
                if (_step > 0 && !_uncertain)
                  TextButton(
                    onPressed: _sending ? null : () => _move(_step - 1),
                    child: const Text('Regresar'),
                  ),
                FilledButton(
                  key: const Key('evaluation-next'),
                  onPressed: _sending
                      ? null
                      : _uncertain
                      ? () => _finish(true)
                      : _step < 4
                      ? _next
                      : _correct && _consent
                      ? _send
                      : null,
                  child: Text(
                    _sending
                        ? 'Enviando…'
                        : _uncertain
                        ? 'Ver mis solicitudes'
                        : _step < 4
                        ? 'Continuar'
                        : 'Enviar solicitud',
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}
