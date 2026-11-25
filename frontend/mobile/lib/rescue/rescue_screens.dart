import '../design/readable_text.dart';
import 'report_photo.dart';
import 'sponsorship_screen.dart';

import '../design/photo_attachment.dart';
import '../core/api_client.dart' show ApiException;
import '../design/lpn_app_bar.dart';
import '../design/lpn_theme.dart';
import '../design/rescue_hero.dart';
import '../design/rescue_cards.dart';
import '../design/form_surfaces.dart';

import 'package:flutter_svg/flutter_svg.dart';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart' show ImageSource;

import '../adoption/adoption_screens.dart' show StatusPanel, messageFor;
import '../auth/account_screen.dart';
import 'rescue_api.dart';
import 'public_reports_controller.dart';
import 'anonymous_report_screen.dart';

Future<ReportReceipt?> openReportFlow(
  BuildContext context,
  RescueApi api,
) async {
  final receipt = await Navigator.of(context).push<ReportReceipt>(
    MaterialPageRoute(builder: (_) => ReportFormScreen(api: api)),
  );
  if (receipt == null || !context.mounted) return receipt;
  await Navigator.of(context).push(
    MaterialPageRoute(
      builder: (_) => ReportReceiptScreen(receipt: receipt, api: api),
    ),
  );
  return receipt;
}

class RescueScreen extends StatefulWidget {
  const RescueScreen({super.key, required this.api, this.onAdopt});
  final RescueApi api;
  final VoidCallback? onAdopt;
  @override
  State<RescueScreen> createState() => _RescueScreenState();
}

class _RescueScreenState extends State<RescueScreen> {
  late final _feed = PublicReportsController(widget.api)..reload();
  Future<void> _reload() => _feed.reload();

  @override
  void dispose() {
    _feed.dispose();
    super.dispose();
  }

  Future<void> _create() async {
    final receipt = await openReportFlow(context, widget.api);
    if (mounted && receipt != null) await _reload();
  }

  Future<void> _manageAnonymous() async {
    await Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => AnonymousReportScreen(api: widget.api)),
    );
    if (mounted) await _reload();
  }

  Future<void> _mine() async {
    if (!widget.api.session.signedIn &&
        !await openLogin(context, widget.api.session)) {
      return;
    }
    if (!mounted) return;
    await Navigator.of(
      context,
    ).push(MaterialPageRoute(builder: (_) => MyReportsScreen(api: widget.api)));
  }

  @override
  Widget build(BuildContext context) => RefreshIndicator(
    onRefresh: _reload,
    child: AnimatedBuilder(
      animation: _feed,
      builder: (context, _) {
        final reports = _feed.reports
            .where(
              (report) => !const {
                'cerrado',
                'rechazado',
                'resuelto',
                'cancelado',
              }.contains(_searchText(report.status)),
            )
            .toList();
        return ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.only(bottom: 24),
          children: [
            RescueHero(onSearchChanged: _feed.search),
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 8),
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _RescueAction(
                    icon: Icons.add,
                    label: 'Reportar un animal',
                    onTap: _create,
                  ),
                  _RescueAction(
                    icon: Icons.route_outlined,
                    label: 'Mis reportes',
                    onTap: _mine,
                  ),
                  _RescueAction(
                    icon: Icons.key_outlined,
                    label: 'Gestionar reporte anónimo',
                    onTap: _manageAnonymous,
                  ),
                  _RescueAction(
                    icon: Icons.history,
                    label: 'Historias de rescate',
                    onTap: () => Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) => CommunityReportsScreen(feed: _feed),
                      ),
                    ),
                  ),
                  _RescueAction(
                    icon: Icons.refresh,
                    label: 'Actualizar',
                    onTap: _reload,
                  ),
                ],
              ),
            ),
            const Padding(
              padding: EdgeInsets.fromLTRB(20, 16, 20, 4),
              child: Text(
                'Animales que necesitan ayuda',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
              ),
            ),
            if (_feed.loading)
              const Center(
                child: CircularProgressIndicator(
                  semanticsLabel: 'Cargando reportes',
                ),
              )
            else if (_feed.error != null)
              StatusPanel(
                message: messageFor(
                  _feed.error,
                  'No pudimos cargar los reportes.',
                ),
                action: _reload,
                actionLabel: 'Reintentar',
              )
            else if (reports.isEmpty)
              Padding(
                padding: const EdgeInsets.all(20),
                child: Text(
                  _feed.nextCursor != null
                      ? 'No hay reportes que necesiten ayuda en esta página. Puedes cargar más reportes.'
                      : _feed.query.isEmpty
                      ? 'Todavía no hay reportes publicados que necesiten ayuda.'
                      : 'No hay reportes que coincidan con la búsqueda.',
                ),
              )
            else
              RescueCards(
                reports: reports,
                origin: widget.api.api.base,
                onOpen: (report) => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) =>
                        ReportDetailScreen(report: report, api: widget.api),
                  ),
                ),
              ),
            PublicReportsPageControls(feed: _feed),
            if (widget.onAdopt != null)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: TextButton.icon(
                  onPressed: widget.onAdopt,
                  icon: const Icon(Icons.favorite_border),
                  label: const Text('Adopta ya'),
                ),
              ),
          ],
        );
      },
    ),
  );
}

