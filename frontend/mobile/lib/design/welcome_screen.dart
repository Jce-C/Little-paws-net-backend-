import 'package:flutter/material.dart';

import '../auth/account_screen.dart';
import '../auth/session.dart';
import 'access_reference.dart';
import 'organic_surface.dart';

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({
    super.key,
    required this.session,
    required this.onExplore,
  });
  final Session session;
  final VoidCallback onExplore;
  Future<void> _login(BuildContext context, {bool register = false}) async {
    final entered = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) =>
            LoginScreen(session: session, initialRegister: register),
      ),
    );
    if (entered == true) onExplore();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    key: const Key('welcome-screen'),
    backgroundColor: AccessPalette.welcome,
    body: DecoratedBox(
      decoration: const BoxDecoration(
        gradient: RadialGradient(
          center: Alignment(.8, -.9),
          radius: 1.2,
          colors: [Color(0xfff9e2af), AccessPalette.welcome],
        ),
      ),
      child: Stack(
        children: [
          Positioned(
            right: -180,
            top: -110,
            child: ExcludeSemantics(
              child: Container(
                width: 300,
                height: 300,
                decoration: const BoxDecoration(
                  color: Color(0xfff5d28e),
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ),
          SafeArea(
            bottom: false,
            child: LayoutBuilder(
              builder: (context, constraints) {
                final compact = constraints.maxHeight < 620;
                final titleStyle = TextStyle(
                  fontFamily: 'Inter',
                  fontSize: compact ? 22 : 28,
                  height: 1.12,
                  letterSpacing: -.6,
                  fontWeight: FontWeight.w700,
                  color: const Color(0xff171717),
                );
                final measured = TextPainter(
                  text: TextSpan(
                    text: 'Para quienes aman a los animales.',
                    style: titleStyle,
                  ),
                  textDirection: Directionality.of(context),
                  textScaler: MediaQuery.textScalerOf(context),
                )..layout(maxWidth: constraints.maxWidth - 64);
                final titleHeight = measured.height;
                measured.dispose();
                final pictureHeight = compact ? 88.0 : 132.0;
                final minimumHero = titleHeight + 40 + pictureHeight + 24;
                final baseHero = (constraints.maxHeight * (compact ? .40 : .47))
                    .clamp(180.0, 430.0);
                final heroHeight = baseHero > minimumHero
                    ? baseHero
                    : minimumHero;
                return SingleChildScrollView(
                  child: ConstrainedBox(
                    constraints: BoxConstraints(
                      minHeight: constraints.maxHeight,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        SizedBox(
                          height: heroHeight,
                          child: SubtleEntrance(
                            child: Stack(
                              children: [
                                Positioned(
                                  left: 24,
                                  right: 24,
                                  bottom: titleHeight + 40,
                                  height: pictureHeight,
                                  child: Image.asset(
                                    'assets/access/welcome-pets.webp',
                                    key: const Key('welcome-pets'),
                                    fit: BoxFit.contain,
                                    excludeFromSemantics: true,
                                  ),
                                ),
                                Positioned(
                                  left: 32,
                                  right: 32,
                                  bottom: 24,
                                  child: Text(
                                    'Para quienes aman a los animales.',
                                    style: titleStyle,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                        Container(
                          constraints: BoxConstraints(
                            minHeight: (constraints.maxHeight - heroHeight)
                                .clamp(0.0, double.infinity),
                          ),
                          padding: EdgeInsets.fromLTRB(
                            32,
                            compact ? 16 : 42,
                            32,
                            20 + MediaQuery.paddingOf(context).bottom,
                          ),
                          decoration: const BoxDecoration(
                            color: AccessPalette.cream,
                            borderRadius: BorderRadius.vertical(
                              top: Radius.circular(52),
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.stretch,
                            children: [
                              Text(
                                'Encuentra y adopta con Little Paws Net.',
                                style: TextStyle(
                                  fontSize: compact ? 18 : 20,
                                  height: 1.3,
                                  color: AccessPalette.purple,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              SizedBox(height: compact ? 12 : 26),
                              FilledButton(
                                key: const Key('welcome-explore'),
                                style: FilledButton.styleFrom(
                                  backgroundColor: AccessPalette.purple,
                                  foregroundColor: AccessPalette.cream,
                                  minimumSize: Size(48, compact ? 48 : 56),
                                  shape: const StadiumBorder(),
                                ),
                                onPressed: onExplore,
                                child: const Row(
                                  children: [
                                    Expanded(
                                      child: Text(
                                        'Encontrar compañero',
                                        style: TextStyle(
                                          fontWeight: FontWeight.w700,
                                        ),
                                      ),
                                    ),
                                    Icon(Icons.arrow_forward),
                                  ],
                                ),
                              ),
                              SizedBox(height: compact ? 6 : 20),
                              Wrap(
                                alignment: WrapAlignment.center,
                                crossAxisAlignment: WrapCrossAlignment.center,
                                children: [
                                  if (!compact)
                                    const Text(
                                      '¿Ya tienes cuenta?',
                                      style: TextStyle(
                                        color: AccessPalette.purple,
                                        fontSize: 14,
                                      ),
                                    ),
                                  TextButton(
                                    key: const Key('welcome-login'),
                                    onPressed: () => _login(context),
                                    child: const Text(
                                      'Iniciar sesión',
                                      style: TextStyle(
                                        color: AccessPalette.purple,
                                        fontWeight: FontWeight.w700,
                                      ),
                                    ),
                                  ),
                                  TextButton(
                                    key: const Key('welcome-register'),
                                    onPressed: () =>
                                        _login(context, register: true),
                                    child: const Text(
                                      'Crear cuenta',
                                      style: TextStyle(
                                        color: AccessPalette.purple,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    ),
  );
}
