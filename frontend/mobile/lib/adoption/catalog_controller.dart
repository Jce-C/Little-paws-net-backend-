import 'package:flutter/foundation.dart';

import '../core/api_client.dart';
import 'adoption_api.dart';

class CatalogController extends ChangeNotifier {
  CatalogController(this.api);
  final AdoptionApi api;
  List<Pet> pets = const [];
  List<String> species = const [];
  String selectedSpecies = '';
  String? nextCursor;
  Object? error;
  Object? pageError;
  bool loading = false;
  bool loadingMore = false;
  bool _disposed = false;
  int _generation = 0;
  final Set<String> _cursors = {};

  Future<void> reload({String? species}) async {
    if (_disposed) return;
    final generation = ++_generation;
    if (species != null) selectedSpecies = species;
    pets = const [];
    nextCursor = null;
    error = null;
    pageError = null;
    loading = true;
    loadingMore = false;
    _cursors.clear();
    _notify();
    try {
      final page = await api.catalogPage(species: selectedSpecies);
      if (!_current(generation)) return;
      pets = page.pets;
      this.species = page.species;
      nextCursor = page.nextCursor;
    } on Exception catch (failure) {
      if (_current(generation)) error = failure;
    } finally {
      if (_current(generation)) {
        loading = false;
        _notify();
      }
    }
  }

  Future<void> loadMore() async {
    final cursor = nextCursor;
    if (_disposed || loading || loadingMore || cursor == null) return;
    final generation = _generation;
    loadingMore = true;
    pageError = null;
    _notify();
    try {
      final page = await api.catalogPage(
        cursor: cursor,
        species: selectedSpecies,
      );
      if (!_current(generation)) return;
      if (page.nextCursor != null && _cursors.contains(page.nextCursor)) {
        throw const ApiException(
          'No pudimos continuar. Actualiza el catálogo.',
        );
      }
      final ids = pets.map((pet) => pet.id).toSet();
      pets = [...pets, ...page.pets.where((pet) => ids.add(pet.id))];
      species = page.species;
      nextCursor = page.nextCursor;
      _cursors.add(cursor);
    } on Exception catch (failure) {
      if (_current(generation)) pageError = failure;
    } finally {
      if (_current(generation)) {
        loadingMore = false;
        _notify();
      }
    }
  }

  bool _current(int generation) => !_disposed && generation == _generation;
  void _notify() {
    if (!_disposed) notifyListeners();
  }

  @override
  void dispose() {
    _disposed = true;
    _generation++;
    super.dispose();
  }
}
