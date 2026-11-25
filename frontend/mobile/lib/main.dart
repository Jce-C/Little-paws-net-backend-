import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'adoption/adoption_api.dart';
import 'adoption/adoption_screens.dart';
import 'auth/account_screen.dart';
import 'auth/session.dart';
import 'core/api_client.dart';
import 'design/lpn_theme.dart';
import 'design/lpn_navigation.dart';
import 'design/welcome_screen.dart';
import 'notifications/notifications_api.dart';
import 'notifications/notifications_screen.dart';
import 'rescue/rescue_api.dart';
import 'rescue/rescue_screens.dart';
import 'explore/explore_screens.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(configuredApp());
}

Widget configuredApp() {
  try {
    return LittlePawsApp(api: ApiClient.fromEnvironment());
  } catch (error) {
    if (error is! ArgumentError && error is! FormatException) rethrow;
    return MaterialApp(
      theme: lpnTheme(),
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        body: SafeArea(
          child: Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.cloud_off_outlined, size: 40),
                  const SizedBox(height: 16),
                  const Text(
                    'Esta versión aún no está conectada',
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Solicita al equipo una versión de prueba configurada para continuar.',
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class LittlePawsApp extends StatefulWidget {
  const LittlePawsApp({
    super.key,
    required this.api,
    this.showWelcome = true,
    this.frameBuilder,
  });
  final TransitionBuilder? frameBuilder;
  final bool showWelcome;
  final ApiClient api;

  @override
  State<LittlePawsApp> createState() => _LittlePawsAppState();
}

class _LittlePawsAppState extends State<LittlePawsApp> {
  late final Session session = Session(widget.api);
  late bool _welcome = widget.showWelcome;
  bool _reduceTransparency = false;
  int _appearanceRevision = 0;
  final _appearanceStorage = const FlutterSecureStorage();
  Future<void> _appearanceWrites = Future.value();
  late final AdoptionApi adoption = AdoptionApi(widget.api, session);

  @override
  void initState() {
    super.initState();
    session.restore();
    _restoreAppearance();
  }

  Future<void> _restoreAppearance() async {
    final revision = _appearanceRevision;
    try {
      final saved = await _appearanceStorage.read(
        key: 'lpn_reduce_transparency',
      );
      if (mounted && revision == _appearanceRevision) {
        setState(() => _reduceTransparency = saved == '1');
      }
    } on Exception {
      // System high contrast remains available if local storage is unavailable.
    }
  }

  void _toggleTransparency() {
    ++_appearanceRevision;
    setState(() => _reduceTransparency = !_reduceTransparency);
    final value = _reduceTransparency ? '1' : '0';
    _appearanceWrites = _appearanceWrites.then((_) async {
      try {
        await _appearanceStorage.write(
          key: 'lpn_reduce_transparency',
          value: value,
        );
      } on Exception {
        // The appearance change still applies during this session.
      }
    });
  }

  @override
  void dispose() {
    session.dispose();
    widget.api.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Little Paws Net',
      builder: widget.frameBuilder,
      debugShowCheckedModeBanner: false,
      locale: const Locale('es'),
      supportedLocales: const [Locale('es')],
      localizationsDelegates: GlobalMaterialLocalizations.delegates,
      theme: lpnTheme(reduceTransparency: _reduceTransparency),
      home: ListenableBuilder(
        listenable: session,
        builder: (context, _) {
          if (_welcome && !session.signedIn) {
            return WelcomeScreen(
              session: session,
              onExplore: () => setState(() => _welcome = false),
            );
          }
          return Home(
            initialIndex: session.signedIn ? 0 : 1,
            adoption: adoption,
            session: session,
            reduceTransparency: _reduceTransparency,
            onTransparencyChanged: _toggleTransparency,
          );
        },
      ),
    );
  }
}

class Home extends StatefulWidget {
  const Home({
    super.key,
    required this.adoption,
    required this.session,
    this.reduceTransparency = false,
    this.onTransparencyChanged,
    this.initialIndex = 1,
  });
  final int initialIndex;
  final bool reduceTransparency;
  final VoidCallback? onTransparencyChanged;
  final AdoptionApi adoption;
  final Session session;

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  late int _index = widget.initialIndex;

  @override
  Widget build(BuildContext context) {
    final view = switch (_index) {
      0 => ExploreScreen(
        api: widget.adoption.api,
        session: widget.session,
        onAdopt: () => setState(() => _index = 1),
        onRescue: () => Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => Scaffold(
              appBar: AppBar(title: const Text('Animales que necesitan ayuda')),
              body: RescueScreen(
                api: RescueApi(widget.adoption.api, widget.session),
                onAdopt: () {
                  Navigator.of(context).pop();
                  setState(() => _index = 1);
                },
              ),
            ),
          ),
        ),
      ),
      2 => RequestsScreen(api: widget.adoption, session: widget.session),
      3 => AccountScreen(session: widget.session),
      _ => CatalogScreen(
        api: widget.adoption,
        session: widget.session,
        onRequested: () => setState(() => _index = 2),
      ),
    };
    return Scaffold(
      appBar: AppBar(
        toolbarHeight: _brandToolbarHeight(context),
        actions: [
          PopupMenuButton<String>(
            tooltip: 'Apariencia',
            icon: const Icon(Icons.tune_rounded),
            onSelected: (_) => widget.onTransparencyChanged?.call(),
            itemBuilder: (_) => [
              CheckedPopupMenuItem(
                value: 'transparency',
                checked: widget.reduceTransparency,
                child: const Text('Reducir transparencias'),
              ),
            ],
          ),
          IconButton(
            tooltip: 'Notificaciones',
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => NotificationsScreen(
                  api: NotificationsApi(widget.adoption.api, widget.session),
                ),
              ),
            ),
          ),
        ],
        backgroundColor: Theme.of(context).colorScheme.surface,
        title: Row(
          children: [
            SvgPicture.asset(
              'assets/brand-organic.svg',
              width: 30,
              height: 34,
              excludeFromSemantics: true,
            ),
            const SizedBox(width: 10),
            const Expanded(
              child: Text(
                'LITTLE PAWS NET',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w400),
              ),
            ),
          ],
        ),
      ),
      // Let content continue behind the shaped floating navigation.
      extendBody: true,
      body: TweenAnimationBuilder<double>(
        key: ValueKey(_index),
        tween: Tween(begin: 0, end: 1),
        duration: Duration(
          milliseconds: MediaQuery.disableAnimationsOf(context) ? 0 : 220,
        ),
        curve: Curves.easeOutCubic,
        child: view,
        builder: (context, progress, child) => Opacity(
          opacity: .85 + .15 * progress,
          child: Transform.translate(
            offset: Offset(0, 6 * (1 - progress)),
            child: child,
          ),
        ),
      ),
      bottomNavigationBar: MediaQuery.viewInsetsOf(context).bottom > 0
          ? null
          : LpnNavigation(
              selected: _index,
              onSelected: (index) => setState(() => _index = index),
              onPrimary: () {
                if (_index == 2) {
                  setState(() => _index = 1);
                } else {
                  openReportFlow(
                    context,
                    RescueApi(widget.adoption.api, widget.session),
                  );
                }
              },
            ),
    );
  }
}

// Measure the brand with the actual system text scale and bell space.
double _brandToolbarHeight(BuildContext context) {
  final style = Theme.of(context).textTheme.titleLarge!
      .copyWith(fontSize: 14, fontWeight: FontWeight.w400);
  final width = (MediaQuery.sizeOf(context).width - 32 - 38 - 96).clamp(
    1.0,
    double.infinity,
  );
  final painter = TextPainter(
    text: TextSpan(text: 'LITTLE PAWS NET', style: style),
    textScaler: MediaQuery.textScalerOf(context),
    textDirection: Directionality.of(context),
  )..layout(maxWidth: width);
  final height = (painter.height + 16).clamp(kToolbarHeight, double.infinity);
  painter.dispose();
  return height;
}
