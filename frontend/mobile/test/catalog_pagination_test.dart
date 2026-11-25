import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/adoption/adoption_api.dart';
import 'package:little_paws_net/adoption/catalog_controller.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/main.dart';

Map<String, Object> pet(int id, [String species = 'Perro']) => {
  'id_mascota': id,
  'nombre': 'Mascota $id',
  'especie': species,
};
http.Response page(List<Object> pets, {String? next, int status = 200}) =>
    http.Response(
      jsonEncode({
        'results': pets,
        'next': next,
        'previous': null,
        'species': ['Gato', 'Perro'],
      }),
      status,
    );
const next = 'http://localhost:8016/api/adopcion/catalogo/?cursor=second';

void main() {
  late ApiClient client;
  late Session session;
  AdoptionApi setup(Future<http.Response> Function(http.Request) respond) {
    client = ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient(respond),
    );
    session = Session(client);
    addTearDown(session.dispose);
    addTearDown(client.close);
    return AdoptionApi(client, session);
  }

  test(
    'Page uses a local cursor and public requests without credentials',
    () async {
      final api = setup((request) async {
        expect(request.url.path, '/api/adopcion/catalogo/');
        expect(request.url.queryParameters, {
          'cursor': 'first',
          'especie': 'Perro',
        });
        expect(request.headers.containsKey('authorization'), isFalse);
        return page([pet(1)], next: '$next&especie=Perro');
      });
      final result = await api.catalogPage(cursor: 'first', species: 'Perro');
      expect(result.pets.single.id, 1);
      expect(result.nextCursor, 'second');
      expect(result.species, ['Gato', 'Perro']);
    },
  );

  test(
    'Page rejects external, wrong-route, repeated and mixed-filter links',
    () async {
      String? link;
      final api = setup((_) async => page([pet(1)], next: link));
      for (final invalid in [
        'https://other.invalid/api/adopcion/catalogo/?cursor=x',
        'javascript:alert(1)',
        '//other.invalid/api/adopcion/catalogo/?cursor=x',
        'http://localhost:8016/api/auth/perfil/?cursor=x',
        '$next#fragment',
        '$next&cursor=third',
        '$next&extra=1',
        '$next&especie=Gato',
        'http://localhost:8016/api/adopcion/catalogo/',
        'http://localhost:8016/api/adopcion/catalogo/?cursor=first',
      ]) {
        link = invalid;
        await expectLater(
          api.catalogPage(cursor: 'first'),
          throwsA(isA<ApiException>()),
        );
      }
    },
  );

  test('Malformed page documents fail with a recoverable API error', () async {
    Object? payload;
    final api = setup((_) async => http.Response(jsonEncode(payload), 200));
    for (final invalid in [
      null,
      [],
      {'results': null, 'species': []},
      {
        'results': [null],
        'species': [],
      },
      {'results': List.generate(25, (index) => pet(index + 1)), 'species': []},
      {
        'results': [],
        'species': [3],
      },
      {'results': [], 'species': [], 'next': 4},
    ]) {
      payload = invalid;
      await expectLater(api.catalogPage(), throwsA(isA<ApiException>()));
    }
  });

  test(
    'Failed next page preserves pets and retries once without duplicates',
    () async {
      var nextCalls = 0;
      final api = setup((request) async {
        if (!request.url.hasQuery) return page([pet(1)], next: next);
        nextCalls++;
        return nextCalls == 1 ? page([], status: 503) : page([pet(1), pet(2)]);
      });
      final controller = CatalogController(api);
      addTearDown(controller.dispose);
      await controller.reload();
      await controller.loadMore();
      expect(controller.pets.map((pet) => pet.id), [1]);
      expect(controller.pageError, isA<ApiException>());
      await Future.wait([controller.loadMore(), controller.loadMore()]);
      expect(nextCalls, 2);
      expect(controller.pets.map((pet) => pet.id), [1, 2]);
      expect(controller.nextCursor, isNull);
      expect(controller.pageError, isNull);
    },
  );

  test('A pending page cannot overwrite a newer species filter', () async {
    final started = Completer<void>();
    final release = Completer<http.Response>();
    final api = setup((request) async {
      if (request.url.queryParameters['especie'] == 'Gato') {
        return page([pet(3, 'Gato')]);
      }
      if (request.url.queryParameters.containsKey('cursor')) {
        started.complete();
        return release.future;
      }
      return page([pet(1)], next: next);
    });
    final controller = CatalogController(api);
    addTearDown(controller.dispose);
    await controller.reload();
    final pending = controller.loadMore();
    await started.future;
    await controller.reload(species: 'Gato');
    release.complete(page([pet(2)]));
    await pending;
    expect(controller.selectedSpecies, 'Gato');
    expect(controller.pets.map((pet) => pet.id), [3]);
    expect(controller.nextCursor, isNull);
    expect(controller.loadingMore, isFalse);
  });

  test('Disposal ignores a pending initial page', () async {
    final release = Completer<http.Response>();
    final api = setup((_) => release.future);
    final controller = CatalogController(api);
    var notifications = 0;
    controller.addListener(() => notifications++);
    final pending = controller.reload();
    controller.dispose();
    release.complete(page([pet(1)]));
    await pending;
    expect(notifications, 1);
  });

  testWidgets('Load more appends results and ends without an extra request', (
    tester,
  ) async {
    var calls = 0;
    setup((request) async {
      calls++;
      return request.url.hasQuery ? page([pet(2)]) : page([pet(1)], next: next);
    });
    await tester.pumpWidget(LittlePawsApp(showWelcome: false, api: client));
    await tester.pumpAndSettle();
    expect(calls, 1);
    final verticalScroll = find.byWidgetPredicate(
      (widget) =>
          widget is Scrollable && widget.axisDirection == AxisDirection.down,
    );
    await tester.scrollUntilVisible(
      find.text('Cargar más'),
      200,
      scrollable: verticalScroll,
    );
    // The list continues behind the floating bar; reveal the final action fully.
    final position = tester.state<ScrollableState>(verticalScroll).position;
    position.jumpTo(position.maxScrollExtent);
    await tester.pumpAndSettle();
    expect(
      tester.getRect(find.text('Cargar más')).bottom,
      lessThan(tester.getRect(find.byKey(const Key('navigation-primary'))).top),
    );
    await tester.tap(find.text('Cargar más'));
    await tester.pumpAndSettle();
    expect(calls, 2);
    expect(find.text('Cargar más'), findsNothing);
    await tester.scrollUntilVisible(
      find.text('Mascota 2'),
      -120,
      scrollable: verticalScroll,
    );
    expect(find.text('Mascota 2'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('Species filter finds pets beyond the initial page', (
    tester,
  ) async {
    setup(
      (request) async => request.url.queryParameters['especie'] == 'Gato'
          ? page([pet(30, 'Gato')])
          : page([pet(1)], next: next),
    );
    await tester.pumpWidget(LittlePawsApp(showWelcome: false, api: client));
    await tester.pumpAndSettle();
    await tester.tap(find.widgetWithText(ChoiceChip, 'Gato'));
    await tester.pumpAndSettle();
    await tester.scrollUntilVisible(
      find.text('Mascota 30'),
      160,
      scrollable: find.byType(Scrollable).first,
    );
    expect(find.text('Mascota 1'), findsNothing);
    expect(find.text('Mascota 30'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