class CommunityReportsScreen extends StatelessWidget {
  const CommunityReportsScreen({super.key, required this.feed});
  final PublicReportsController feed;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Historias de rescate'),
    body: AnimatedBuilder(
      animation: feed,
      builder: (context, _) => RefreshIndicator(
        onRefresh: feed.reload,
        child: ListView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(24),
          children: [
            const Text(
              'Reportes publicados por la comunidad. Abre uno para consultar la información y los avances disponibles.',
            ),
            if (feed.query.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text('Resultados de la búsqueda: ${feed.query}'),
            ],
            const SizedBox(height: 16),
            if (feed.loading)
              const Center(
                child: CircularProgressIndicator(
                  semanticsLabel: 'Cargando reportes',
                ),
              )
            else if (feed.error != null)
              StatusPanel(
                message: messageFor(
                  feed.error,
                  'No pudimos cargar los reportes.',
                ),
                action: feed.reload,
                actionLabel: 'Reintentar',
              )
            else if (feed.reports.isEmpty)
              const Text('No hay reportes publicados para esta consulta.')
            else
              for (final report in feed.reports)
                ReportTile(report: report, api: feed.api),
            PublicReportsPageControls(feed: feed),
          ],
        ),
      ),
    ),
  );
}

class PublicReportsPageControls extends StatelessWidget {
  const PublicReportsPageControls({super.key, required this.feed});
  final PublicReportsController feed;
  @override
  Widget build(BuildContext context) {
    if (feed.loading) return const SizedBox.shrink();
    if (feed.pageError != null) {
      return Padding(
        padding: const EdgeInsets.all(16),
        child: StatusPanel(
          message: messageFor(
            feed.pageError,
            'No pudimos cargar más reportes. Lo anterior sigue disponible.',
          ),
          action: feed.loadMore,
          actionLabel: 'Reintentar cargar más',
        ),
      );
    }
    if (feed.nextCursor == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: OutlinedButton.icon(
        onPressed: feed.loadingMore ? null : feed.loadMore,
        icon: const Icon(Icons.expand_more),
        label: Text(feed.loadingMore ? 'Cargando más…' : 'Cargar más reportes'),
      ),
    );
  }
}

String _searchText(String value) {
  var result = value.toLowerCase().trim();
  for (final entry in const {
    'á': 'a',
    'é': 'e',
    'í': 'i',
    'ó': 'o',
    'ú': 'u',
    'ü': 'u',
  }.entries) {
    result = result.replaceAll(entry.key, entry.value);
  }
  return result;
}

class ReportTile extends StatelessWidget {
  const ReportTile({super.key, required this.report, this.api});
  final AnimalReport report;
  final RescueApi? api;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 6),
    child: ReportDecisionCard(
      report: report,
      origin: api?.api.base,
      compact: true,
      onOpen: () => Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => ReportDetailScreen(report: report, api: api),
        ),
      ),
    ),
  );
}

