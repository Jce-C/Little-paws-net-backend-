import '../design/readable_text.dart';
import 'personal_pet_screen.dart';
import '../design/lpn_app_bar.dart';

import 'package:flutter/material.dart';

import '../adoption/adoption_screens.dart' show StatusPanel, messageFor;
import '../auth/account_screen.dart';
import 'owned_pets_api.dart';
import 'pet_qr_screen.dart';

class OwnedPetsScreen extends StatelessWidget {
  const OwnedPetsScreen({super.key, required this.api});
  final OwnedPetsApi api;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Mis mascotas'),
    body: ListenableBuilder(
      listenable: api.session,
      builder: (context, _) {
        if (api.session.restoring) {
          return const Center(child: CircularProgressIndicator());
        }
        if (!api.session.signedIn) return _signIn(context, api);
        return _OwnedList(
          key: ValueKey((
            api.session.identityRevision,
            api.session.account!.email,
          )),
          api: api,
        );
      },
    ),
  );
}

class _OwnedList extends StatefulWidget {
  const _OwnedList({super.key, required this.api});
  final OwnedPetsApi api;
  @override
  State<_OwnedList> createState() => _OwnedListState();
}

class _OwnedListState extends State<_OwnedList> {
  Future<List<OwnedPet>>? _pending;
  String? _next;
  bool _loadingMore = false;
  int _generation = 0;
  String? _pageError;
  late Future<List<OwnedPet>> _pets = _fetch();

  Future<List<OwnedPet>> _fetch() => _pending ??= widget.api
      .page()
      .then((page) {
        _next = page.next;
        return page.rows;
      })
      .whenComplete(() => _pending = null);

  Future<void> _more() async {
    if (_loadingMore || _next == null) return;
    final generation = _generation;
    final before = _next!;
    setState(() {
      _loadingMore = true;
      _pageError = null;
    });
    try {
      final current = await _pets;
      final page = await widget.api.page(before: before);
      if (mounted && generation == _generation) {
        setState(() {
          _next = page.next;
          _pets = Future.value([
            ...current,
            ...page.rows.where(
              (row) => !current.any((old) => old.pet.id == row.pet.id),
            ),
          ]);
        });
      }
    } on Exception catch (error) {
      if (mounted && generation == _generation) {
        setState(
          () =>
              _pageError = messageFor(error, 'No pudimos cargar más mascotas.'),
        );
      }
    } finally {
      if (mounted && generation == _generation) {
        setState(() => _loadingMore = false);
      }
    }
  }

  Future<void> _reload() async {
    _generation++;
    _loadingMore = false;
    _pageError = null;
    final next = _fetch();
    setState(() {
      _pets = next;
    });
    try {
      await next;
    } on Exception {
      /* The view offers retry. */
    }
  }

  @override
  Widget build(BuildContext context) => RefreshIndicator(
    onRefresh: _reload,
    child: FutureBuilder<List<OwnedPet>>(
      future: _pets,
      builder: (context, snapshot) => ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(20),
        children: [
          const Text(
            'Fichas asociadas a tu cuenta, incluidas las mascotas cuya adopción ya fue aprobada.',
          ),
          Align(
            alignment: Alignment.centerRight,
            child: IconButton(
              tooltip: 'Actualizar mis mascotas',
              onPressed: snapshot.connectionState == ConnectionState.done
                  ? _reload
                  : null,
              icon: const Icon(Icons.refresh),
            ),
          ),
          if (snapshot.connectionState != ConnectionState.done)
            const Center(
              child: CircularProgressIndicator(
                semanticsLabel: 'Cargando tus mascotas',
              ),
            )
          else if (snapshot.hasError)
            StatusPanel(
              message: messageFor(
                snapshot.error,
                'No pudimos consultar tus mascotas.',
              ),
              action: _reload,
              actionLabel: 'Reintentar',
            )
          else if (snapshot.data!.isEmpty)
            const StatusPanel(
              message: 'Todavía no hay mascotas asociadas a tu cuenta. Cuando se apruebe una adopción aparecerá aquí.',
            )
          else
            for (final owned in snapshot.data!)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.pets_outlined),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              owned.pet.name,
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      if (owned.personal?['foto_miniatura'] case final value?)
                        if (medicalPhoto(value) case final bytes?)
                          Padding(
                            padding: const EdgeInsets.only(bottom: 12),
                            child: ClipRRect(
                              borderRadius: BorderRadius.circular(18),
                              child: Image.memory(
                                bytes,
                                height: 120,
                                fit: BoxFit.cover,
                                semanticLabel:
                                    'Foto privada de ${owned.pet.name}',
                              ),
                            ),
                          ),
                      Text(owned.pet.summary),
                      if (owned.personal != null)
                        TextButton.icon(
                          onPressed: () => Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => PersonalPetDetailsScreen(
                                session: widget.api.session,
                                id: owned.pet.id,
                              ),
                            ),
                          ),
                          icon: const Icon(Icons.pets_outlined),
                          label: const Text('Ver ficha'),
                        ),

