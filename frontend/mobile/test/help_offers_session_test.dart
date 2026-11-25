import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/explore/explore_screens.dart';

http.Response reply(Object value, [int status = 200]) => http.Response(
  jsonEncode(value),
  status,
  headers: {'content-type': 'application/json; charset=utf-8'},
);
const privateOffer = [
  {
    'id': 1,
    'organizacion': 'Organización QA',
    'modalidad': 'especie',
    'mensaje': 'Ofrecimiento privado de Ana QA',
  },
];

void main() {
  late ApiClient api;
  late Session session;
  var identity = 'ana@example.invalid';
  var reads = 0;
  late Future<http.Response> Function() offers;
  setUp(() async {
    identity = 'ana@example.invalid';
    reads = 0;
    offers = () async => reply(privateOffer);
    api = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient((request) async {
        switch (request.url.path) {
          case '/api/auth/token/':
            identity = (jsonDecode(request.body) as Map)['email'] as String;
            return reply({'access': identity, 'refresh': 'synthetic-refresh'});
          case '/api/auth/perfil/':
            return reply({'nombre': 'Persona QA', 'email': identity});
          case '/api/auth/token/revoke/':
            return reply({});
          case '/api/ayudas/intereses/':
            reads++;
            return offers();
          default:
            throw StateError('Unexpected synthetic route');
        }
      }),
    );
    session = Session(api);
    await session.restore();
    await session.login(identity, 'synthetic-password');
  });
  tearDown(() {
    session.dispose();
    api.close();
  });
  Future<void> open(WidgetTester tester, {bool withSession = true}) async {
    await tester.pumpWidget(
      MaterialApp(
        home: PublicListScreen(
          api: api,
          session: withSession ? session : null,
          path: '/api/ayudas/intereses/',
          title: 'Mis ofrecimientos',
          kind: 'offers',
        ),
      ),
    );
    await tester.pump();
  }

  testWidgets(
    'Logout removes an already rendered private help offer immediately',
    (tester) async {
      await open(tester);
      await tester.pumpAndSettle();
      expect(find.text('Ofrecimiento privado de Ana QA'), findsOneWidget);
      await session.logout();
      await tester.pumpAndSettle();
      expect(find.text('Ofrecimiento privado de Ana QA'), findsNothing);
      expect(find.text('Iniciar sesión'), findsOneWidget);
      expect(reads, 1);
    },
  );
  testWidgets(
    'A late response cannot reveal one account offers to another account',
    (tester) async {
      final pending = Completer<http.Response>();
      offers = () => pending.future;
      await open(tester);
      expect(reads, 1);
      offers = () async => reply({'detalle': 'Permiso denegado'}, 403);
      await session.login('bea@example.invalid', 'synthetic-password');
      await tester.pumpAndSettle();
      pending.complete(reply(privateOffer));
      await tester.pumpAndSettle();
      expect(reads, 2);
      expect(find.text('Ofrecimiento privado de Ana QA'), findsNothing);
      expect(
        find.text('Tu cuenta no tiene acceso para realizar esta acción.'),
        findsOneWidget,
      );
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Private offer route without a session makes no request and offers no retry',
    (tester) async {
      await open(tester, withSession: false);
      await tester.pumpAndSettle();
      expect(reads, 0);
      expect(find.text('Reintentar'), findsNothing);
      expect(find.textContaining('Inicia sesión'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Updating the same account profile does not reload its private offer list',
    (tester) async {
      await open(tester);
      await tester.pumpAndSettle();
      await session.updateProfile(name: 'Nombre nuevo QA');
      await tester.pumpAndSettle();
      expect(reads, 1);
      expect(find.text('Ofrecimiento privado de Ana QA'), findsOneWidget);
    },
  );
}
