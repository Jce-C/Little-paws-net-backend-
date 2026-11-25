import '../rescue/my_sponsorships_screen.dart';
import '../pets/personal_pet_screen.dart';
import '../explore/help_management.dart';

import 'package:flutter/material.dart';

import '../adoption/adoption_screens.dart' show messageFor;
import '../design/lpn_theme.dart';
import '../pets/owned_pets_api.dart';
import '../pets/owned_pets_screens.dart';
import '../pets/profile_pet_preview.dart';
import 'account_access.dart';
import 'profile_screen.dart';
import 'session.dart';

class AccountOverview extends StatefulWidget {
  const AccountOverview({
    super.key,
    required this.session,
    required this.account,
  });
  final Session session;
  final Account account;
  @override
  State<AccountOverview> createState() => _AccountOverviewState();
}

class _AccountOverviewState extends State<AccountOverview> {
  int _petRevision = 0;
  late Future<List<AssignedRole>> _roles = AccountAccess(widget.session).load();
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _observe(_roles);
  }

  Future<void> _observe(Future<List<AssignedRole>> current) async {
    try {
      await current;
    } on Exception {
      /* FutureBuilder offers explicit retry. */
    }
    if (mounted && identical(_roles, current)) setState(() => _loading = false);
  }

  void _reload() {
    if (_loading) return;
    final next = AccountAccess(widget.session).load();
    setState(() {
      _roles = next;
      _loading = true;
    });
    _observe(next);
  }

  @override
  Widget build(BuildContext context) {
    final account = widget.account;
    final solid =
        MediaQuery.highContrastOf(context) ||
        (Theme.of(context).extension<LpnMaterials>()?.reduceTransparency ??
            false);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          constraints: const BoxConstraints(minHeight: 83),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: solid
                ? LpnColors.paper
                : Color.alphaBlend(const Color(0x80fcf0d3), LpnColors.canvas),
            borderRadius: BorderRadius.circular(28),
            border: Border.all(color: LpnColors.line),
            boxShadow: solid
                ? null
                : const [
                    BoxShadow(
                      color: Color(0x14423222),
                      offset: Offset(0, 4),
                      blurRadius: 10,
                      spreadRadius: 3,
                    ),
                  ],
          ),
          child: Row(
            children: [
              CircleAvatar(
                radius: 27,
                backgroundColor: LpnColors.butter,
                foregroundColor: LpnColors.ink,
                child: Text(
                  account.name.trim().isEmpty
                      ? '?'
                      : account.name.trim().characters.first.toUpperCase(),
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      account.name,
                      style: const TextStyle(
                        fontSize: 18,
                        height: 1.3,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    Text(
                      account.email,
                      style: const TextStyle(fontSize: 14, height: 1.5),
                    ),
                    if (account.phone.isNotEmpty)
                      Text(
                        account.phone,
                        style: const TextStyle(fontSize: 14, height: 1.5),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
        Align(
          alignment: Alignment.centerRight,
          child: TextButton.icon(
            onPressed: () {
              ScaffoldMessenger.of(context).removeCurrentSnackBar();
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => ProfileScreen(session: widget.session),
                ),
              );
            },
            icon: const Icon(Icons.edit_outlined, size: 16),
            label: const Text('Editar perfil', style: TextStyle(fontSize: 14)),
          ),
        ),
        const SizedBox(height: 24),
        const Text('Mis mascotas', style: TextStyle(fontSize: 15, height: 1.4)),
        const SizedBox(height: 10),
        ProfilePetPreview(
          key: ValueKey(_petRevision),
          api: OwnedPetsApi(widget.session.api, widget.session),
        ),
        const SizedBox(height: 12),
        Center(
          child: FilledButton.icon(
            onPressed: () async {
              await Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => OwnedPetsScreen(
                    api: OwnedPetsApi(widget.session.api, widget.session),
                  ),
                ),
              );
              if (mounted) setState(() => _petRevision++);
            },
            icon: const Icon(Icons.pets_outlined, size: 18),
            label: const Text('Mis mascotas', style: TextStyle(fontSize: 14)),
          ),
        ),
        OutlinedButton.icon(
          onPressed: () async {
            if (await openPersonalPet(context, widget.session) && mounted) {
              setState(() => _petRevision++);
            }
          },
          icon: const Icon(Icons.add),
          label: const Text('Agregar mascota'),
        ),
        TextButton.icon(
          onPressed: () => Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => MySponsorshipsScreen(session: widget.session),
            ),
          ),
          icon: const Icon(Icons.volunteer_activism_outlined),
          label: const Text('Mis compromisos'),
        ),
        HelpManagementShortcut(
          api: widget.session.api,
          session: widget.session,
        ),
        const Divider(height: 32),
        const SizedBox(height: 12),
        Row(
          children: [
            const Expanded(
              child: Text(
                'Mis roles',
                style: TextStyle(fontSize: 15, height: 1.4),
              ),
            ),
            IconButton(
              tooltip: 'Actualizar mis roles',
              onPressed: _loading ? null : _reload,
              icon: const Icon(Icons.refresh, size: 20),
            ),
          ],
        ),
        const Text(
          'Estos son tus roles y las organizaciones donde se aplican. Tus permisos se comprueban al realizar cada acción.',
          style: TextStyle(fontSize: 14, height: 1.5),
        ),
        const SizedBox(height: 8),
        FutureBuilder<List<AssignedRole>>(
          future: _roles,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Padding(
                padding: EdgeInsets.all(16),
                child: Center(
                  child: CircularProgressIndicator(
                    semanticsLabel: 'Consultando tus roles',
                  ),
                ),
              );
            }
            if (snapshot.hasError) {
              return Semantics(
                liveRegion: true,
                child: Text(
                  messageFor(
                    snapshot.error,
                    'No pudimos consultar tus roles. Usa actualizar para reintentar.',
                  ),
                  style: TextStyle(
                    fontSize: 14,
                    color: Theme.of(context).colorScheme.error,
                  ),
                ),
              );
            }
            final roles = snapshot.data!;
            if (roles.isEmpty) {
              return const Text(
                'No hay roles vigentes asignados.',
                style: TextStyle(fontSize: 14),
              );
            }
            return Column(
              children: [
                for (final role in roles)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                role.code,
                                style: const TextStyle(
                                  fontSize: 14,
                                  height: 1.4,
                                ),
                              ),
                              Text(
                                role.context,
                                style: const TextStyle(
                                  fontSize: 14,
                                  height: 1.4,
                                  color: LpnColors.muted,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 10),
                        const Tooltip(
                          message: 'Asignación de solo lectura',
                          child: Icon(
                            Icons.lock_outline,
                            size: 16,
                            color: LpnColors.muted,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            );
          },
        ),
        const SizedBox(height: 24),
        Center(
          child: TextButton(
            onPressed: widget.session.logout,
            child: const Text(
              'Cerrar sesión',
              style: TextStyle(fontSize: 14, color: LpnColors.ink),
            ),
          ),
        ),
      ],
    );
  }
}