                      Text('Estado: ${owned.status}'),
                      if (owned.activeCustody) ...[
                        const SizedBox(height: 12),
                        const Text(
                          'Esta ficha tiene una custodia vigente. La organización debe revisar la titularidad antes de acceder al expediente.',
                        ),
                      ] else
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton.icon(
                            key: Key('pet-record-${owned.pet.id}'),
                            onPressed: () => Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => PetMedicalRecordScreen(
                                  api: widget.api,
                                  petId: owned.pet.id,
                                ),
                              ),
                            ),
                            icon: const Icon(
                              Icons.medical_information_outlined,
                            ),
                            label: Text(
                              owned.personal != null
                                  ? 'Salud y QR'
                                  : 'Ver expediente',
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
          if (_pageError != null) Text(_pageError!),
          if (_next != null)
            TextButton(
              onPressed: _loadingMore ? null : _more,
              child: Text(_loadingMore ? 'Cargando…' : 'Ver más mascotas'),
            ),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () async {
              if (await openPersonalPet(context, widget.api.session) &&
                  mounted) {
                await _reload();
              }
            },
            icon: const Icon(Icons.add),
            label: const Text('Agregar mascota'),
          ),
        ],
      ),
    ),
  );
}

class PetMedicalRecordScreen extends StatelessWidget {
  const PetMedicalRecordScreen({
    super.key,
    required this.api,
    required this.petId,
  });
  final OwnedPetsApi api;
  final int petId;
  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: lpnAppBar(context, 'Expediente privado'),
    body: ListenableBuilder(
      listenable: api.session,
      builder: (context, _) {
        if (api.session.restoring) {
          return const Center(child: CircularProgressIndicator());
        }
        if (!api.session.signedIn) return _signIn(context, api);
        return _MedicalBody(
          key: ValueKey((
            api.session.identityRevision,
            api.session.account!.email,
            petId,
          )),
          api: api,
          petId: petId,
        );
      },
    ),
  );
}

class _MedicalBody extends StatefulWidget {
  const _MedicalBody({super.key, required this.api, required this.petId});
  final OwnedPetsApi api;
  final int petId;
  @override
  State<_MedicalBody> createState() => _MedicalBodyState();
}

class _MedicalBodyState extends State<_MedicalBody> {
  Future<PetMedicalRecord>? _pending;
  late Future<PetMedicalRecord> _record = _fetch();

  Future<PetMedicalRecord> _fetch() => _pending ??= widget.api
      .record(widget.petId)
      .whenComplete(() => _pending = null);

  Future<void> _reload() async {
    final next = _fetch();
    setState(() {
      _record = next;
    });
    try {
      await next;
    } on Exception {
      /* The view offers retry. */
    }
  }