class ReportDetailScreen extends StatelessWidget {
  const ReportDetailScreen({super.key, required this.report, this.api});
  final AnimalReport report;
  final RescueApi? api;
  IconData get _statusIcon => switch (report.status.toLowerCase()) {
    'pendiente' => Icons.schedule_outlined,
    'cerrado' || 'resuelto' => Icons.task_alt,
    'aceptado' || 'en atención' => Icons.volunteer_activism_outlined,
    _ => Icons.info_outline,
  };
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Reporte #${report.id}'),
    bottomNavigationBar: api != null && report.rescueCase != null
        ? LpnActionBar(
            avoidKeyboard: true,
            child: Align(
              heightFactor: 1,
              alignment: AlignmentDirectional.centerEnd,
              child: FilledButton.icon(
                onPressed: () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => SponsorshipScreen(
                      session: api!.session,
                      reportId: report.id,
                    ),
                  ),
                ),
                icon: const Icon(Icons.volunteer_activism_outlined),
                label: const Text('Apadrinar este caso'),
              ),
            ),
          )
        : null,
    body: ListView(
      padding: EdgeInsets.symmetric(
        vertical: 16,
        horizontal: ((MediaQuery.sizeOf(context).width - 640) / 2).clamp(
          16.0,
          double.infinity,
        ),
      ),
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(20),
          child: ReportPhoto(
            value: report.photo,
            reportId: report.id,
            origin: api?.api.base,
            height: 180,
          ),
        ),
        const SizedBox(height: 12),
        LpnFormSection(
          title: report.type,
          icon: Icons.pets_outlined,
          tone: 3,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(_statusIcon, size: 20, color: LpnColors.sage),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    report.status,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(
                  Icons.location_on_outlined,
                  size: 20,
                  color: LpnColors.sage,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    report.city.isEmpty ? 'Ciudad no publicada' : report.city,
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 16),
        LpnFormSection(
          title: 'Qué ocurrió',
          icon: Icons.notes_outlined,
          tone: 2,
          children: [
            ReadableText(
              report.description,
              style: const TextStyle(height: 1.5),
            ),
          ],
        ),
        const SizedBox(height: 16),
        LpnFormSection(
          title: 'Seguimiento del rescate',
          icon: Icons.route_outlined,
          tone: 1,
          children: [
            if (report.rescueCase case final rescueCase?) ...[
              Text(
                'Aceptado por ${rescueCase.organization}',
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 8),
              Text('Caso #${rescueCase.id}'),
              const SizedBox(height: 4),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.info_outline, size: 18),
                  const SizedBox(width: 8),
                  Expanded(child: Text(rescueCase.status)),
                ],
              ),
            ] else
              const Text(
                'Aún sin organización asignada. Podrás apadrinar cuando una fundación acepte el caso.',
              ),
          ],
        ),
      ],
    ),
  );
}

class MyReportsScreen extends StatelessWidget {
  const MyReportsScreen({super.key, required this.api});
  final RescueApi api;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Mis reportes'),
    body: ListenableBuilder(
      listenable: api.session,
      builder: (context, _) {
        if (!api.session.signedIn) {
          return StatusPanel(
            message: 'Inicia sesión para consultar tus reportes.',
            action: () => openLogin(context, api.session),
            actionLabel: 'Iniciar sesión',
          );
        }
        return _MyReportList(
          key: ValueKey(api.session.account!.email),
          api: api,
        );
      },
    ),
  );
}

class _MyReportList extends StatefulWidget {
  const _MyReportList({super.key, required this.api});
  final RescueApi api;
  @override
  State<_MyReportList> createState() => _MyReportListState();
}

class _MyReportListState extends State<_MyReportList> {
  late Future<List<AnimalReport>> _reports = widget.api.mine();
  Future<void> _reload() async {
    final next = widget.api.mine();
    setState(() {
      _reports = next;
    });
    try {
      await next;
    } on Exception {
      /* The list offers retry. */
    }
  }

  @override
  Widget build(BuildContext context) => RefreshIndicator(
    onRefresh: _reload,
    child: FutureBuilder<List<AnimalReport>>(
      future: _reports,
      builder: (context, snapshot) => ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(20),
        children: [
          const Text(
            'Aquí aparecen únicamente los reportes enviados con tu cuenta.',
          ),
          Align(
            alignment: Alignment.centerRight,
            child: IconButton(
              tooltip: 'Actualizar reportes',
              onPressed: _reload,
              icon: const Icon(Icons.refresh),
            ),
          ),
          if (snapshot.connectionState != ConnectionState.done)
            const Center(child: CircularProgressIndicator())
          else if (snapshot.hasError)
            StatusPanel(
              message: messageFor(
                snapshot.error,
                'No pudimos consultar tus reportes.',
              ),
              action: _reload,
              actionLabel: 'Reintentar',
            )
          else if (snapshot.data!.isEmpty)
            const StatusPanel(
              message: 'Todavía no has enviado reportes con esta cuenta.',
            )
          else
            for (final report in snapshot.data!)
              ReportTile(report: report, api: widget.api),
        ],
      ),
    ),
  );
}

class ReportFormScreen extends StatefulWidget {
  const ReportFormScreen({super.key, required this.api, this.choosePhoto});
  final RescueApi api;
  final Future<Uint8List?> Function(ImageSource)? choosePhoto;
  @override
  State<ReportFormScreen> createState() => _ReportFormScreenState();
}

