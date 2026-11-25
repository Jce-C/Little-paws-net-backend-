import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/pets/personal_pet_screen.dart';
import 'package:little_paws_net/pets/profile_pet_preview.dart';
import 'package:little_paws_net/pets/owned_pets_api.dart';

http.Response json(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);
void main() {
  const directory = String.fromEnvironment('LPN_VISUAL_QA_DIR');
  setUpAll(() async {
    for (final f in {
      'Inter': 'assets/fonts/Inter.ttf',
      'MaterialIcons': 'fonts/MaterialIcons-Regular.otf',
    }.entries) {
      await (FontLoader(f.key)..addFont(rootBundle.load(f.value))).load();
    }
  });
  late ApiClient api;
  late Session session;
  late Future<http.Response> Function(http.Request) respond;
  var writes = 0;
  var email = 'qa@example.invalid';
  setUp(() async {
    writes = 0;
    api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((r) async {
        if (r.url.path == '/api/auth/token/') {
          email = (jsonDecode(r.body) as Map)['email'] as String;
          return json({'access': email, 'refresh': 'qa-refresh'});
        }
        if (r.url.path == '/api/auth/perfil/') {
          return json({'nombre': 'Persona QA', 'email': email});
        }
        if (r.url.path == '/api/auth/token/revoke/') return json({});
        if (r.method == 'POST') writes++;
        return respond(r);
      }),
    );
    session = Session(api);
    await session.restore();
    await session.login(email, 'synthetic', remember: false);
  });
  tearDown(() {
    session.dispose();
    api.close();
  });
  Future<void> open(WidgetTester tester, Widget child) async {
    tester.view.physicalSize = const Size(393, 852);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      RepaintBoundary(
        key: const Key('account-pet-capture'),
        child: MaterialApp(
          theme: lpnTheme(),
          locale: const Locale('es'),
          supportedLocales: const [Locale('es')],
          localizationsDelegates: GlobalMaterialLocalizations.delegates,
          debugShowCheckedModeBanner: false,
          home: Scaffold(body: child),
        ),
      ),
    );
    await tester.pumpAndSettle();
  }

  Future<void> capture(WidgetTester tester, String name) async {
    await tester.pumpAndSettle();
    if (directory.isNotEmpty) {
      await expectLater(
        find.byKey(const Key('account-pet-capture')),
        matchesGoldenFile(Uri.file('$directory/$name.png')),
      );
    }
  }

  testWidgets(
    'Personal pet preview requests only three and opens its private ficha, not medical route',
    (tester) async {
      var reads = 0;
      respond = (r) async {
        reads++;
        if (r.url.path == '/api/mascotas/mias/') {
          expect(r.url.queryParameters['limite'], '3');
          return json({
            'results': [
              {
                'id_mascota': 8,
                'nombre': 'Moka QA',
                'especie': 'Conejo',
                'estado': 'Con dueño',
                'custodia_vigente': false,
                'personal': {'raza': 'Sin raza registrada', 'color': 'Gris'},
              },
            ],
            'next_cursor': '8',
          });
        }
        expect(r.url.path, '/api/mascotas/personales/8/');
        return json({
          'id_mascota': 8,
          'nombre': 'Moka QA',
          'especie': 'Conejo',
          'color': 'Gris',
          'descripcion': 'Ficha privada de ejemplo',
        });
      };
      await open(tester, ProfilePetPreview(api: OwnedPetsApi(api, session)));
      expect(find.textContaining('en total'), findsNothing);
      expect(find.text('Ver expediente'), findsNothing);
      await capture(tester, '01-vista-previa');
      await tester.tap(find.text('Ver ficha'));
      await tester.pumpAndSettle();
      expect(find.text('Ficha de tu mascota'), findsOneWidget);
      expect(find.text('Gris'), findsOneWidget);
      expect(reads, 2);
      await capture(tester, '02-ficha-privada');
    },
  );
  testWidgets('Registration stays private and preserves its draft on cancel', (
    tester,
  ) async {
    respond = (_) async => json({}, 500);
    await open(
      tester,
      Builder(
        builder: (context) => TextButton(
          onPressed: () => Navigator.of(context).push(
            MaterialPageRoute(
              builder: (_) => PersonalPetScreen(session: session),
            ),
          ),
          child: const Text('Agregar'),
        ),
      ),
    );
    await tester.tap(find.text('Agregar'));
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('personal-nombre')), 'Moka QA');
    await tester.enterText(
      find.byKey(const Key('personal-especie')),
      'Especie no catalogada',
    );
    await capture(tester, '03-agregar-mascota');
    await tester.tap(find.byKey(const Key('personal-cancel')));
    await tester.pumpAndSettle();
    expect(find.text('¿Descartar esta mascota?'), findsOneWidget);
    await tester.tap(find.text('Seguir editando'));
    await tester.pumpAndSettle();
    expect(find.text('Moka QA'), findsOneWidget);
    await tester.tap(find.byKey(const Key('personal-cancel')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Descartar'));
    await tester.pumpAndSettle();
    expect(find.text('Agregar'), findsOneWidget);
    expect(writes, 0);
  });
  testWidgets(
    'Same-account reauthentication destroys an unfinished private pet form',
    (tester) async {
      respond = (_) async => json({}, 500);
      await open(tester, PersonalPetScreen(session: session));
      await tester.enterText(
        find.byKey(const Key('personal-nombre')),
        'Borrador anterior',
      );
      await session.login(email, 'synthetic', remember: false);
      await tester.pumpAndSettle();
      expect(find.text('Borrador anterior'), findsNothing);
      expect(writes, 0);
    },
  );
  testWidgets(
    'Registration primary and cancel remain usable at 320px and 200 percent text',
    (tester) async {
      respond = (_) async => json({}, 500);
      await open(tester, PersonalPetScreen(session: session));
      tester.view.physicalSize = const Size(320, 640);
      tester.platformDispatcher.textScaleFactorTestValue = 2;
      addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
      await tester.pumpAndSettle();
      expect(
        find.byKey(const Key('personal-save')).hitTestable(),
        findsOneWidget,
      );
      expect(
        find.byKey(const Key('personal-cancel')).hitTestable(),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    },
  );
}
