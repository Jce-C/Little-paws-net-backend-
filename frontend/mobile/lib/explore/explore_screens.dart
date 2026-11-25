import '../design/form_surfaces.dart';
import '../design/readable_text.dart';
import 'bank_instructions.dart';
import 'cop_amount.dart';
import 'product_presentation.dart';
import 'product_catalog_screen.dart';

import 'package:flutter/material.dart';

import '../adoption/adoption_screens.dart' show StatusPanel, messageFor;
import '../auth/account_screen.dart';
import '../auth/session.dart';
import '../core/api_client.dart';
import '../design/lpn_app_bar.dart';
import '../design/lpn_theme.dart';
import '../design/organic_surface.dart';
import '../design/refined_surfaces.dart';
import 'community_screen.dart';
import 'organization_public_info.dart';
import 'organization_logo.dart';
import 'message_composer.dart';
import 'help_program.dart';
import 'help_offer_card.dart';
import '../design/decision_card.dart';
import 'session_action_gate.dart';

class ExploreScreen extends StatelessWidget {
  const ExploreScreen({
    super.key,
    required this.api,
    required this.session,
    required this.onRescue,
    required this.onAdopt,
  });
  final ApiClient api;
  final Session session;
  final VoidCallback onRescue, onAdopt;
  void _open(BuildContext context, Widget child) =>
      Navigator.of(context).push(MaterialPageRoute(builder: (_) => child));
  @override
  Widget build(BuildContext context) => HomeBackdrop(
    child: ListView(
      padding: EdgeInsets.only(
        bottom: 20 + MediaQuery.paddingOf(context).bottom,
      ),
      children: [
        const IntegratedHomeHeader(),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: FeatureDeck(
            quickActions: true,
            shortcuts: [
              FeatureRow(
                icon: Icons.pets_outlined,
                title: 'Adopta un compañero',
                subtitle: 'Mascotas en adopción',
                onTap: onAdopt,
              ),
              FeatureRow(
                icon: Icons.health_and_safety_outlined,
                title: 'Ayuda a un animal',
                subtitle: 'Consulta o crea un reporte',
                color: LpnColors.blush,
                onTap: onRescue,
              ),
              FeatureRow(
                icon: Icons.volunteer_activism_outlined,
                title: 'Ayudas',
                subtitle: 'Tiempo, insumos o aportes',
                color: LpnColors.butter,
                onTap: () =>
                    _open(context, HelpScreen(api: api, session: session)),
              ),
              FeatureRow(
                icon: Icons.storefront_outlined,
                title: 'Organizaciones',
                subtitle: 'Contactos y servicios',
                onTap: () => _open(
                  context,
                  PublicListScreen(
                    api: api,
                    path: '/api/red/organizaciones/',
                    title: 'Nuestra red',
                    kind: 'organizations',
                  ),
                ),
              ),
            ],
            children: [
              FeatureRow(
                icon: Icons.forum_outlined,
                title: 'Comunidad',
                subtitle: 'Comparte y conversa',
                color: LpnColors.blush,
                onTap: () =>
                    _open(context, CommunityScreen(api: api, session: session)),
              ),
              FeatureRow(
                icon: Icons.shopping_bag_outlined,
                title: 'Tienda',
                subtitle: 'Productos para su cuidado',
                color: LpnColors.butter,
                onTap: () => _open(
                  context,
                  PublicListScreen(
                    api: api,
                    session: session,
                    path: '/api/catalogo/productos/',
                    title: 'Tienda',
                    kind: 'products',
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );
}

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key, required this.api, required this.session});
  final ApiClient api;
  final Session session;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Ayudas'),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          'Tu ayuda tiene\nmuchas formas.',
          style: Theme.of(context).textTheme.headlineSmall,
        ),
        const SizedBox(height: 24),
        for (final mode in [
          'Aporte monetario',
          'Tiempo y voluntariado',
          'Ayuda en especie',
        ])
          FeatureRow(
            icon: mode == 'Aporte monetario'
                ? Icons.savings_outlined
                : mode == 'Tiempo y voluntariado'
                ? Icons.schedule
                : Icons.inventory_2_outlined,
            title: mode,
            subtitle: mode == 'Aporte monetario'
                ? 'Registra un compromiso, sin cobros.'
                : mode == 'Tiempo y voluntariado'
                ? 'Elige una actividad y acuerda tu participación.'
                : 'Ofrece insumos según las necesidades publicadas.',
            color: mode == 'Aporte monetario'
                ? LpnColors.butter
                : mode == 'Tiempo y voluntariado'
                ? LpnColors.sageSoft
                : LpnFormPalette.tones[2],
            onTap: () => Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => PublicListScreen(
                  api: api,
                  session: session,
                  path: mode == 'Aporte monetario'
                      ? '/api/fondos/'
                      : '/api/red/organizaciones/',
                  title: mode,
                  kind: mode == 'Aporte monetario' ? 'funds' : 'help',
                ),
              ),
            ),
          ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          icon: const Icon(Icons.link_outlined),
          label: const Text('Canales publicados por las organizaciones'),
          onPressed: () => Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => PublicListScreen(
                api: api,
                path: '/api/red/organizaciones/',
                title: 'Canales de aporte',
                kind: 'channels',
              ),
            ),
          ),
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          icon: const Icon(Icons.history),
          label: const Text('Mis ofrecimientos'),
          onPressed: () async {
            if (!session.signedIn && !await openLogin(context, session)) return;
            if (!context.mounted) return;
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => PublicListScreen(
                  api: api,
                  session: session,
                  path: '/api/ayudas/intereses/',
                  title: 'Mis ofrecimientos',
                  kind: 'offers',
                ),
              ),
            );
          },
        ),
        const SizedBox(height: 12),
        const Text(
          'No transfieras dinero a contactos sin verificar. Aquí no se procesa ningún cobro ni se inventan cuentas bancarias.',
        ),
      ],
    ),
  );
}

