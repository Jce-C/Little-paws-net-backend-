import '../explore/session_action_gate.dart';
import 'request_detail_screen.dart';
import 'questionnaire_screen.dart';
import '../design/catalog_hero.dart';
import '../design/decision_card.dart';
import '../design/lpn_app_bar.dart';
import '../design/lpn_theme.dart';
import '../design/form_surfaces.dart';

import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../auth/account_screen.dart';
import '../auth/session.dart';
import '../core/api_client.dart';
import 'adoption_api.dart';
import 'catalog_controller.dart';
import 'public_pet_image.dart';
import 'public_pet_story.dart';
import 'pet_gallery.dart';
import '../design/refined_surfaces.dart';
export 'public_pet_image.dart' show PetPlaceholder;

class CatalogScreen extends StatefulWidget {
  const CatalogScreen({
    super.key,
    required this.api,
    required this.session,
    required this.onRequested,
  });

  final AdoptionApi api;
  final Session session;
  final VoidCallback onRequested;

  @override
  State<CatalogScreen> createState() => _CatalogScreenState();
}

class _CatalogScreenState extends State<CatalogScreen> {
  late final CatalogController _catalog = CatalogController(widget.api)
    ..reload();

  @override
  void dispose() {
    _catalog.dispose();
    super.dispose();
  }

  Future<void> _reload() => _catalog.reload();

