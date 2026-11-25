import 'dart:async';

import 'package:flutter/foundation.dart';

import '../core/api_client.dart';
import 'rescue_api.dart';

/// Public reads only. A new search invalidates any response already in flight.
class PublicReportsController extends ChangeNotifier {
  PublicReportsController(this.api);
  final RescueApi api;
  List<AnimalReport> reports = const [];
  String query = '';
  String? nextCursor;
  Object? error;
  Object? pageError;
  bool loading = false;
  bool loadingMore = false;
  bool _disposed = false;
  int _generation = 0;
  Timer? _searchTimer;
  final _cursors = <String>{};

  void search(String value) {
    final next = value.trim();
    if (_disposed || next == query) return;
    query = next;
    _generation++;
    _searchTimer?.cancel();
    _reset();
    _notify();
    _searchTimer = Timer(const Duration(milliseconds: 400), reload);
  }

  void _reset() {
    reports = const [];
    nextCursor = null;
    error = null;
    pageError = null;
    loading = true;
    loadingMore = false;
    _cursors.clear();
  }

  Future<void> reload() async {
    if (_disposed) return;
    _searchTimer?.cancel();
    final generation = ++_generation;
    _reset();
    _notify();
    try {
      final page = await api.publicReportPage(query: query);
      if (!_current(generation)) return;
      reports = page.reports;
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
      final page = await api.publicReportPage(query: query, cursor: cursor);
      if (!_current(generation)) return;
      if (page.nextCursor != null &&
          (page.nextCursor == cursor || _cursors.contains(page.nextCursor))) {
        throw const ApiException(
          'No pudimos continuar. Actualiza los reportes.',
        );
      }
      final ids = reports.map((r) => r.id).toSet();
      reports = [...reports, ...page.reports.where((r) => ids.add(r.id))];
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
    _searchTimer?.cancel();
    super.dispose();
  }
}