class PublicListScreen extends StatelessWidget {
  const PublicListScreen({
    super.key,
    required this.api,
    required this.path,
    required this.title,
    required this.kind,
    this.session,
  });
  final ApiClient api;
  final Session? session;
  final String path, title, kind;

  Widget _body({Key? key}) => _PublicListBody(
    key: key,
    api: api,
    path: path,
    title: title,
    kind: kind,
    session: session,
  );
  Widget _signIn(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, title),
    body: StatusPanel(
      message: 'Inicia sesión para consultar tus ofrecimientos de ayuda.',
      action: session == null ? null : () => openLogin(context, session!),
      actionLabel: 'Iniciar sesión',
    ),
  );
  @override
  Widget build(BuildContext context) {
    if (kind == 'products' && session != null) {
      return ProductCatalogScreen(
        api: api,
        onOpen: (row) => Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) =>
                ProductScreen(row: row, api: api, session: session!),
          ),
        ),
      );
    }
    if (kind != 'offers') return _body();
    final current = session;
    if (current == null) return _signIn(context);
    return ListenableBuilder(
      listenable: current,
      builder: (context, _) {
        if (current.restoring) {
          return Scaffold(
            appBar: lpnAppBar(context, title),
            body: const Center(child: CircularProgressIndicator()),
          );
        }
        if (!current.signedIn) return _signIn(context);
        return _body(
          key: ValueKey((current.identityRevision, current.account!.email)),
        );
      },
    );
  }
}

class _PublicListBody extends StatefulWidget {
  const _PublicListBody({
    super.key,
    required this.api,
    required this.path,
    required this.title,
    required this.kind,
    this.session,
  });
  final ApiClient api;
  final Session? session;
  final String path, title, kind;
  @override
  State<_PublicListBody> createState() => _PublicListBodyState();
}