  Future<void> _open(Pet pet) async {
    final sent = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) =>
            PetScreen(pet: pet, api: widget.api, session: widget.session),
      ),
    );
    if (mounted && sent == true) widget.onRequested();
  }

  @override
  Widget build(BuildContext context) => RefreshIndicator(
    onRefresh: _reload,
    child: ListenableBuilder(
      listenable: _catalog,
      builder: (context, child) {
        final species = {
          ..._catalog.species,
          if (_catalog.selectedSpecies.isNotEmpty) _catalog.selectedSpecies,
        }.toList()..sort();
        final activeFilter = _catalog.selectedSpecies;
        final pets = _catalog.pets;
        return CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            SliverToBoxAdapter(
              child: CatalogHero(
                species: species,
                selected: activeFilter,
                counter: !_catalog.loading && _catalog.error == null
                    ? (_catalog.nextCursor == null
                          ? '${pets.length} ${pets.length == 1 ? 'resultado' : 'resultados'}'
                          : '${pets.length} cargados')
                    : null,
                onSelected: (value) {
                  if (_catalog.selectedSpecies != value) {
                    _catalog.reload(species: value);
                  }
                },
              ),
            ),
            if (_catalog.loading)
              const SliverToBoxAdapter(
                child: Padding(
                  padding: EdgeInsets.all(28),
                  child: Center(
                    child: CircularProgressIndicator(
                      semanticsLabel: 'Cargando mascotas',
                    ),
                  ),
                ),
              )
            else if (_catalog.error != null)
              SliverToBoxAdapter(
                child: StatusPanel(
                  message: messageFor(
                    _catalog.error,
                    'No pudimos cargar las mascotas.',
                  ),
                  action: _reload,
                  actionLabel: 'Reintentar',
                ),
              )
            else if (pets.isEmpty)
              SliverToBoxAdapter(
                child: StatusPanel(
                  message: 'Todavía no hay mascotas disponibles para adopción.',
                  action: _reload,
                  actionLabel: 'Actualizar',
                ),
              )
            else
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(20, 12, 20, 24),
                sliver: SliverLayoutBuilder(
                  builder: (context, constraints) {
                    final scaler = MediaQuery.textScalerOf(context);
                    final columns = math.max(
                      1,
                      (constraints.crossAxisExtent /
                              math.max(160, 140 * scaler.scale(14) / 14))
                          .floor(),
                    );
                    const nameStyle = TextStyle(
                      fontSize: 20,
                      height: 1.25,
                      fontWeight: FontWeight.w700,
                    );
                    const captionStyle = TextStyle(fontSize: 14, height: 1.4);
                    final labelWidth = math.max(
                      1.0,
                      (constraints.crossAxisExtent - (columns - 1) * 14) /
                              columns -
                          32,
                    );
                    var labelHeight = 0.0;
                    for (final pet in pets) {
                      double measure(
                        String text, {
                        bool bold = false,
                        bool strong = false,
                        double inset = 0,
                      }) {
                        if (text.isEmpty) return 0;
                        final painter = TextPainter(
                          text: TextSpan(
                            text: text,
                            style: Theme.of(context).textTheme.bodyMedium!
                                .merge(bold ? nameStyle : captionStyle)
                                .copyWith(
                                  fontWeight: bold || strong
                                      ? FontWeight.w700
                                      : FontWeight.w400,
                                ),
                          ),
                          textDirection: Directionality.of(context),
                          textScaler: scaler,
                          maxLines: 2,
                          ellipsis: '…',
                        )..layout(maxWidth: math.max(1, labelWidth - inset));
                        final height = painter.height;
                        painter.dispose();
                        return height;
                      }

                      labelHeight = math.max(
                        labelHeight,
                        measure(pet.name, bold: true) +
                            measure(pet.summary) +
                            measure(pet.attributes, inset: 12) +
                            (pet.attributes.isNotEmpty ? 8 : 0) +
                            measure(pet.description) +
                            math.max(
                              48,
                              24 +
                                  measure(
                                    'Ver detalles',
                                    inset: 52,
                                    strong: true,
                                  ),
                            ) +
                            measure('En adopción'),
                      );
                    }
                    return SliverGrid.builder(
                      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: columns,
                        mainAxisExtent: 248 + labelHeight,
                        crossAxisSpacing: 14,
                        mainAxisSpacing: 10,
                      ),
                      itemCount: pets.length,
                      itemBuilder: (context, index) {
                        final pet = pets[index];
                        return Semantics(
                          button: true,
                          excludeSemantics: true,
                          label:
                              '${pet.name}. ${pet.summary}${pet.attributes.isNotEmpty ? '. ${pet.attributes}' : ''}${pet.description.isNotEmpty ? '. ${pet.description}' : ''}',
                          onTap: () => _open(pet),
                          child: Card(
                            margin: EdgeInsets.zero,
                            clipBehavior: Clip.antiAlias,
                            child: InkWell(
                              onTap: () => _open(pet),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.stretch,
                                children: [
                                  SizedBox(
                                    height: 144,
                                    child: PublicPetImage(
                                      pet: pet,
                                      origin: widget.api.api.base,
                                    ),
                                  ),
                                  Expanded(
                                    child: Padding(
                                      padding: const EdgeInsets.all(16),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.stretch,
                                        children: [
                                          Text(
                                            pet.name,
                                            style: nameStyle,
                                            maxLines: 2,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                          const SizedBox(height: 4),
                                          const Text(
                                            'En adopción',
                                            style: TextStyle(
                                              fontSize: 14,
                                              height: 1.4,
                                              color: LpnColors.sage,
                                              fontWeight: FontWeight.w600,
                                            ),
                                          ),
                                          const SizedBox(height: 12),
                                          if (pet.attributes.isNotEmpty)
                                            Text(
                                              pet.attributes,
                                              style: captionStyle,
                                              maxLines: 2,
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                          if (pet.summary.isNotEmpty) ...[
                                            const SizedBox(height: 4),
                                            Text(
                                              pet.summary,
                                              style: captionStyle,
                                              maxLines: 2,
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                          ],
                                          if (pet.description.isNotEmpty) ...[
                                            const SizedBox(height: 12),
                                            Text(
                                              pet.description,
                                              style: captionStyle,
                                              maxLines: 2,
                                              overflow: TextOverflow.ellipsis,
                                            ),
                                          ],
                                          const Spacer(),
                                          const SizedBox(height: 12),
                                          const DecisionAction('Ver detalles'),
                                        ],
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        );
                      },
                    );
                  },
                ),
              ),
            if (!_catalog.loading &&
                _catalog.error == null &&
                (_catalog.nextCursor != null || _catalog.loadingMore))
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
                  child: _catalog.loadingMore
                      ? const Center(
                          child: CircularProgressIndicator(
                            semanticsLabel: 'Cargando más mascotas',
                          ),
                        )
                      : _catalog.pageError != null
                      ? StatusPanel(
                          message: messageFor(
                            _catalog.pageError,
                            'No pudimos cargar más mascotas.',
                          ),
                          action: _catalog.loadMore,
                          actionLabel: 'Reintentar carga',
                        )
                      : OutlinedButton.icon(
                          onPressed: _catalog.loadMore,
                          icon: const Icon(Icons.expand_more),
                          label: const Text('Cargar más'),
                        ),
                ),
              ),
            SliverToBoxAdapter(
              child: SizedBox(height: MediaQuery.paddingOf(context).bottom),
            ),
          ],
        );
      },
    ),
  );
}

class PetScreen extends StatefulWidget {
  const PetScreen({
    super.key,
    required this.pet,
    required this.api,
    required this.session,
  });
  final Pet pet;
  final AdoptionApi api;
  final Session session;
  @override
  State<PetScreen> createState() => _PetScreenState();
}

class _PetScreenState extends State<PetScreen> {
  late Future<PetDetail> _detail = widget.api.detail(widget.pet.id);
  Future<void> _reload() async {
    final next = widget.api.detail(widget.pet.id);
    setState(() {
      _detail = next;
    });
    try {
      await next;
    } on Exception {
      /* The screen offers retry. */
    }
  }

  Future<void> _apply(Pet pet) async {
    if (!widget.session.signedIn && !await openLogin(context, widget.session)) {
      return;
    }
    if (!mounted) return;
    final sent = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => widget.session.account?.adoptionEvaluation == true
            ? AdoptionQuestionnaireScreen(pet: pet, api: widget.api)
            : RequestDialog(pet: pet, api: widget.api, fullPage: true),
      ),
    );
    if (!mounted) return;
    if (sent == true) {
      Navigator.of(context).pop(true);
    } else {
      await _reload();
    }
  }

  @override
  Widget build(BuildContext context) => FutureBuilder<PetDetail>(
    future: _detail,
    builder: (context, snapshot) {
      final detail =
          snapshot.connectionState == ConnectionState.done && !snapshot.hasError
          ? snapshot.data
          : null;
      return Scaffold(
        appBar: lpnAppBar(
          context,
          'Conoce a ${detail?.pet.name ?? widget.pet.name}',
          actions: [
            IconButton(
              tooltip: 'Actualizar ficha',
              onPressed: snapshot.connectionState == ConnectionState.done
                  ? _reload
                  : null,
              icon: const Icon(Icons.refresh),
            ),
          ],
        ),
        body: SafeArea(
          child: Column(
            children: [
              Expanded(
                child: RefreshIndicator(
                  onRefresh: _reload,
                  child: ListView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: EdgeInsets.fromLTRB(
                      20,
                      20,
                      20,
                      20 + MediaQuery.paddingOf(context).bottom,
                    ),
                    children: [
                      if (snapshot.connectionState != ConnectionState.done)
                        const Center(
                          child: CircularProgressIndicator(
                            semanticsLabel: 'Cargando ficha',
                          ),
                        )
                      else if (snapshot.hasError)
                        StatusPanel(
                          message: messageFor(
                            snapshot.error,
                            'No pudimos cargar la ficha.',
                          ),
                          action: _reload,
                          actionLabel: 'Reintentar',
                        )
                      else if (detail != null) ...[
                        PetGallery(
                          key: ValueKey(
                            '${detail.pet.id}:${detail.photos.map((photo) => photo.path).join(',')}',
                          ),
                          detail: detail,
                          origin: widget.api.api.base,
                        ),
                        const SizedBox(height: 18),
                        if (detail.pet.summary.isNotEmpty) ...[
                          Text(
                            detail.pet.summary,
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 14),
                          ),
                          const SizedBox(height: 16),
                        ],
                        PublicPetFacts(detail: detail),
                        const SizedBox(height: 20),
                        FormCard(
                          title: 'Sobre esta mascota',
                          child: Text(
                            detail.pet.description.isNotEmpty
                                ? detail.pet.description
                                : 'La organización todavía no ha publicado una descripción.',
                          ),
                        ),
                        const SizedBox(height: 16),
                        AdoptionReadiness(
                          specialCare: detail.pet.presentation?.care ?? '',
                          spaceNeeds: detail.pet.presentation?.space ?? '',
                        ),
                        const SizedBox(height: 32),
                        PublicPetStory(detail: detail),
                        const SizedBox(height: 18),
                        const Text(
                          'La organización revisará tu solicitud. Puedes consultar su decisión en Solicitudes.',
                          style: TextStyle(fontSize: 14, height: 1.5),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'Esta ficha pública no incluye el expediente médico ni datos privados de personas.',
                          style: TextStyle(fontSize: 14, height: 1.5),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              if (detail != null)
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 8, 20, 12),
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(
                        minWidth: 160,
                        maxWidth: 260,
                      ),
                      child: FilledButton(
                        onPressed: () => _apply(detail.pet),
                        child: const Text(
                          'Solicitar adopción',
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      );
    },
  );
}

class RequestDialog extends StatelessWidget {
  const RequestDialog({
    super.key,
    required this.pet,
    required this.api,
    this.fullPage = false,
  });
  final bool fullPage;
  final Pet pet;
  final AdoptionApi api;

  @override
  Widget build(BuildContext context) => SessionActionGate(
    session: api.session,
    title: 'Solicitud de adopción',
    message: 'Inicia sesión para enviar una solicitud.',
    form: (identity) => _LegacyRequestForm(
      key: identity,
      pet: pet,
      api: api,
      fullPage: fullPage,
    ),
  );
}

class _LegacyRequestForm extends StatefulWidget {
  const _LegacyRequestForm({
    super.key,
    required this.pet,
    required this.api,
    this.fullPage = false,
  });
  final bool fullPage;
  final Pet pet;
  final AdoptionApi api;

  @override
  State<_LegacyRequestForm> createState() => _RequestDialogState();
}

class _RequestDialogState extends State<_LegacyRequestForm> {
  final _note = TextEditingController();
  bool _sending = false;
  bool _leaving = false, _confirming = false;
  bool _uncertain = false;
  String? _error;

  @override
  void dispose() {
    _note.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    if (_sending || _uncertain) return;
    setState(() {
      _sending = true;
      _error = null;
    });
    try {
      final id = await widget.api.request(widget.pet.id, _note.text);
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Solicitud #$id enviada.')));
      await _close(true);
    } on Exception catch (error) {
      if (mounted) {
        setState(() {
          // A lost response does not prove the transaction failed. Do not offer
          // another POST before the person checks their server-side requests.
          _uncertain =
              error is! ApiException ||
              error.status == null ||
              error.status! >= 500;
          _error = _uncertain
              ? 'No pudimos confirmar si se creó la solicitud. Revisa tus solicitudes antes de volver a enviarla.'
              : messageFor(
                  error,
                  'No pudimos completar el envío. Revisa los datos.',
                );
        });
      }
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  Future<void> _close([bool? result]) async {
    if (!mounted) return;
    setState(() => _leaving = true);
    await WidgetsBinding.instance.endOfFrame;
    if (mounted) Navigator.of(context).pop(result);
  }

  Future<void> _cancel() async {
    if (_sending || _confirming) return;
    if (_note.text.trim().isNotEmpty) {
      _confirming = true;
      final discard = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          scrollable: true,
          title: const Text('¿Descartar la solicitud?'),
          content: Text(
            _uncertain
                ? 'El envío podría haberse completado. Salir no lo anula; revisa Mis solicitudes antes de repetirlo.'
                : 'Se descartará el mensaje que escribiste.',
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
    await _close();
  }

  List<Widget> _actions(BuildContext context) => [
    TextButton(
      onPressed: _sending ? null : _cancel,
      child: const Text('Cancelar'),
    ),
    FilledButton(
      onPressed: _sending
          ? null
          : _uncertain
          ? () => _close(true)
          : _send,
      child: Text(
        _sending
            ? 'Enviando…'
            : _uncertain
            ? 'Ver mis solicitudes'
            : 'Enviar solicitud',
      ),
    ),
  ];

  Widget _fields(BuildContext context) => LpnFormSection(
    title: 'Tu solicitud',
    icon: Icons.favorite_border_rounded,
    description:
        'La organización revisará tu solicitud antes de decidir la adopción.',
    children: [
      Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: LpnColors.sageSoft,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          children: [
            const Icon(Icons.pets_outlined, color: LpnColors.sage),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Quieres adoptar a',
                    style: TextStyle(fontSize: 14, color: LpnColors.muted),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    widget.pet.name,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      if (widget.fullPage) ...[
        const SizedBox(height: 20),
        const Text(
          'Envías la solicitud como',
          style: TextStyle(fontSize: 14, color: LpnColors.muted),
        ),
        const SizedBox(height: 4),
        Text(
          widget.api.session.account?.name ?? '',
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
      ],
      const SizedBox(height: 24),
      AdoptionReadiness(
        specialCare: widget.pet.presentation?.care ?? '',
        spaceNeeds: widget.pet.presentation?.space ?? '',
      ),
      const SizedBox(height: 24),
      LpnFieldLabel(
        label: '¿Por qué quieres adoptar? (opcional)',
        child: TextField(
          key: const Key('adoption-note'),
          controller: _note,
          onChanged: (_) => setState(() {}),
          enabled: !_sending && !_uncertain,
          maxLength: 2000,
          style: const TextStyle(fontSize: 16, height: 1.5),
          minLines: 3,
          maxLines: 5,
          decoration: const InputDecoration(
            counterText: '',
            hintText: 'Háblanos del hogar que puedes ofrecer.',
          ),
        ),
      ),
      const SizedBox(height: 12),
      const Text(
        'Después del envío podrás consultar el estado en Mis solicitudes.',
        style: TextStyle(fontSize: 14, height: 1.5, color: LpnColors.muted),
      ),
      if (_error != null) ...[
        const SizedBox(height: 16),
        Semantics(
          liveRegion: true,
          child: Text(
            _error!,
            style: TextStyle(color: Theme.of(context).colorScheme.error),
          ),
        ),
      ],
    ],
  );

  @override
  Widget build(BuildContext context) => PopScope(
    canPop: _leaving || (!_sending && _note.text.trim().isEmpty),
    onPopInvokedWithResult: (didPop, _) {
      if (!didPop) _cancel();
    },
    child: widget.fullPage
        ? Scaffold(
            appBar: lpnAppBar(context, 'Solicitud de adopción'),
            body: Column(
              children: [
                Expanded(
                  child: ListView(
                    padding: const EdgeInsets.fromLTRB(28, 16, 28, 24),
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(20),
                        child: Image.asset(
                          'assets/request-banner.webp',
                          height: 148,
                          fit: BoxFit.cover,
                          excludeFromSemantics: true,
                        ),
                      ),
                      const SizedBox(height: 24),
                      _fields(context),
                      const SizedBox(height: 24),
                      const Text(
                        'Gracias por querer dar un hogar.',
                        textAlign: TextAlign.center,
                        style: TextStyle(fontSize: 12),
                      ),
                    ],
                  ),
                ),
                LpnActionBar(
                  child: Wrap(
                    spacing: 12,
                    runSpacing: 8,
                    alignment: WrapAlignment.end,
                    children: _actions(context),
                  ),
                ),
              ],
            ),
          )
        : AlertDialog(
            backgroundColor: const Color(0xfffbefd5),
            title: const Text(
              'Solicitud de adopción',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 15),
            ),
            constraints: const BoxConstraints(maxWidth: 380),
            scrollable: true,
            content: _fields(context),
            actions: _actions(context),
          ),
  );
}

class RequestsScreen extends StatelessWidget {
  const RequestsScreen({super.key, required this.api, required this.session});
  final AdoptionApi api;
  final Session session;

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: session,
    builder: (context, child) {
      if (session.restoring) {
        return const Center(child: CircularProgressIndicator());
      }
      if (!session.signedIn) {
        return StatusPanel(
          message: 'Inicia sesión para consultar tus solicitudes.',
          action: () => openLogin(context, session),
          actionLabel: 'Iniciar sesión',
        );
      }
      return _RequestList(
        key: ValueKey((session.identityRevision, session.account!.email)),
        api: api,
      );
    },
  );
}

class _RequestList extends StatefulWidget {
  const _RequestList({super.key, required this.api});
  final AdoptionApi api;

  @override
  State<_RequestList> createState() => _RequestListState();
}

class _RequestListState extends State<_RequestList> {
  String? _next;
  bool _loadingMore = false;
  int _generation = 0;
  String? _pageError;
  bool _refreshing = true;
  bool _opening = false;
  Future<List<AdoptionRequest>> _fetch() async {
    final generation = _generation;
    try {
      final page = await widget.api.requestPage();
      if (mounted && generation == _generation) _next = page.next;
      return page.rows;
    } finally {
      if (mounted && generation == _generation) {
        setState(() => _refreshing = false);
      }
    }
  }

  Future<void> _open(AdoptionRequest request) async {
    if (_opening || _refreshing) return;
    _opening = true;
    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) =>
            RequestDetailScreen(session: widget.api.session, id: request.id),
      ),
    );
    if (mounted) {
      _opening = false;
      await _reload();
    }
  }

  late Future<List<AdoptionRequest>> _requests = _fetch();
  Future<void> _more() async {
    if (_loadingMore || _refreshing || _next == null) return;
    final generation = _generation;
    final cursor = _next!;
    setState(() {
      _loadingMore = true;
      _pageError = null;
    });
    try {
      final current = await _requests;
      if (!mounted || generation != _generation) return;
      final page = await widget.api.requestPage(before: cursor);
      if (mounted && generation == _generation) {
        setState(() {
          _next = page.next;
          _requests = Future.value([
            ...current,
            ...page.rows.where(
              (row) => !current.any((old) => old.id == row.id),
            ),
          ]);
        });
      }
    } on Exception catch (error) {
      if (mounted && generation == _generation) {
        setState(
          () => _pageError = messageFor(
            error,
            'No pudimos cargar más solicitudes.',
          ),
        );
      }
    } finally {
      if (mounted && generation == _generation) {
        setState(() => _loadingMore = false);
      }
    }
  }

  Future<void> _reload() async {
    if (_refreshing) return;
    _refreshing = true;
    _next = null;
    _generation++;
    _loadingMore = false;
    _pageError = null;
    final next = _fetch();
    setState(() {
      _requests = next;
    });
    try {
      await _requests;
    } on Exception {
      // The list displays the error and offers retry.
    }
  }

  @override
  Widget build(BuildContext context) => RefreshIndicator(
    onRefresh: _reload,
    child: FutureBuilder<List<AdoptionRequest>>(
      future: _requests,
      builder: (context, state) => ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(20),
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  'Mis solicitudes',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
              ),
              IconButton(
                tooltip: 'Actualizar solicitudes',
                onPressed: _refreshing ? null : _reload,
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
          if (state.connectionState != ConnectionState.done)
            const Padding(
              padding: EdgeInsets.all(24),
              child: Center(child: CircularProgressIndicator()),
            )
          else if (state.hasError)
            StatusPanel(
              message: messageFor(
                state.error,
                'No pudimos consultar tus solicitudes.',
              ),
              action: _reload,
              actionLabel: 'Reintentar',
            )
          else if (state.data!.isEmpty)
            const StatusPanel(
              message: 'Todavía no has enviado solicitudes de adopción.',
            )
          else
            for (final request in state.data!)
              Card(
                color: LpnFormPalette.tones[0],
                elevation: 0,
                child: InkWell(
                  borderRadius: BorderRadius.circular(20),
                  onTap: () => _open(request),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Row(
                          children: [
                            if (request.photo != null)
                              ClipRRect(
                                borderRadius: BorderRadius.circular(12),
                                child: Image.memory(
                                  request.photo!,
                                  width: 56,
                                  height: 56,
                                  fit: BoxFit.cover,
                                  semanticLabel: 'Fotografía de la mascota',
                                ),
                              )
                            else
                              const Icon(
                                Icons.pets_outlined,
                                color: LpnColors.sage,
                              ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                request.petName ?? 'Tu solicitud',
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                            const Icon(Icons.chevron_right),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Solicitud #${request.id}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        const SizedBox(height: 4),
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(
                              Icons.info_outline,
                              size: 18,
                              color: LpnColors.sage,
                            ),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                request.status,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                          ],
                        ),
                        if (request.createdAt != null)
                          Padding(
                            padding: const EdgeInsets.only(top: 8),
                            child: Text(
                              MaterialLocalizations.of(
                                context,
                              ).formatMediumDate(request.createdAt!.toLocal()),
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
          if (_pageError != null) Text(_pageError!),
          if (_next != null)
            TextButton(
              onPressed: _loadingMore ? null : _more,
              child: Text(_loadingMore ? 'Cargando…' : 'Ver más solicitudes'),
            ),
        ],
      ),
    ),
  );
}

String messageFor(Object? error, String fallback) =>
    error is ApiException ? error.message : fallback;

class StatusPanel extends StatelessWidget {
  const StatusPanel({
    super.key,
    required this.message,
    this.action,
    this.actionLabel,
  });
  final String message;
  final VoidCallback? action;
  final String? actionLabel;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.all(24),
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Icon(Icons.pets_outlined, size: 30),
        const SizedBox(height: 10),
        Semantics(
          liveRegion: true,
          child: Text(message, textAlign: TextAlign.center),
        ),
        if (action != null) ...[
          const SizedBox(height: 12),
          OutlinedButton(onPressed: action, child: Text(actionLabel!)),
        ],
      ],
    ),
  );
}
