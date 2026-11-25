import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/pets/owned_pets_api.dart';
import 'package:little_paws_net/pets/pet_qr_screen.dart';
import 'package:qr_flutter/qr_flutter.dart';

void main() {
  late ApiClient client;
  late Session session;
  var requests = 0;
  var denied = false;
  var invalid = false;
  Completer<http.Response>? pending;

  setUp(() async {
    requests = 0;
    denied = false;
    invalid = false;
    pending = null;
    http.Response json(Object value, [int status = 200]) => http.Response(
      jsonEncode(value),
      status,
      headers: {'content-type': 'application/json; charset=utf-8'},
    );
    client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        if (request.url.path == '/api/auth/token/') {
          return json({'access': 'access', 'refresh': 'refresh'});
        }
        if (request.url.path == '/api/auth/perfil/') {
          return json({'nombre': 'Ana QA', 'email': 'ana@example.invalid'});
        }
        if (request.url.path == '/api/auth/token/revoke/') return json({});
        if (request.url.path == '/api/mascotas/8/qr/') {
          expect(request.method, 'POST');
          expect(request.headers['authorization'], 'Bearer access');
          requests++;
          if (pending != null) return pending!.future;
          if (denied) return json({}, 403);
          return json({
            'id_qr': requests,
            'codigo': invalid ? 'invalid' : 'a' * 42 + '$requests',
            'expira': DateTime.now()
                .add(const Duration(hours: 24))
                .toUtc()
                .toIso8601String(),
          }, 201);
        }
        throw StateError('Unexpected route');
      }),
    );
    session = Session(client);
    await session.restore();
    await session.login('ana@example.invalid', 'test-password');
  });

  tearDown(() {
    session.dispose();
    client.close();
  });

  Future<void> open(WidgetTester tester, {bool enlarged = false}) async {
    if (enlarged) {
      tester.view.physicalSize = const Size(320, 640);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
    }
    await tester.pumpWidget(
      MaterialApp(
        builder: enlarged
            ? (context, child) => MediaQuery(
                data: MediaQuery.of(context)
                    .copyWith(textScaler: const TextScaler.linear(2)),
                child: child!,
              )
            : null,
        home: PetQrScreen(api: OwnedPetsApi(client, session), petId: 8),
      ),
    );
    await tester.pumpAndSettle();
  }

  Future<void> generate(WidgetTester tester) async {
    await tester.ensureVisible(find.text('Generar QR'));
    await tester.tap(find.text('Generar QR'));
    await tester.pumpAndSettle();
  }

  testWidgets(
    'Only explicit generation issues a QR; replacing it requires confirmation',
    (tester) async {
      await open(tester);
      expect(requests, 0);
      expect(find.byType(QrImageView), findsNothing);
      await generate(tester);
      expect(requests, 1);
      expect(find.byType(QrImageView), findsOneWidget);
      await tester.ensureVisible(find.text('Generar otro QR'));
      await tester.tap(find.text('Generar otro QR'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Cancelar'));
      await tester.pumpAndSettle();
      expect(requests, 1);
      await tester.tap(find.text('Generar otro QR'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Generar otro'));
      await tester.pumpAndSettle();
      expect(requests, 2);
      expect(find.byType(QrImageView), findsOneWidget);
      await tester.pumpWidget(const SizedBox());
    },
  );

  testWidgets('Backgrounding hides identifier without issuing another one', (
    tester,
  ) async {
    await open(tester);
    await generate(tester);
    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.inactive);
    await tester.pumpAndSettle();
    expect(find.byType(QrImageView), findsNothing);
    tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
    await tester.pumpAndSettle();
    expect(requests, 1);
    expect(find.text('Generar QR'), findsOneWidget);
  });

  testWidgets('Logout removes QR and does not expose it to next account', (
    tester,
  ) async {
    await open(tester);
    await generate(tester);
    await session.logout();
    await tester.pumpAndSettle();
    expect(find.byType(QrImageView), findsNothing);
    expect(
      find.text('Inicia sesión de nuevo para generar un QR.'),
      findsOneWidget,
    );
    await session.login('ana@example.invalid', 'test-password');
    await tester.pumpAndSettle();
    expect(find.byType(QrImageView), findsNothing);
    expect(requests, 1);
  });

  testWidgets(
    'An issuance finishing in the background cannot redisplay the QR',
    (tester) async {
      await open(tester);
      pending = Completer<http.Response>();
      await tester.tap(find.text('Generar QR'));
      await tester.pump();
      tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.inactive);
      await tester.pump();
      pending!.complete(
        http.Response(
          jsonEncode({
            'id_qr': 1,
            'codigo': 'a' * 43,
            'expira': DateTime.now()
                .add(const Duration(hours: 24))
                .toUtc()
                .toIso8601String(),
          }),
          201,
          headers: {'content-type': 'application/json'},
        ),
      );
      await tester.pumpAndSettle();
      tester.binding.handleAppLifecycleStateChanged(AppLifecycleState.resumed);
      await tester.pumpAndSettle();
      expect(find.byType(QrImageView), findsNothing);
      expect(requests, 1);
      expect(find.text('Generar QR'), findsOneWidget);
    },
  );

  testWidgets(
    'Server rejection clears previous QR and leaves a recoverable state',
    (tester) async {
      await open(tester);
      await generate(tester);
      denied = true;
      await tester.ensureVisible(find.text('Generar otro QR'));
      await tester.tap(find.text('Generar otro QR'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Generar otro'));
      await tester.pumpAndSettle();
      expect(find.byType(QrImageView), findsNothing);
      expect(
        find.text('Tu cuenta no tiene acceso para realizar esta acción.'),
        findsOneWidget,
      );
      expect(find.text('Generar QR'), findsOneWidget);
    },
  );

  testWidgets('Expired identifier disappears even without network access', (
    tester,
  ) async {
    await open(tester);
    await generate(tester);
    await tester.pump(const Duration(hours: 25));
    expect(find.byType(QrImageView), findsNothing);
    expect(
      find.text('El QR venció. Genera otro cuando lo necesites.'),
      findsOneWidget,
    );
    expect(requests, 1);
  });

  testWidgets('QR and generation controls fit at 320px with 200 percent text', (
    tester,
  ) async {
    await open(tester, enlarged: true);
    await generate(tester);
    await tester.scrollUntilVisible(find.byType(QrImageView), 200);
    expect(find.byType(QrImageView), findsOneWidget);
    expect(find.text('Generar otro QR'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tester.pumpWidget(const SizedBox());
  });

  test(
    'Malformed QR is rejected instead of rendering an unusable identifier',
    () async {
      invalid = true;
      await expectLater(
        OwnedPetsApi(client, session).generateQr(8),
        throwsA(isA<ApiException>()),
      );
    },
  );
  testWidgets(
    'Reauthenticating the same account removes the old QR without issuing another',
    (tester) async {
      await open(tester);
      await generate(tester);
      expect(find.byType(QrImageView), findsOneWidget);
      await session.login('ana@example.invalid', 'test-password');
      await tester.pumpAndSettle();
      expect(find.byType(QrImageView), findsNothing);
      expect(requests, 1);
      expect(find.text('Generar QR'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
}