class _PublicListBodyState extends State<_PublicListBody> {
  Future<void> _offer(Map<String, dynamic> row, [String? activity]) async {
    final session = widget.session!;
    if (!session.signedIn && !await openLogin(context, session)) {
      return;
    }
    if (!mounted) return;
    final saved = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => PublicMessageScreen(
          api: widget.api,
          session: session,
          path: '/api/ayudas/intereses/',
          title: 'Ofrecer ayuda',
          textKey: 'mensaje',
          public: false,
          targetLabel:
              'Organización: ${row["nombre"]}${activity == null ? '' : '\nActividad: $activity'}',
          extra: {
            'fundacion_id': row['id'],
            'actividad': ?activity,
            'modalidad':
                activity != null || widget.title.contains('voluntariado')
                ? 'voluntariado'
                : 'especie',
          },
        ),
      ),
    );
    if (saved == true && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Interés registrado. La organización aún no lo ha aceptado.',
          ),
        ),
      );
    }
  }

  late Future<List<Map<String, dynamic>>> _data = _load();
  String _filter = '';
  bool _loading = true;
  Future<List<Map<String, dynamic>>> _load() async {
    try {
      final value = widget.kind == 'offers'
          ? await widget.session!.authorized(
              (token) => widget.api.get(widget.path, token: token),
            )
          : await widget.api.get(widget.path);
      if (value is! List ||
          value.length > 300 ||
          value.any((row) => row is! Map<String, dynamic>)) {
        throw const ApiException('No pudimos interpretar el catálogo.');
      }
      final rows = value.cast<Map<String, dynamic>>();
      if (_filter.isNotEmpty &&
          !rows.any(
            (row) =>
                row[widget.kind == 'products' ? 'categoria' : 'tipo'] ==
                _filter,
          )) {
        _filter = '';
      }
      return rows;
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _reload() async {
    if (_loading) return;
    final next = _load();
    setState(() {
      _loading = true;
      _data = next;
    });
    try {
      await next;
    } on Exception {
      /* FutureBuilder displays the error. */
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(
      context,
      widget.title,
      actions: [
        if (widget.kind == 'organizations' ||
            widget.kind == 'help' ||
            widget.kind == 'channels')
          IconButton(
            tooltip: 'Actualizar directorio',
            onPressed: _loading ? null : _reload,
            icon: const Icon(Icons.refresh),
          ),
      ],
    ),
    body: FutureBuilder<List<Map<String, dynamic>>>(
      future: _data,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return SingleChildScrollView(
            child: StatusPanel(
              message: messageFor(
                snapshot.error,
                'No pudimos consultar esta sección.',
              ),
              action: _reload,
              actionLabel: 'Reintentar',
            ),
          );
        }
        final volunteers =
            widget.kind == 'help' && widget.title.contains('voluntariado');
        final data = snapshot.data!
            .where((row) => widget.kind != 'help' || row['tipo'] == 'Fundación')
            .where((row) => !volunteers || row['acepta_voluntarios'] == true)
            .where(
              (row) =>
                  widget.kind != 'channels' ||
                  (row['programa_ayuda'] is Map &&
                      row['programa_ayuda']['canales'] is List &&
                      (row['programa_ayuda']['canales'] as List).isNotEmpty),
            )
            .toList();
        if (widget.kind == 'offers') {
          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Text(
                'Mis ofrecimientos',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 16),
              const Text(
                'Intereses enviados. La organización debe acordar contigo la participación o entrega.',
              ),
              if (data.isEmpty)
                const StatusPanel(
                  message: 'Todavía no has registrado ofrecimientos de ayuda.',
                ),
              const SizedBox(height: 16),
              for (final row in data) HelpOfferCard(row: row),
            ],
          );
        }
        final choices =
            data
                .map(
                  (row) =>
                      '${row[widget.kind == 'products' ? 'categoria' : 'tipo'] ?? ''}',
                )
                .where((v) => v.isNotEmpty)
                .toSet()
                .toList()
              ..sort();
        final visible = data
            .where(
              (row) =>
                  _filter.isEmpty ||
                  row[widget.kind == 'products' ? 'categoria' : 'tipo'] ==
                      _filter,
            )
            .toList();
        return ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(
              widget.title,
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            if (widget.kind == 'help')
              const Padding(
                padding: EdgeInsets.only(bottom: 16),
                child: Text(
                  'Puedes manifestar tu interés a una fundación verificada. El registro no equivale a una aceptación; la organización debe acordar contigo cualquier actividad o entrega.',
                ),
              ),
            if (choices.isNotEmpty)
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: [
                  for (final value in ['', ...choices])
                    ChoiceChip(
                      label: Text(value.isEmpty ? 'Todas' : value),
                      selected: value == _filter,
                      onSelected: (_) => setState(() => _filter = value),
                    ),
                ],
              ),
            const SizedBox(height: 16),
            if (visible.isEmpty)
              const StatusPanel(
                message:
                    'Todavía no hay información publicada en esta categoría.',
              ),
            for (final row in visible)
              if (widget.kind == 'products')
                ProductCatalogCard(
                  row: row,
                  origin: widget.api.base,
                  onOpen: () => Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => ProductScreen(
                        row: row,
                        api: widget.api,
                        session: widget.session!,
                      ),
                    ),
                  ),
                )
              else if (widget.kind == 'organizations')
                Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      borderRadius: BorderRadius.circular(20),
                      onTap: () => Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => OrganizationDetailScreen(
                            row: row,
                            origin: widget.api.base,
                          ),
                        ),
                      ),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 20,
                        ),
                        decoration: BoxDecoration(
                          border: Border(
                            bottom: BorderSide(
                              color: Theme.of(context).dividerColor
                                  .withValues(alpha: .2),
                            ),
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            OrganizationIdentity(
                              row: row,
                              origin: widget.api.base,
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    'Ver contacto y servicios',
                                    style: TextStyle(
                                      fontWeight: FontWeight.w600,
                                      color: Theme.of(context)
                                          .colorScheme
                                          .primary,
                                    ),
                                  ),
                                ),
                                const Icon(Icons.arrow_outward, size: 20),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                )
              else
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        if (widget.kind == 'organizations' ||
                            widget.kind == 'help' ||
                            widget.kind == 'channels')
                          OrganizationIdentity(
                            row: row,
                            origin: widget.api.base,
                          )
                        else
                          DecisionHeading(
                            title:
                                '${row['nombre'] ?? row['organizacion'] ?? 'Sin nombre registrado'}',
                            contextLine: widget.kind == 'funds'
                                ? 'Fondo de ayuda'
                                : null,
                          ),
                        const SizedBox(height: 8),
                        if (widget.kind == 'funds') ...[
                          Text('Administra: ${row['administradora'] ?? ''}'),
                          const SizedBox(height: 12),
                          OutlinedButton(
                            onPressed: () => Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => ContributionScreen(
                                  row: row,
                                  api: widget.api,
                                  session: widget.session!,
                                ),
                              ),
                            ),
                            child: const Text('Ofrecer un aporte'),
                          ),
                        ] else ...[
                          if (widget.kind == 'offers')
                            Text(
                              'Modalidad: ${row['modalidad']}. Interés registrado; pendiente de acuerdo con la organización.',
                            ),
                          if (widget.kind == 'help' &&
                              row['tipo'] == 'Fundación') ...[
                            if ('${row['necesidades_ayuda'] ?? ''}'.isNotEmpty)
                              Text(
                                'Necesidades publicadas: ${row['necesidades_ayuda']}',
                              ),
                            HelpProgramInfo(
                              row: row,
                              onActivity: widget.title.contains('voluntariado')
                                  ? (title) => _offer(row, title)
                                  : null,
                            ),
                            const SizedBox(height: 16),
                            OutlinedButton(
                              onPressed: () => _offer(row),
                              child: const Text('Manifestar mi interés'),
                            ),
                          ],
                          if (widget.kind == 'channels')
                            HelpProgramInfo(row: row, showActivities: false),
                          if (widget.kind == 'organizations' ||
                              widget.kind == 'help')
                            OrganizationPublicInfo(row: row, compact: true),
                          if (widget.kind == 'organizations' ||
                              widget.kind == 'help')
                            Align(
                              alignment: AlignmentDirectional.centerStart,
                              child: TextButton.icon(
                                icon: const Icon(Icons.info_outline, size: 18),
                                label: const Text('Ver contacto y servicios'),
                                onPressed: () => Navigator.of(context).push(
                                  MaterialPageRoute(
                                    builder: (_) => OrganizationDetailScreen(
                                      row: row,
                                      origin: widget.api.base,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                        ],
                      ],
                    ),
                  ),
                ),
          ],
        );
      },
    ),
  );
}