  @override
  Widget build(BuildContext context) => RefreshIndicator(
    onRefresh: _reload,
    child: FutureBuilder<PetMedicalRecord>(
      future: _record,
      builder: (context, snapshot) => ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(20),
        children: [
          Row(
            children: [
              const Icon(Icons.lock_outline),
              const SizedBox(width: 8),
              const Expanded(child: Text('Información privada de la mascota')),
              IconButton(
                tooltip: 'Actualizar expediente',
                onPressed: snapshot.connectionState == ConnectionState.done
                    ? _reload
                    : null,
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (snapshot.connectionState != ConnectionState.done)
            const Center(
              child: CircularProgressIndicator(
                semanticsLabel: 'Cargando expediente',
              ),
            )
          else if (snapshot.hasError)
            StatusPanel(
              message: messageFor(
                snapshot.error,
                'No pudimos consultar el expediente.',
              ),
              action: _reload,
              actionLabel: 'Reintentar',
            )
          else ...[
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary
                    .withValues(alpha: .08),
                borderRadius: BorderRadius.circular(28),
              ),
              child: LayoutBuilder(
                builder: (context, box) {
                  final portrait = snapshot.data!.photo != null
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(20),
                          child: Image.memory(
                            snapshot.data!.photo!,
                            width: 88,
                            height: 88,
                            fit: BoxFit.cover,
                            semanticLabel: 'Retrato de ${snapshot.data!.name}',
                            errorBuilder: (_, error, stack) =>
                                const Icon(Icons.pets_outlined, size: 48),
                          ),
                        )
                      : const Icon(Icons.pets_outlined, size: 48);
                  final information = Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'EXPEDIENTE PROTEGIDO',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          letterSpacing: .8,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        snapshot.data!.name,
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '${snapshot.data!.entries.length} ${snapshot.data!.entries.length == 1 ? 'atención' : 'atenciones'} en esta consulta',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  );
                  final stacked =
                      box.maxWidth < 280 ||
                      MediaQuery.textScalerOf(context).scale(16) > 24;
                  return stacked
                      ? Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            portrait,
                            const SizedBox(height: 16),
                            information,
                          ],
                        )
                      : Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            portrait,
                            const SizedBox(width: 16),
                            Expanded(child: information),
                          ],
                        );
                },
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Últimas 50 atenciones. Las correcciones conservan el registro original.',
            ),
            const SizedBox(height: 16),
            TextButton.icon(
              onPressed: () => Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) =>
                      PetQrScreen(api: widget.api, petId: widget.petId),
                ),
              ),
              icon: const Icon(Icons.qr_code_2),
              label: const Text('QR de identificación'),
            ),
            const SizedBox(height: 16),
            if (snapshot.data!.entries.isEmpty)
              const StatusPanel(
                message: 'Todavía no hay atenciones médicas registradas para esta mascota.',
              )
            else
              for (final entry in snapshot.data!.entries)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          'Atención #${entry.id}',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        Text(
                          MaterialLocalizations.of(context)
                              .formatMediumDate(entry.date.toLocal()),
                        ),
                        const SizedBox(height: 8),
                        ReadableText(
                          entry.detail,
                          style: const TextStyle(height: 1.5),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Registrado por: ${entry.author}',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        for (final amendment in entry.amendments) ...[
                          const Divider(height: 24),
                          const Text(
                            'Corrección registrada',
                            style: TextStyle(fontWeight: FontWeight.w700),
                          ),
                          Text(
                            MaterialLocalizations.of(context)
                                .formatMediumDate(amendment.date.toLocal()),
                          ),
                          Text(amendment.detail),
                          Text('Motivo: ${amendment.reason}'),
                        ],
                      ],
                    ),
                  ),
                ),
          ],
        ],
      ),
    ),
  );
}

Widget _signIn(BuildContext context, OwnedPetsApi api) => SingleChildScrollView(
  child: StatusPanel(
    message: 'Inicia sesión para consultar las mascotas y expedientes asociados a tu cuenta.',
    action: () => openLogin(context, api.session),
    actionLabel: 'Iniciar sesión',
  ),
);
