import 'dart:async';
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';

http.Response json(Object value, {int status = 200}) =>
    http.Response(jsonEncode(value), status);

ApiClient client(Future<http.Response> Function(http.Request) respond) =>
    ApiClient(
      base: Uri.parse('http://localhost:8016'),
      client: MockClient(respond),
    );

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() => FlutterSecureStorage.setMockInitialValues({}));

  test('Remember opt-out keeps access only in memory and erases a prior stored token', () async {
    final base = Uri.parse('https://qa.littlepaws.invalid');
    final storageKey =
        'lpn_refresh_${base64Url.encode(utf8.encode(base.origin))}';
    FlutterSecureStorage.setMockInitialValues({storageKey: 'previous-refresh'});
    final api = ApiClient(
      base: base,
      client: MockClient((request) async {
        if (request.url.path == '/api/auth/token/') {
          return json({'access': 'memory-access', 'refresh': 'memory-refresh'});
        }
        return json({'nombre': 'Ana', 'email': 'ana@example.invalid'});
      }),
    );
    addTearDown(api.close);
    final session = Session(api);
    addTearDown(session.dispose);
    await session.login(
      'ana@example.invalid',
      'example password',
      remember: false,
    );
    expect(session.account?.email, 'ana@example.invalid');
    expect(await session.authorized((token) async => token), 'memory-access');
    expect(await const FlutterSecureStorage().read(key: storageKey), isNull);
    var restoreCalls = 0;
    final freshApi = ApiClient(
      base: base,
      client: MockClient((_) async {
        restoreCalls++;
        return json({});
      }),
    );
    addTearDown(freshApi.close);
    final freshSession = Session(freshApi);
    addTearDown(freshSession.dispose);
    await freshSession.restore();
    expect(freshSession.account, isNull);
    expect(restoreCalls, 0);
  });
  test(
    'Restore rotates the stored refresh and loads the current profile',
    () async {
      final base = Uri.parse('https://qa.littlepaws.invalid');
      final storageKey =
          'lpn_refresh_${base64Url.encode(utf8.encode(base.origin))}';
      FlutterSecureStorage.setMockInitialValues({storageKey: 'stored-refresh'});
      final api = ApiClient(
        base: base,
        client: MockClient((request) async {
          if (request.url.path == '/api/auth/token/refresh/') {
            expect(jsonDecode(request.body), {'refresh': 'stored-refresh'});
            return json({
              'access': 'restored-access',
              'refresh': 'rotated-refresh',
            });
          }
          expect(request.headers['authorization'], 'Bearer restored-access');
          return json({'nombre': 'Ana', 'email': 'ana@example.invalid'});
        }),
      );
      addTearDown(api.close);
      final session = Session(api);
      addTearDown(session.dispose);
      await session.restore();
      expect(session.restoring, isFalse);
      expect(session.account?.email, 'ana@example.invalid');
      expect(
        await const FlutterSecureStorage().read(key: storageKey),
        'rotated-refresh',
      );
    },
  );

  test(
    'A late restore cannot erase a newer login or its saved token',
    () async {
      final base = Uri.parse('https://qa.littlepaws.invalid');
      final storageKey =
          'lpn_refresh_${base64Url.encode(utf8.encode(base.origin))}';
      FlutterSecureStorage.setMockInitialValues({
        storageKey: 'previous-refresh',
      });
      final restoring = Completer<void>();
      final release = Completer<http.Response>();
      final api = ApiClient(
        base: base,
        client: MockClient((request) async {
          switch (request.url.path) {
            case '/api/auth/token/refresh/':
              restoring.complete();
              return release.future;
            case '/api/auth/token/':
              return json({'access': 'new-access', 'refresh': 'new-refresh'});
            case '/api/auth/perfil/':
              return json({
                'nombre': 'Carlos',
                'email': 'carlos@example.invalid',
              });
            default:
              throw StateError('Unexpected route');
          }
        }),
      );
      addTearDown(api.close);
      final session = Session(api);
      addTearDown(session.dispose);
      final restore = session.restore();
      await restoring.future;
      await session.login('carlos@example.invalid', 'test-password');
      release.complete(json({'detail': 'Revoked'}, status: 401));
      await restore;
      expect(session.account?.email, 'carlos@example.invalid');
      expect(
        await const FlutterSecureStorage().read(key: storageKey),
        'new-refresh',
      );
    },
  );

  test('A second unauthorized response ends the session', () async {
    final api = client((request) async {
      return switch (request.url.path) {
        '/api/auth/token/' => json({'access': 'old', 'refresh': 'refresh'}),
        '/api/auth/perfil/' => json({
          'nombre': 'Ana',
          'email': 'ana@example.invalid',
        }),
        '/api/auth/token/refresh/' => json({
          'access': 'renewed',
          'refresh': 'rotated',
        }),
        _ => throw StateError('Unexpected route'),
      };
    });
    addTearDown(api.close);
    final session = Session(api);
    addTearDown(session.dispose);
    await session.restore();
    await session.login('ana@example.invalid', 'test-password');

    await expectLater(
      session.authorized<Object?>((token) async {
        throw const ApiException('Unauthorized', status: 401);
      }),
      throwsA(isA<ApiException>().having((e) => e.status, 'status', 401)),
    );
    expect(session.signedIn, isFalse);
  });

  test(
    'Concurrent requests share one refresh and use the rotated token',
    () async {
      final release = Completer<void>();
      final started = Completer<void>();
      var refreshes = 0;
      final api = client((request) async {
        switch (request.url.path) {
          case '/api/auth/token/':
            return json({'access': 'old', 'refresh': 'refresh'});
          case '/api/auth/perfil/':
            return json({'nombre': 'Ana', 'email': 'ana@example.invalid'});
          case '/api/auth/token/refresh/':
            refreshes++;
            if (!started.isCompleted) started.complete();
            await release.future;
            return json({'access': 'renewed', 'refresh': 'rotated'});
          default:
            throw StateError('Unexpected route');
        }
      });
      addTearDown(api.close);
      final session = Session(api);
      addTearDown(session.dispose);
      await session.restore();
      await session.login('ana@example.invalid', 'test-password');

      Future<String> operation(String token) async {
        if (token == 'old') throw const ApiException('Expired', status: 401);
        return token;
      }

      final first = session.authorized(operation);
      final second = session.authorized(operation);
      await started.future;
      release.complete();
      expect(await Future.wait([first, second]), ['renewed', 'renewed']);
      expect(refreshes, 1);
      expect(await session.authorized((token) async => token), 'renewed');
    },
  );

  test('An expired refresh returns the account to signed out', () async {
    final api = client((request) async {
      return switch (request.url.path) {
        '/api/auth/token/' => json({'access': 'old', 'refresh': 'refresh'}),
        '/api/auth/perfil/' => json({
          'nombre': 'Ana',
          'email': 'ana@example.invalid',
        }),
        '/api/auth/token/refresh/' => json({'detail': 'Expired'}, status: 401),
        _ => throw StateError('Unexpected route'),
      };
    });
    addTearDown(api.close);
    final session = Session(api);
    addTearDown(session.dispose);
    await session.restore();
    await session.login('ana@example.invalid', 'test-password');
    await expectLater(
      session.authorized<Object?>((token) async {
        throw const ApiException('Expired', status: 401);
      }),
      throwsA(isA<ApiException>()),
    );
    expect(session.signedIn, isFalse);
  });

  test(
    'Permission denied does not renew or sign out a valid account',
    () async {
      var refreshes = 0;
      final api = client((request) async {
        switch (request.url.path) {
          case '/api/auth/token/':
            return json({'access': 'old', 'refresh': 'refresh'});
          case '/api/auth/perfil/':
            return json({'nombre': 'Ana', 'email': 'ana@example.invalid'});
          default:
            refreshes++;
            throw StateError('A forbidden operation must not renew');
        }
      });
      addTearDown(api.close);
      final session = Session(api);
      addTearDown(session.dispose);
      await session.restore();
      await session.login('ana@example.invalid', 'test-password');
      await expectLater(
        session.authorized<Object?>((token) async {
          throw const ApiException('Forbidden', status: 403);
        }),
        throwsA(isA<ApiException>().having((e) => e.status, 'status', 403)),
      );
      expect(session.signedIn, isTrue);
      expect(refreshes, 0);
    },
  );

  test(
    'Old refresh cannot sign out the account that logged in afterwards',
    () async {
      final started = Completer<void>();
      final release = Completer<http.Response>();
      var logins = 0;
      final api = client((request) async {
        switch (request.url.path) {
          case '/api/auth/token/':
            logins++;
            return json({
              'access': 'access-$logins',
              'refresh': 'refresh-$logins',
            });
          case '/api/auth/perfil/':
            final second =
                request.headers['authorization'] == 'Bearer access-2';
            return json({
              'nombre': second ? 'Carlos' : 'Ana',
              'email': second
                  ? 'carlos@example.invalid'
                  : 'ana@example.invalid',
            });
          case '/api/auth/token/refresh/':
            started.complete();
            return release.future;
          case '/api/auth/token/revoke/':
            return http.Response('', 205);
          default:
            throw StateError('Unexpected route');
        }
      });
      addTearDown(api.close);
      final session = Session(api);
      addTearDown(session.dispose);
      await session.restore();
      await session.login('ana@example.invalid', 'test-password');
      final old = session.authorized<Object?>((token) async {
        throw const ApiException('Expired', status: 401);
      });
      final failure = expectLater(old, throwsA(isA<ApiException>()));
      await started.future;
      await session.logout();
      await session.login('carlos@example.invalid', 'test-password');
      release.complete(json({'detail': 'Revoked'}, status: 401));
      await failure;
      expect(session.account?.email, 'carlos@example.invalid');
      expect(await session.authorized((token) async => token), 'access-2');
    },
  );

  for (final newerLogin in [false, true]) {
    test(
      newerLogin
          ? 'A late registration cannot replace a newer account'
          : 'A late registration cannot sign in after logout',
      () async {
        final started = Completer<void>();
        final release = Completer<http.Response>();
        var logins = 0;
        final api = client((request) async {
          switch (request.url.path) {
            case '/api/auth/registro/':
              started.complete();
              return release.future;
            case '/api/auth/token/':
              logins++;
              expect(
                jsonDecode(request.body)['email'],
                'carlos@example.invalid',
              );
              return json({
                'access': 'carlos-access',
                'refresh': 'carlos-refresh',
              });
            case '/api/auth/perfil/':
              return json({
                'nombre': 'Carlos',
                'email': 'carlos@example.invalid',
              });
            default:
              throw StateError('Unexpected route');
          }
        });
        addTearDown(api.close);
        final session = Session(api);
        addTearDown(session.dispose);
        await session.restore();
        final pending = session.register(
          'Ana',
          'ana@example.invalid',
          'test-password',
        );
        final failure = expectLater(pending, throwsA(isA<ApiException>()));
        await started.future;
        if (newerLogin) {
          await session.login('carlos@example.invalid', 'test-password');
        } else {
          await session.logout();
        }
        release.complete(json({'nombre': 'Ana'}, status: 201));
        await failure;
        expect(logins, newerLogin ? 1 : 0);
        expect(
          session.account?.email,
          newerLogin ? 'carlos@example.invalid' : null,
        );
      },
    );
  }

  test('Malformed credentials response reports an API error', () async {
    final api = client((request) async => json({'unexpected': true}));
    addTearDown(api.close);
    final session = Session(api);
    addTearDown(session.dispose);
    await session.restore();
    await expectLater(
      session.login('ana@example.invalid', 'test-password'),
      throwsA(isA<ApiException>()),
    );
    expect(session.signedIn, isFalse);
  });

  test(
    'Dispose while refresh is pending does not notify disposed listeners',
    () async {
      final started = Completer<void>();
      final release = Completer<http.Response>();
      final api = client((request) async {
        return switch (request.url.path) {
          '/api/auth/token/' => json({'access': 'old', 'refresh': 'refresh'}),
          '/api/auth/perfil/' => json({
            'nombre': 'Ana',
            'email': 'ana@example.invalid',
          }),
          '/api/auth/token/refresh/' => () {
            started.complete();
            return release.future;
          }(),
          _ => throw StateError('Unexpected route'),
        };
      });
      addTearDown(api.close);
      final session = Session(api);
      await session.restore();
      await session.login('ana@example.invalid', 'test-password');
      final old = session.authorized<Object?>((token) async {
        throw const ApiException('Expired', status: 401);
      });
      final failure = expectLater(old, throwsA(isA<ApiException>()));
      await started.future;
      session.dispose();
      release.complete(json({'detail': 'Expired'}, status: 401));
      await failure;
    },
  );
}