class ProductScreen extends StatelessWidget {
  const ProductScreen({
    super.key,
    required this.row,
    required this.api,
    required this.session,
  });
  final Map<String, dynamic> row;
  final ApiClient api;
  final Session session;
  @override
  Widget build(BuildContext context) {
    final ready =
        (productStock(row) ?? 0) > 0 && CopAmount.parse(row['precio']) != null;
    return Scaffold(
      appBar: lpnAppBar(context, 'Producto'),
      bottomNavigationBar: LpnKeyboardSafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: FilledButton.icon(
            onPressed: ready
                ? () => Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) =>
                          OrderScreen(row: row, api: api, session: session),
                    ),
                  )
                : null,
            icon: const Icon(Icons.shopping_bag_outlined),
            label: Text(ready ? 'Preparar pedido' : 'No disponible'),
          ),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          ProductPresentation(row: row, origin: api.base),
          const SizedBox(height: 28),
          Text(
            'Sobre el producto',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          ReadableText(
            '${row['descripcion'] ?? 'Sin descripción publicada.'}',
            style: const TextStyle(height: 1.5),
          ),
          const SizedBox(height: 24),
          const Text(
            'El pedido no procesa pagos ni reserva existencias.',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: LpnColors.ink,
            ),
          ),
          if (row['credito_foto'] is String)
            ExpansionTile(
              tilePadding: EdgeInsets.zero,
              title: const Text('Créditos de la fotografía'),
              children: [ReadableText(row['credito_foto'] as String)],
            ),
        ],
      ),
    );
  }
}

