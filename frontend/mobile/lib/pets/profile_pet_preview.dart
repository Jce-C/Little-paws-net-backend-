import 'package:flutter/material.dart';

import '../adoption/adoption_screens.dart' show messageFor;
import 'owned_pets_api.dart';
import 'owned_pets_screens.dart';
import 'personal_pet_screen.dart';

/// Figma 156:1796: actual owned pets appear in the profile, not a fake Bruno.
class ProfilePetPreview extends StatefulWidget {
  const ProfilePetPreview({super.key, required this.api});
  final OwnedPetsApi api;
  @override
  State<ProfilePetPreview> createState() => _ProfilePetPreviewState();
}

class _ProfilePetPreviewState extends State<ProfilePetPreview> {
  late Future<List<OwnedPet>> _pets = widget.api
      .page(limit: 3)
      .then((page) => page.rows);
  @override
  Widget build(BuildContext context) => FutureBuilder<List<OwnedPet>>(
    future: _pets,
    builder: (context, snapshot) {
      if (snapshot.connectionState != ConnectionState.done) {
        return const LinearProgressIndicator(
          semanticsLabel: 'Cargando tus mascotas',
        );
      }
      if (snapshot.hasError) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              messageFor(snapshot.error, 'No pudimos consultar tus mascotas.'),
              style: const TextStyle(fontSize: 14),
            ),
            TextButton(
              onPressed: () {
                final next = widget.api
                    .page(limit: 3)
                    .then((page) => page.rows);
                setState(() {
                  _pets = next;
                });
              },
              child: const Text('Reintentar mascotas'),
            ),
          ],
        );
      }
      final pets = snapshot.data!;
      if (pets.isEmpty) {
        return const Text(
          'Todavía no tienes mascotas asociadas a tu cuenta.',
          style: TextStyle(fontSize: 14),
        );
      }
      return Column(
        children: [
          for (final owned in pets.take(3))
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Row(
                      children: [
                        if (medicalPhoto(owned.personal?['foto_miniatura'])
                            case final bytes?)
                          ClipRRect(
                            borderRadius: BorderRadius.circular(12),
                            child: Image.memory(
                              bytes,
                              width: 54,
                              height: 54,
                              fit: BoxFit.cover,
                              semanticLabel: 'Fotografía privada de tu mascota',
                            ),
                          )
                        else
                          const SizedBox(
                            width: 54,
                            height: 54,
                            child: Icon(Icons.pets_outlined, size: 30),
                          ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                owned.pet.name,
                                style: const TextStyle(
                                  fontSize: 18,
                                  height: 1.3,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              Text(
                                owned.pet.summary,
                                style: const TextStyle(fontSize: 14),
                              ),
                              Text(
                                owned.status,
                                style: const TextStyle(fontSize: 14),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    if (owned.personal != null || !owned.activeCustody)
                      TextButton(
                        onPressed: () => Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => owned.personal != null
                                ? PersonalPetDetailsScreen(
                                    session: widget.api.session,
                                    id: owned.pet.id,
                                  )
                                : PetMedicalRecordScreen(
                                    api: widget.api,
                                    petId: owned.pet.id,
                                  ),
                          ),
                        ),
                        child: Text(
                          owned.personal != null
                              ? 'Ver ficha'
                              : 'Ver expediente',
                          style: TextStyle(fontSize: 14),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          if (pets.length > 3)
            Text(
              'Mostrando 3 mascotas de esta página',
              style: const TextStyle(fontSize: 14),
            ),
        ],
      );
    },
  );
}
