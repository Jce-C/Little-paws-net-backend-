import 'package:flutter/material.dart';

import '../core/api_client.dart';
import '../design/lpn_app_bar.dart';
import '../design/refined_surfaces.dart';

class ProductCatalogScreen extends StatefulWidget {
  const ProductCatalogScreen({
    super.key,
    required this.api,
    required this.onOpen,
  });
  final ApiClient api;
  final ValueChanged<Map<String, dynamic>> onOpen;
  @override
  State<ProductCatalogScreen> createState() => _ProductCatalogScreenState();
}

class _ProductCatalogScreenState extends State<ProductCatalogScreen> {
  final _search = TextEditingController();
  final _scroll = ScrollController();
  List<Map<String, dynamic>> _rows = [];
  List<String> _categories = [];
  String _query = '', _category = '';
  String? _next, _error;
  bool _loading = false, _legacy = false;
  int _generation = 0;
  @override
  void initState() {
    super.initState();
    _fetch();
  }

  @override
  void dispose() {
    _search.dispose();
    _scroll.dispose();
    super.dispose();
  }

  Future<void> _fetch({bool more = false}) async {
    if (more && (_loading || _next == null)) return;
    final generation = more ? _generation : ++_generation;
    final cursor = more ? _next : null;
    setState(() {
      _loading = true;
      _error = null;
      if (!more) {
        _rows = [];
        _next = null;
      }
    });
    try {
      final path = Uri(
        path: '/api/catalogo/productos/',
        queryParameters: {
          'paginado': '1',
          'limite': '20',
          'despues': ?cursor,
          if (_query.isNotEmpty) 'buscar': _query,
          if (_category.isNotEmpty) 'categoria': _category,
        },
      ).toString();
      final value = await widget.api.get(path);
      if (!mounted || generation != _generation) return;
      final legacy = value is List;
      final Object? raw = legacy
          ? value
          : value is Map
          ? value['results']
          : null;
      if (raw is! List ||
          raw.length > (legacy ? 100 : 50) ||
          raw.any(
            (v) =>
                v is! Map<String, dynamic> ||
                v['id_producto'] is! int ||
                (v['id_producto'] as int) < 1 ||
                v['nombre'] is! String,
          )) {
        throw const ApiException('No pudimos interpretar el catálogo.');
      }
      final rows = raw.cast<Map<String, dynamic>>();
      final Object? next = legacy ? null : (value as Map)['next_cursor'];
      var previous = cursor == null ? 0 : int.parse(cursor);
      for (final row in rows) {
        final id = row['id_producto'] as int;
        if (id <= previous) {
          throw const ApiException('La página del catálogo no es válida.');
        }
        previous = id;
      }
      if (next != null &&
          (next is! String ||
              !RegExp(r'^[1-9][0-9]{0,18}$').hasMatch(next) ||
              rows.isEmpty ||
              next != '${rows.last['id_producto']}')) {
        throw const ApiException('La página siguiente no es válida.');
      }
      List<String>? categories;
      if (cursor == null) {
        final Object? rawCategories = legacy
            ? rows
                  .map((r) => r['categoria'])
                  .whereType<String>()
                  .toSet()
                  .toList()
            : (value as Map)['categorias'];
        if (rawCategories is! List ||
            rawCategories.length > 100 ||
            rawCategories.any((v) => v is! String)) {
          throw const ApiException('No pudimos interpretar las categorías.');
        }
        categories = rawCategories.cast<String>().toSet().toList()..sort();
      }
      setState(() {
        _rows = more ? [..._rows, ...rows] : rows;
        _next = next as String?;
        _legacy = legacy;
        if (categories != null) _categories = categories;
      });
    } on Exception {
      if (mounted && generation == _generation) {
        setState(
          () => _error = more
              ? 'No pudimos cargar más productos. Puedes reintentar.'
              : 'No pudimos consultar los productos.',
        );
      }
    } finally {
      if (mounted && generation == _generation) {
        setState(() => _loading = false);
      }
    }
  }

  void _apply() {
    _query = _search.text.trim();
    if (_legacy) {
      setState(() {});
    } else {
      _fetch();
    }
  }

  @override
  Widget build(BuildContext context) {
    final visible = _legacy
        ? _rows
              .where(
                (r) =>
                    (_category.isEmpty || r['categoria'] == _category) &&
                    '${r['nombre']} ${r['tienda'] ?? ''}'
                        .toLowerCase()
                        .contains(_query.toLowerCase()),
              )
              .toList()
        : _rows;
    return Scaffold(
      appBar: lpnAppBar(
        context,
        'Tienda',
        actions: [
          IconButton(
            tooltip: 'Actualizar productos',
            onPressed: _loading ? null : () => _fetch(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => _fetch(),
        child: ListView.builder(
          controller: _scroll,
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          itemCount: visible.length + 2,
          itemBuilder: (context, index) {
            if (index == 0) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'Productos para su cuidado',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _search,
                    maxLength: 100,
                    textInputAction: TextInputAction.search,
                    onSubmitted: (_) => _apply(),
                    decoration: InputDecoration(
                      labelText: 'Buscar productos',
                      counterText: '',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: IconButton(
                        tooltip: 'Aplicar búsqueda',
                        icon: const Icon(Icons.arrow_forward),
                        onPressed: _apply,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    key: ValueKey((_category, _categories.join('|'))),
                    initialValue: _category,
                    isExpanded: true,
                    decoration: const InputDecoration(labelText: 'Categoría'),
                    items: [
                      const DropdownMenuItem(value: '', child: Text('Todas')),
                      if (_category.isNotEmpty &&
                          !_categories.contains(_category))
                        DropdownMenuItem(
                          value: _category,
                          child: Text(_category),
                        ),
                      for (final c in _categories)
                        DropdownMenuItem(value: c, child: Text(c)),
                    ],
                    onChanged: (value) {
                      if (value == null) return;
                      _category = value;
                      _apply();
                    },
                  ),
                  const SizedBox(height: 16),
                  if (_loading && visible.isEmpty)
                    const Padding(
                      padding: EdgeInsets.all(20),
                      child: Center(child: CircularProgressIndicator()),
                    ),
                  if (!_loading && visible.isEmpty && _error == null)
                    const Padding(
                      padding: EdgeInsets.all(20),
                      child: Text('No hay productos para esta búsqueda.'),
                    ),
                ],
              );
            }
            if (index <= visible.length) {
              final row = visible[index - 1];
              return ProductCatalogCard(
                row: row,
                origin: widget.api.base,
                onOpen: () => widget.onOpen(row),
              );
            }
            return Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (_error != null)
                  Semantics(liveRegion: true, child: Text(_error!)),
                if (_next != null || _error != null)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    child: OutlinedButton.icon(
                      onPressed: _loading
                          ? null
                          : () =>
                                _fetch(more: _rows.isNotEmpty && _next != null),
                      icon: Icon(
                        _error == null ? Icons.expand_more : Icons.refresh,
                      ),
                      label: Text(
                        _loading
                            ? 'Cargando…'
                            : _error != null
                            ? 'Reintentar'
                            : 'Cargar más productos',
                      ),
                    ),
                  ),
              ],
            );
          },
        ),
      ),
    );
  }
}