class OrderScreen extends StatelessWidget {
  const OrderScreen({
    super.key,
    required this.row,
    required this.api,
    required this.session,
  });
  final Map<String, dynamic> row;
  final ApiClient api;
  final Session session;
  @override
  Widget build(BuildContext context) => SessionActionGate(
    session: session,
    title: 'Preparar pedido',
    message: 'Inicia sesión para preparar tu pedido.',
    form: (identity) =>
        _OrderForm(key: identity, row: row, api: api, session: session),
  );
}

class _OrderForm extends StatefulWidget {
  const _OrderForm({
    super.key,
    required this.row,
    required this.api,
    required this.session,
  });
  final Map<String, dynamic> row;
  final ApiClient api;
  final Session session;
  @override
  State<_OrderForm> createState() => _OrderFormState();
}

class _OrderFormState extends State<_OrderForm> {
  int _quantity = 1;
  bool _busy = false, _uncertain = false;
  int? _order;
  CopAmount? _serverTotal;
  int get _stock => productStock(widget.row) ?? 0;
  CopAmount? get _price => CopAmount.parse(widget.row['precio']);
  String? _error;
  Future<void> _send() async {
    if (_busy ||
        _uncertain ||
        _order != null ||
        _quantity > _stock ||
        _price == null) {
      return;
    }
    if (!widget.session.signedIn) return;
    if (!mounted) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final response = await widget.session.authorized(
        (token) => widget.api.post('/api/pedidos/', {
          'id_tienda': widget.row['id_tienda'],
          'lineas': [
            {'id_producto': widget.row['id_producto'], 'cantidad': _quantity},
          ],
        }, token: token),
      );
      if (response is! Map ||
          response['id_pedido'] is! int ||
          response['cobrado'] != false) {
        throw const ApiException('No pudimos confirmar el pedido.');
      }
      if (mounted) {
        setState(() {
          _order = response['id_pedido'] as int;
          _serverTotal = CopAmount.parse(response['total_referencial']);
        });
      }
    } on Exception catch (e) {
      if (mounted) {
        setState(() {
          _uncertain =
              e is! ApiException || e.status == null || e.status! >= 500;
          _error = _uncertain
              ? 'No pudimos confirmar si se inició el pedido. Evita repetirlo; consulta con la tienda. No se ha procesado un pago.'
              : messageFor(e, 'No pudimos iniciar el pedido.');
        });
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Preparar pedido'),
    bottomNavigationBar: _order == null
        ? LpnKeyboardSafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: FilledButton(
                onPressed:
                    _busy || _uncertain || _stock < _quantity || _price == null
                    ? null
                    : _send,
                child: Text(_busy ? 'Iniciando…' : 'Iniciar pedido sin pago'),
              ),
            ),
          )
        : null,
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        LpnFormSection(
          title: 'Resumen del pedido',
          icon: Icons.shopping_bag_outlined,
          tone: 2,
          children: [
            Text(
              '${widget.row['nombre']}',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            Text(
              'Precio unitario de referencia: ${_price?.formatted ?? 'No disponible'}',
            ),
            const SizedBox(height: 16),
            const Text(
              'La tienda valida disponibilidad y precio al iniciar el pedido. Este proceso no cobra dinero.',
            ),
            const SizedBox(height: 24),
            if (_serverTotal != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Text(
                  'Total de referencia guardado: ${_serverTotal!.formatted}',
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            if (_order != null)
              StatusPanel(
                message: 'Pedido #$_order iniciado. No se ha cobrado dinero.',
              )
            else ...[
              if (_price != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Text(
                    'Total de referencia: ${_price!.times(_quantity).formatted}',
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              if (_stock == 0)
                const Text(
                  'Sin existencias disponibles para iniciar un pedido.',
                ),
              Wrap(
                crossAxisAlignment: WrapCrossAlignment.center,
                spacing: 12,
                children: [
                  IconButton(
                    tooltip: 'Reducir cantidad',
                    onPressed: !_busy && !_uncertain && _quantity > 1
                        ? () => setState(() => _quantity--)
                        : null,
                    icon: const Icon(Icons.remove_circle_outline),
                  ),
                  Semantics(
                    liveRegion: true,
                    child: Text('Cantidad: $_quantity'),
                  ),
                  IconButton(
                    tooltip: 'Aumentar cantidad',
                    onPressed: !_busy && !_uncertain && _quantity < _stock
                        ? () => setState(() => _quantity++)
                        : null,
                    icon: const Icon(Icons.add_circle_outline),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              if (_error != null)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Text(
                    _error!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ),
            ],
          ],
        ),
      ],
    ),
  );
}

class ContributionScreen extends StatelessWidget {
  const ContributionScreen({
    super.key,
    required this.row,
    required this.api,
    required this.session,
  });
  final Map<String, dynamic> row;
  final ApiClient api;
  final Session session;
  @override
  Widget build(BuildContext context) => SessionActionGate(
    session: session,
    title: 'Ofrecer un aporte',
    message: 'Inicia sesión para registrar tu compromiso de aporte.',
    form: (identity) =>
        _ContributionForm(key: identity, row: row, api: api, session: session),
  );
}

class _ContributionForm extends StatefulWidget {
  const _ContributionForm({
    super.key,
    required this.row,
    required this.api,
    required this.session,
  });
  final Map<String, dynamic> row;
  final ApiClient api;
  final Session session;
  @override
  State<_ContributionForm> createState() => _ContributionFormState();
}

class _ContributionFormState extends State<_ContributionForm> {
  final _amount = TextEditingController();
  bool _busy = false,
      _sent = false,
      _uncertain = false,
      _leaving = false,
      _confirming = false;
  String? _error;
  @override
  void dispose() {
    _amount.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    if (_busy || _sent || _uncertain) return;
    if (!widget.session.signedIn) return;
    if (!mounted) return;
    final amount = _amount.text.trim().replaceAll(',', '.');
    if (!RegExp(r'^\d{1,10}(\.\d{1,2})?$').hasMatch(amount) ||
        (double.tryParse(amount) ?? 0) <= 0) {
      setState(
        () => _error = 'Escribe un monto positivo con hasta dos decimales.',
      );
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final result = await widget.session.authorized(
        (token) => widget.api.post('/api/fondos/donaciones/', {
          'id_fondo_externo': widget.row['id_fondo_externo'],
          'monto_comprometido': amount,
        }, token: token),
      );
      if (result is! Map ||
          result['id_donacion'] is! int ||
          result['dinero_recibido'] != false) {
        throw const ApiException(
          'No pudimos confirmar el compromiso. No se procesó ningún pago.',
        );
      }
      if (mounted) setState(() => _sent = true);
    } on Exception catch (e) {
      if (mounted) {
        setState(() {
          _uncertain =
              e is! ApiException || e.status == null || e.status! >= 500;
          _error = _uncertain
              ? 'No pudimos confirmar el resultado. Evita repetir el compromiso; consulta con la organización. No se procesó ningún pago.'
              : messageFor(e, 'No pudimos registrar el compromiso.');
        });
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _cancel() async {
    if (_busy || _confirming) return;
    if (!_sent && _amount.text.trim().isNotEmpty) {
      _confirming = true;
      final leave = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          scrollable: true,
          title: const Text('¿Salir del compromiso?'),
          content: Text(
            _uncertain
                ? 'El compromiso podría haberse registrado. Salir no lo revierte; consulta con la organización antes de repetirlo. No se ha procesado ningún pago.'
                : 'Se descartará el monto que escribiste. No se ha procesado ningún pago.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Seguir aquí'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Salir'),
            ),
          ],
        ),
      );
      _confirming = false;
      if (leave != true || !mounted) return;
    }
    setState(() => _leaving = true);
    await WidgetsBinding.instance.endOfFrame;
    if (mounted) Navigator.pop(context, _sent);
  }

  @override
  Widget build(BuildContext context) => PopScope(
    canPop: _leaving,
    onPopInvokedWithResult: (didPop, _) {
      if (!didPop) _cancel();
    },
    child: Scaffold(
      appBar: lpnAppBar(context, 'Ofrecer un aporte'),
      bottomNavigationBar: LpnKeyboardSafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Wrap(
            alignment: WrapAlignment.end,
            spacing: 12,
            runSpacing: 8,
            children: [
              TextButton(
                onPressed: _busy ? null : _cancel,
                child: Text(_sent ? 'Volver' : 'Cancelar'),
              ),
              if (!_sent)
                FilledButton(
                  onPressed: _busy || _uncertain ? null : _send,
                  child: Text(_busy ? 'Registrando…' : 'Registrar compromiso'),
                ),
            ],
          ),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          BankInstructions(
            session: widget.session,
            path: '/api/fondos/${widget.row['id_fondo_externo']}/datos-aporte/',
          ),
          const SizedBox(height: 20),
          Text(
            '${widget.row['nombre']}',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          const SizedBox(height: 16),
          const Text(
            'Solo se registra tu intención de aportar. No se cobra dinero ni se confirma una transferencia.',
          ),
          const SizedBox(height: 24),
          if (_sent)
            const StatusPanel(
              message:
                  'Compromiso registrado. No se ha recibido ni cobrado dinero.',
            )
          else
            FormCard(
              title: 'Tu compromiso',
              icon: Icons.savings_outlined,
              tone: 2,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'Elige un monto o escribe otro',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 12),
                  DraftSuggestions(
                    values: const [
                      r'$10.000 COP',
                      r'$20.000 COP',
                      r'$50.000 COP',
                    ],
                    enabled: !_busy && !_uncertain && !_sent,
                    onSelected: (value) => setState(
                      () => _amount.text = value.replaceAll(
                        RegExp(r'[^0-9]'),
                        '',
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _amount,
                    enabled: !_busy && !_uncertain,
                    keyboardType: const TextInputType.numberWithOptions(
                      decimal: true,
                    ),
                    decoration: const InputDecoration(
                      labelText: 'Monto comprometido (COP)',
                    ),
                  ),
                  const SizedBox(height: 20),
                  if (_error != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 16),
                      child: Text(
                        _error!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                        ),
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
