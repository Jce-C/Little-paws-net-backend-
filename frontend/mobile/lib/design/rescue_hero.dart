import 'package:flutter/material.dart';

import 'lpn_theme.dart';

class RescueHero extends StatefulWidget {
  const RescueHero({super.key, required this.onSearchChanged});
  final ValueChanged<String> onSearchChanged;
  @override
  State<RescueHero> createState() => _RescueHeroState();
}

class _RescueHeroState extends State<RescueHero> {
  final _search = TextEditingController();
  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(horizontal: 20),
    child: ClipRRect(
      borderRadius: BorderRadius.circular(24),
      child: Stack(
        children: [
          const Positioned.fill(child: ColoredBox(color: LpnColors.charcoal)),
          Positioned.fill(
            child: Image.asset(
              'assets/rescue-banner.webp',
              key: const Key('rescue-hero'),
              fit: BoxFit.fitWidth,
              alignment: Alignment.topCenter,
              semanticLabel:
                  'Dos perros en un refugio; una persona acaricia a uno',
            ),
          ),
          Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    Colors.black.withValues(alpha: .72),
                  ],
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                SizedBox(
                  height: (MediaQuery.sizeOf(context).width * .42).clamp(
                    120,
                    180,
                  ),
                ),
                Align(
                  alignment: AlignmentDirectional.centerStart,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: .66),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Padding(
                      padding: EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                      child: Text(
                        'Ayúdanos a rescatar',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 26,
                          height: 1.15,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Semantics(
                  container: true,
                  child: TextField(
                    key: const Key('rescue-search'),
                    controller: _search,
                    maxLength: 100,
                    textInputAction: TextInputAction.search,
                    onSubmitted: (_) => FocusScope.of(context).unfocus(),
                    onChanged: (value) {
                      setState(() {});
                      widget.onSearchChanged(value);
                    },
                    decoration: InputDecoration(
                      labelText: 'Buscar reportes',
                      filled: true,
                      fillColor: LpnColors.paper.withValues(
                        alpha: LpnMaterials.solid(context) ? 1 : .96,
                      ),
                      counterText: '',
                      prefixIcon: const Icon(Icons.search, size: 20),
                      suffixIcon: _search.text.isEmpty
                          ? null
                          : IconButton(
                              tooltip: 'Limpiar búsqueda',
                              icon: const Icon(Icons.close, size: 18),
                              onPressed: () {
                                _search.clear();
                                setState(() {});
                                widget.onSearchChanged('');
                              },
                            ),
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