class _ReportFormScreenState extends State<ReportFormScreen> {
  final _form = GlobalKey<FormState>();
  final _wizardScroll = ScrollController();
  final _cityInput = TextEditingController();
  final _cityFocus = FocusNode();
  int _step = 0;
  Uint8List? _photo;
  bool _pickingPhoto = false;
  bool _photoPublic = false, _identityChanged = false;
  late final int _identityRevision;
  late final String? _identity;
  bool get _sameIdentity =>
      mounted &&
      !_identityChanged &&
      widget.api.session.identityRevision == _identityRevision &&
      widget.api.session.account?.email == _identity;
  void _sessionChanged() {
    if (!_sameIdentity && mounted && !_identityChanged) {
      setState(() {
        _identityChanged = true;
        _photo = null;
        _photoPublic = false;
      });
      for (final controller in [
        _neighborhood,
        _address,
        _description,
        _directions,
        _contact,
        _cityInput,
      ]) {
        controller.clear();
      }
      _city = null;
      _type = null;
      ++_citySearch;
    }
  }

  bool _leaving = false, _confirming = false, _uncertain = false;
  bool get _dirty =>
      _photo != null ||
      _type != null ||
      _description.text.isNotEmpty ||
      _cityInput.text.isNotEmpty ||
      _neighborhood.text.isNotEmpty ||
      _address.text.isNotEmpty ||
      _contact.text.isNotEmpty ||
      _directions.text.isNotEmpty;
  void _changeStep(int step) {
    if (_sending || _pickingPhoto || !_sameIdentity) return;
    ++_citySearch;
    FocusScope.of(context).unfocus();
    setState(() {
      _step = step;
      _error = null;
    });
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted && _wizardScroll.hasClients) _wizardScroll.jumpTo(0);
    });
  }

  void _next() {
    if (validateLpnForm(_form)) _changeStep(_step + 1);
  }

  Future<void> _leave({bool exit = false}) async {
    if (_confirming || ((_sending || _pickingPhoto) && !_identityChanged)) {
      return;
    }
    if (!exit && _step > 0 && !_uncertain && !_identityChanged) {
      _changeStep(_step - 1);
      return;
    }
    if (_dirty) {
      _confirming = true;
      final discard = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('¿Descartar este reporte?'),
          content: Text(
            _uncertain
                ? 'El envío podría haberse guardado. Salir no lo cancela; comprueba el reporte antes de repetirlo.'
                : 'Todavía no se ha enviado.',
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
      if (discard != true || !mounted) return;
    }
    if (!mounted) return;
    setState(() => _leaving = true);
    await WidgetsBinding.instance.endOfFrame;
    if (mounted) Navigator.pop(context);
  }

  final _neighborhood = TextEditingController();
  final _address = TextEditingController();
  final _description = TextEditingController();
  final _directions = TextEditingController();
  final _contact = TextEditingController();
  late Future<ReportOptions> _options = widget.api.options();
  ReportChoice? _type;
  ReportCity? _city;
  String? _error;
  String? _cityError;
  bool _sending = false;
  int _citySearch = 0;

  @override
  void initState() {
    super.initState();
    _identityRevision = widget.api.session.identityRevision;
    _identity = widget.api.session.account?.email;
    widget.api.session.addListener(_sessionChanged);
    for (final field in [
      _neighborhood,
      _address,
      _description,
      _directions,
      _contact,
      _cityInput,
    ]) {
      field.addListener(_draftChanged);
    }
  }

  void _draftChanged() {
    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    widget.api.session.removeListener(_sessionChanged);
    for (final controller in [
      _neighborhood,
      _address,
      _description,
      _directions,
      _contact,
    ]) {
      controller.removeListener(_draftChanged);
      controller.dispose();
    }
    _wizardScroll.dispose();
    _cityInput.removeListener(_draftChanged);
    _cityInput.dispose();
    _cityFocus.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_sameIdentity ||
        _sending ||
        _pickingPhoto ||
        _uncertain ||
        (_photo != null && !_photoPublic) ||
        !validateLpnForm(_form)) {
      return;
    }
    if (_type == null || _description.text.trim().isEmpty) {
      _changeStep(0);
      return;
    }
    if (_city == null ||
        _cityInput.text != _city!.label ||
        _neighborhood.text.trim().isEmpty ||
        _address.text.trim().isEmpty) {
      _changeStep(1);
      return;
    }
    FocusScope.of(context).unfocus();
    setState(() {
      _sending = true;
      _error = null;
    });
    try {
      final receipt = await widget.api.create(
        type: _type!.id,
        city: _city!.id,
        neighborhood: _neighborhood.text,
        address: _address.text,
        description: _description.text,
        directions: _directions.text,
        contact: _contact.text,
        photo: _photo,
        photoPublic: _photoPublic,
      );
      if (mounted && _sameIdentity) {
        setState(() => _leaving = true);
        await WidgetsBinding.instance.endOfFrame;
        if (mounted && _sameIdentity) Navigator.of(context).pop(receipt);
      }
    } on Exception catch (error) {
      if (mounted && _sameIdentity) {
        setState(() {
          _uncertain =
              error is! ApiException ||
              error.status == null ||
              error.status! >= 500;
          _error = _uncertain
              ? _identity == null
                    ? 'El reporte podría haberse guardado, pero no recibimos la confirmación ni la clave privada. No repetiremos el envío. Comprueba los reportes públicos o contacta al equipo antes de volver a enviarlo.'
                    : 'El reporte podría haberse guardado. Revisa Mis reportes antes de repetirlo. Conservamos tu borrador y no reenviamos automáticamente.'
              : messageFor(
                  error,
                  'Revisa los datos. No pudimos enviar el reporte.',
                );
        });
        await showDialog<void>(
          context: context,
          builder: (context) => AlertDialog(
            scrollable: true,
            title: Text(_uncertain ? 'Verifica el envío' : 'Revisa el reporte'),
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
      if (mounted) setState(() => _sending = false);
    }
  }

  Widget _field(
    String key,
    String label,
    TextEditingController controller,
    int maxLength, {
    bool required = true,
    int lines = 1,
  }) => Padding(
    padding: const EdgeInsets.only(top: 16),
    child: LpnFieldLabel(
      label: label,
      child: TextFormField(
        key: Key(key),
        controller: controller,
        enabled: !_sending && !_uncertain,
        style: const TextStyle(fontSize: 16),
        maxLength: maxLength,
        minLines: lines,
        maxLines: lines + (lines > 1 ? 2 : 0),
        decoration: const InputDecoration(counterText: ''),
        validator: (value) => required && (value ?? '').trim().isEmpty
            ? 'Completa este dato.'
            : null,
      ),
    ),
  );

  @override
  Widget build(BuildContext context) => _identityChanged
      ? Scaffold(
          appBar: lpnAppBar(context, 'Reportar un animal'),
          body: SingleChildScrollView(
            child: StatusPanel(
              message: 'La sesión cambió. Eliminamos este borrador para no enviarlo con otra cuenta.',
              action: () => _leave(exit: true),
              actionLabel: 'Salir del formulario',
            ),
          ),
        )
      : PopScope(
          canPop:
              _leaving || !_sending && !_pickingPhoto && !_dirty && _step == 0,
          onPopInvokedWithResult: (didPop, _) {
            if (!didPop) _leave();
          },
          child: Scaffold(
            appBar: lpnAppBar(
              context,
              'Reportar un animal',
              leading: BackButton(
                onPressed: _sending || _pickingPhoto ? null : () => _leave(),
              ),
            ),
            body: FutureBuilder<ReportOptions>(
              future: _options,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError || snapshot.data!.types.isEmpty) {
                  return StatusPanel(
                    message: snapshot.hasError
                        ? messageFor(
                            snapshot.error,
                            'No pudimos cargar las opciones.',
                          )
                        : 'No hay tipos de reporte disponibles. Contacta al equipo.',
                    action: () => setState(() {
                      _options = widget.api.options();
                    }),
                    actionLabel: 'Reintentar',
                  );
                }
                return Form(
                  key: _form,
                  child: Column(
                    children: [
                      Expanded(
                        child: LpnFormScrollView(
                          controller: _wizardScroll,
                          padding: EdgeInsets.symmetric(
                            vertical: 16,
                            horizontal:
                                ((MediaQuery.sizeOf(context).width - 640) / 2)
                                    .clamp(16.0, double.infinity),
                          ),
                          children: [
                            LpnStepProgress(
                              step: _step,
                              titles: const [
                                'Situación',
                                'Ubicación',
                                'Revisión y contacto',
                              ],
                              icons: const [
                                Icons.pets_outlined,
                                Icons.location_on_outlined,
                                Icons.fact_check_outlined,
                              ],
                            ),
                            const SizedBox(height: 16),
                            if (_step == 0)
                              LpnFormSection(
                                title: 'Situación',
                                icon: Icons.pets_outlined,
                                description: 'Selecciona el tipo de reporte y describe lo que observas.',
                                children: [
                                  FormField<ReportChoice>(
                                    key: const Key('report-type'),
                                    initialValue: _type,
                                    validator: (value) => value == null
                                        ? 'Selecciona la situación.'
                                        : null,
                                    builder: (field) => Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.stretch,
                                      children: [
                                        const Text(
                                          'Tipo de reporte',
                                          style: TextStyle(
                                            fontSize: 14,
                                            fontWeight: FontWeight.w600,
                                          ),
                                        ),
                                        const SizedBox(height: 8),
                                        Wrap(
                                          spacing: 8,
                                          runSpacing: 4,
                                          children: [
                                            for (final type
                                                in snapshot.data!.types)
                                              ChoiceChip(
                                                label: Text(
                                                  type.name,
                                                  style: const TextStyle(
                                                    fontSize: 14,
                                                  ),
                                                ),
                                                selected: _type?.id == type.id,
                                                showCheckmark: true,
                                                onSelected:
                                                    _sending || _uncertain
                                                    ? null
                                                    : (_) {
                                                        setState(
                                                          () => _type = type,
                                                        );
                                                        field.didChange(type);
                                                      },
                                              ),
                                          ],
                                        ),
                                        if (field.errorText != null)
                                          Text(
                                            field.errorText!,
                                            style: TextStyle(
                                              color: Theme.of(context)
                                                  .colorScheme
                                                  .error,
                                            ),
                                          ),
                                      ],
                                    ),
                                  ),
                                  _field(
                                    'report-description',
                                    '¿Qué está pasando con el animal?',
                                    _description,
                                    5000,
                                    lines: 3,
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    _type?.name.toLowerCase().contains(
                                              'perd',
                                            ) ==
                                            true
                                        ? 'Describe al animal y cuándo lo viste por última vez. Evita datos personales.'
                                        : 'Describe lo que observas sin ponerte en riesgo. Evita datos personales.',
                                    style: TextStyle(
                                      fontSize: 14,
                                      height: 1.5,
                                      color: LpnColors.muted,
                                    ),
                                  ),
                                ],
                              ),
                            if (_step == 0) ...[
                              const SizedBox(height: 16),
                              LpnFormSection(
                                title: 'Fotografía del animal',
                                tone: 2,
                                icon: Icons.camera_alt_outlined,
                                children: [
                                  PhotoAttachment(
                                    value: _photo,
                                    choose: widget.choosePhoto,
                                    onBusyChanged: (busy) {
                                      if (mounted) {
                                        setState(() => _pickingPhoto = busy);
                                      }
                                    },
                                    onChanged: (value) {
                                      if (_sameIdentity) {
                                        setState(() {
                                          _photo = value;
                                          _photoPublic = false;
                                        });
                                      }
                                    },
                                    enabled: !_sending && !_uncertain,
                                    public: true,
                                  ),
                                ],
                              ),
                            ],
                            if (_step == 1)
                              LpnFormSection(
                                title: 'Ubicación',
                                tone: 1,
                                icon: Icons.location_on_outlined,
                                description: 'Indica un lugar que permita encontrar al animal.',
                                children: [
                                  Autocomplete<ReportCity>(
                                    textEditingController: _cityInput,
                                    focusNode: _cityFocus,
                                    displayStringForOption: (city) =>
                                        city.label,
                                    optionsBuilder: (value) async {
                                      final search = ++_citySearch;
                                      if (_sending ||
                                          _uncertain ||
                                          value.text.trim().length < 2) {
                                        return const <ReportCity>[];
                                      }
                                      if (_city != null &&
                                          value.text == _city!.label) {
                                        return [_city!];
                                      }
                                      await Future<void>.delayed(
                                        const Duration(milliseconds: 300),
                                      );
                                      if (!mounted || search != _citySearch) {
                                        return const <ReportCity>[];
                                      }
                                      try {
                                        final result = await widget.api.options(
                                          value.text,
                                        );
                                        if (mounted &&
                                            _sameIdentity &&
                                            search == _citySearch &&
                                            _step == 1) {
                                          setState(
                                            () => _cityError =
                                                result.cities.isEmpty
                                                ? 'No hay coincidencias. Revisa el nombre de la ciudad.'
                                                : null,
                                          );
                                        }
                                        if (!_sameIdentity ||
                                            search != _citySearch ||
                                            _step != 1) {
                                          return const <ReportCity>[];
                                        }
                                        return result.cities;
                                      } on Exception {
                                        if (mounted &&
                                            _sameIdentity &&
                                            search == _citySearch &&
                                            _step == 1) {
                                          setState(
                                            () => _cityError = 'No pudimos buscar la ciudad. Intenta de nuevo.',
                                          );
                                        }
                                        return const <ReportCity>[];
                                      }
                                    },
                                    onSelected: (city) => setState(() {
                                      ++_citySearch;
                                      _city = city;
                                      _cityError = null;
                                    }),
                                    fieldViewBuilder:
                                        (
                                          context,
                                          controller,
                                          focusNode,
                                          onSubmitted,
                                        ) => LpnFieldLabel(
                                          label: 'Ciudad',
                                          child: TextFormField(
                                            key: const Key('report-city'),
                                            controller: controller,
                                            focusNode: focusNode,
                                            enabled: !_sending && !_uncertain,
                                            decoration: const InputDecoration(
                                              helperText: 'Escribe 2 letras y selecciona una opción.',
                                              helperMaxLines: 3,
                                              prefixIcon: Icon(
                                                Icons.location_city_outlined,
                                              ),
                                            ),
                                            onChanged: (_) {
                                              Scrollable.ensureVisible(
                                                context,
                                                alignment: .1,
                                              );
                                              if (_city != null) {
                                                setState(() => _city = null);
                                              }
                                            },
                                            validator: (value) =>
                                                _city == null ||
                                                    value != _city!.label
                                                ? 'Selecciona una ciudad de la lista.'
                                                : null,
                                          ),
                                        ),
                                  ),
                                  if (_cityError != null)
                                    Semantics(
                                      liveRegion: true,
                                      child: Text(_cityError!),
                                    ),
                                  _field(
                                    'report-neighborhood',
                                    'Barrio o sector',
                                    _neighborhood,
                                    120,
                                  ),
                                  _field(
                                    'report-address',
                                    'Dirección o lugar de referencia',
                                    _address,
                                    255,
                                  ),
                                  _field(
                                    'report-directions',
                                    'Indicaciones adicionales (opcional)',
                                    _directions,
                                    1000,
                                    required: false,
                                    lines: 2,
                                  ),
                                ],
                              ),
                            if (_step == 2)
                              LpnFormSection(
                                title: 'Revisa tu reporte',
                                tone: 2,
                                icon: Icons.fact_check_outlined,
                                children: [
                                  ListTile(
                                    contentPadding: EdgeInsets.zero,
                                    title: Text(_type?.name ?? ''),
                                    subtitle: const Text('Situación'),
                                    trailing: IconButton(
                                      tooltip: 'Editar situación',
                                      onPressed: () => _changeStep(0),
                                      icon: const Icon(Icons.edit_outlined),
                                    ),
                                  ),
                                  ListTile(
                                    contentPadding: EdgeInsets.zero,
                                    title: Text(_city?.label ?? ''),
                                    subtitle: Text(
                                      '${_neighborhood.text}\n${_address.text}',
                                    ),
                                    trailing: IconButton(
                                      tooltip: 'Editar ubicación',
                                      onPressed: () => _changeStep(1),
                                      icon: const Icon(Icons.edit_outlined),
                                    ),
                                  ),
                                  if (_directions.text.trim().isNotEmpty) ...[
                                    const Divider(),
                                    const Text(
                                      'Indicaciones adicionales',
                                      style: TextStyle(
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                    ReadableText(_directions.text),
                                  ],
                                  if (_photo != null) ...[
                                    const SizedBox(height: 12),
                                    ClipRRect(
                                      borderRadius: BorderRadius.circular(16),
                                      child: Image.memory(
                                        _photo!,
                                        height: 140,
                                        fit: BoxFit.contain,
                                        semanticLabel: 'Foto que se publicará con tu reporte',
                                      ),
                                    ),
                                    CheckboxListTile(
                                      key: const Key('report-photo-consent'),
                                      contentPadding: EdgeInsets.zero,
                                      controlAffinity:
                                          ListTileControlAffinity.leading,
                                      title: const Text(
                                        'Acepto mostrar esta foto con el reporte.',
                                        style: TextStyle(
                                          fontSize: 14,
                                          fontWeight: FontWeight.w500,
                                          height: 1.4,
                                        ),
                                      ),
                                      value: _photoPublic,
                                      onChanged: _sending || _uncertain
                                          ? null
                                          : (value) => setState(
                                              () =>
                                                  _photoPublic = value ?? false,
                                            ),
                                    ),
                                  ],
                                  ExpansionTile(
                                    tilePadding: EdgeInsets.zero,
                                    title: const Text('Ver descripción'),
                                    children: [ReadableText(_description.text)],
                                  ),
                                ],
                              ),
                            if (_step == 2) const SizedBox(height: 16),
                            if (_step == 2)
                              LpnFormSection(
                                title: 'Contacto',
                                tone: 0,
                                icon: Icons.shield_outlined,
                                description: 'Este dato es opcional y no se publica en la descripción.',
                                children: [
                                  _field(
                                    'report-contact',
                                    'Contacto privado (opcional)',
                                    _contact,
                                    150,
                                    required: false,
                                  ),
                                  const SizedBox(height: 12),
                                  Text(
                                    widget.api.session.signedIn
                                        ? 'Podrás seguir el reporte en Mis reportes.'
                                        : 'No necesitas una cuenta. Al enviarlo recibirás una clave privada para gestionarlo.',
                                    style: const TextStyle(
                                      fontSize: 14,
                                      height: 1.5,
                                      color: LpnColors.muted,
                                    ),
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
                              key: const Key('report-cancel'),
                              onPressed: _sending || _pickingPhoto
                                  ? null
                                  : () => _leave(exit: true),
                              child: Text(
                                _uncertain
                                    ? 'Salir del formulario'
                                    : 'Cancelar',
                              ),
                            ),
                            if (_step > 0 && !_uncertain)
                              TextButton(
                                key: const Key('report-previous'),
                                onPressed: _sending || _pickingPhoto
                                    ? null
                                    : () => _changeStep(_step - 1),
                                child: const Text('Anterior'),
                              ),
                            if (_uncertain && _identity != null)
                              OutlinedButton(
                                key: const Key('report-check-own'),
                                onPressed: () => Navigator.of(context).push(
                                  MaterialPageRoute(
                                    builder: (_) => Scaffold(
                                      appBar: lpnAppBar(
                                        context,
                                        'Mis reportes',
                                      ),
                                      body: MyReportsScreen(api: widget.api),
                                    ),
                                  ),
                                ),
                                child: const Text('Ver mis reportes'),
                              ),
                            FilledButton.icon(
                              key: Key(
                                _step == 2 ? 'report-submit' : 'report-next',
                              ),
                              onPressed:
                                  _sending ||
                                      _pickingPhoto ||
                                      _uncertain ||
                                      (_step == 2 &&
                                          _photo != null &&
                                          !_photoPublic)
                                  ? null
                                  : _step == 2
                                  ? _submit
                                  : _next,
                              icon: Icon(
                                _step == 2
                                    ? Icons.send_outlined
                                    : Icons.arrow_forward,
                              ),
                              label: Text(
                                _sending
                                    ? 'Enviando…'
                                    : _step == 2
                                    ? 'Enviar reporte'
                                    : 'Continuar',
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
        );
}

class ReportReceiptScreen extends StatelessWidget {
  const ReportReceiptScreen({
    super.key,
    required this.receipt,
    required this.api,
  });
  final ReportReceipt receipt;
  final RescueApi api;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Reporte recibido'),
    body: ListView(
      padding: const EdgeInsets.all(24),
      children: [
        const SizedBox(height: 48),
        SvgPicture.asset(
          'assets/login-brand.svg',
          width: 92,
          height: 104,
          excludeFromSemantics: true,
        ),
        const SizedBox(height: 16),
        const Text(
          'LITTLE PAWS NET',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 20),
        ),
        const SizedBox(height: 16),
        Text(
          '¡Reporte enviado!',
          style: const TextStyle(fontFamily: 'LPN Script', fontSize: 24),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 12),
        Text(
          'Reporte #${receipt.id}, ${receipt.status}',
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 20),
        const Text(
          'Enviar el reporte no significa que una organización ya haya aceptado el rescate.',
        ),
        if (receipt.privateCode case final code?) ...[
          const SizedBox(height: 20),
          const Text(
            'Guarda tu clave privada',
            style: TextStyle(fontWeight: FontWeight.w700),
          ),
          const Text(
            'Solo se muestra ahora. No la compartas en publicaciones ni capturas: permite gestionar tu reporte anónimo.',
          ),
          const SizedBox(height: 12),
          ReadableText(code),
          OutlinedButton.icon(
            onPressed: () async {
              await Clipboard.setData(ClipboardData(text: code));
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text(
                      'Clave copiada. Guárdala en un lugar privado.',
                    ),
                  ),
                );
              }
            },
            icon: const Icon(Icons.copy_outlined),
            label: const Text('Copiar clave privada'),
          ),
          TextButton.icon(
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => AnonymousReportScreen(
                  api: api,
                  reportId: receipt.id,
                  privateCode: code,
                ),
              ),
            ),
            icon: const Icon(Icons.key_outlined),
            label: const Text('Gestionar este reporte'),
          ),
        ] else ...[
          const SizedBox(height: 20),
          FilledButton(
            onPressed: () => Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (_) => MyReportsScreen(api: api)),
            ),
            child: const Text('Ver mis reportes'),
          ),
        ],
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Volver a rescates'),
        ),
      ],
    ),
  );
}

class _RescueAction extends StatelessWidget {
  const _RescueAction({
    required this.icon,
    required this.label,
    required this.onTap,
  });
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) => SizedBox(
    width: MediaQuery.textScalerOf(context).scale(12) > 18
        ? 112
        : ((MediaQuery.sizeOf(context).width - 72) / 5).clamp(48, 72),
    child: Column(
      children: [
        IconButton.filledTonal(
          onPressed: onTap,
          tooltip: label,
          icon: Icon(icon),
          constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
        ),
        const SizedBox(height: 4),
        Text(
          const {
                'Reportar un animal': 'Reportar',
                'Gestionar reporte anónimo': 'Con clave',
                'Historias de rescate': 'Historial',
              }[label] ??
              label,
          textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 12, height: 1.3),
        ),
      ],
    ),
  );
}
