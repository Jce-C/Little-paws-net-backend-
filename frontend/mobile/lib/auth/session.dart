import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../core/api_client.dart';

class Account {
  const Account({
    required this.name,
    required this.email,
    this.phone = '',
    this.safeRetries = false,
    this.adoptionEvaluation = false,
    this.demo = false,
  });
  final String name;
  final String email;
  final String phone;
  final bool safeRetries;
  final bool adoptionEvaluation;
  final bool demo;

  factory Account.fromJson(Map<String, dynamic> data) {
    final name = data['nombre'];
    final email = data['email'];
    final phone = data['telefono'] ?? '';
    if (name is! String ||
        email is! String ||
        email.trim().isEmpty ||
        phone is! String) {
      throw const ApiException('No pudimos verificar los datos de tu cuenta.');
    }
    return Account(
      name: name,
      email: email,
      phone: phone,
      safeRetries: data['reintentos_seguros'] == true,
      adoptionEvaluation: data['evaluacion_adopcion'] == true,
      demo: data['demostracion'] == true,
    );
  }
}

class Session extends ChangeNotifier {
  Session(this.api);

  final ApiClient api;
  final _storage = const FlutterSecureStorage();
  String? _access;
  String? _refresh;
  int _generation = 0;
  Future<String>? _renewal;
  Future<void> _storageWrites = Future.value();
  bool _disposed = false;
  bool _rememberSession = true;
  bool rememberPreference = false;
  String get _rememberKey =>
      'lpn_remember_${base64Url.encode(utf8.encode(api.base.origin))}';
  Future<bool> loadRememberPreference() async {
    try {
      rememberPreference = await _storage.read(key: _rememberKey) == '1';
    } on Exception {
      rememberPreference = false;
    }
    return rememberPreference;
  }

  Future<void> setRememberPreference(bool value) async {
    rememberPreference = value;
    _storageWrites = _storageWrites.catchError((Object _) {}).then((_) async {
      if (value) {
        await _storage.write(key: _rememberKey, value: '1');
      } else {
        await _storage.delete(key: _rememberKey);
      }
    });
    await _storageWrites;
  }

  Account? account;
  bool restoring = true;
  bool get signedIn => account != null;

  /// Changes only across authentication boundaries, not profile refreshes.
  int get identityRevision => _generation;

  String get _storageKey =>
      'lpn_refresh_${base64Url.encode(utf8.encode(api.base.origin))}';
  bool get _persist => api.base.scheme == 'https' && !kIsWeb;

  Future<void> restore() async {
    final generation = _generation;
    try {
      if (_persist) {
        final refresh = await _storage.read(key: _storageKey);
        _checkGeneration(generation);
        _refresh = refresh;
      }
      if (_refresh != null) {
        final profile = await authorized(
          (token) => api.get('/api/auth/perfil/', token: token),
        );
        _checkGeneration(generation);
        account = Account.fromJson(_object(profile));
      }
    } on ApiException catch (e) {
      if (generation == _generation && (e.status == 401 || e.status == 400)) {
        await _clear();
      }
    } on Exception {
      if (generation == _generation) await _clear();
    } finally {
      restoring = false;
      _notify();
    }
  }

  Future<void> login(
    String email,
    String password, {
    bool remember = true,
  }) async {
    _rememberSession = remember;
    final generation = ++_generation;
    _access = null;
    _refresh = null;
    _renewal = null;
    account = null;
    _notify();
    await _saveRefresh(null);
    _checkGeneration(generation);
    final result = _object(
      await api.post('/api/auth/token/', {
        'email': email.trim(),
        'password': password,
      }),
    );
    _checkGeneration(generation);
    final access = _token(result, 'access');
    final refresh = _token(result, 'refresh');
    final profile = await api.get('/api/auth/perfil/', token: access);
    _checkGeneration(generation);
    final verified = Account.fromJson(_object(profile));
    _access = access;
    _refresh = refresh;
    account = verified;
    await _saveRefresh(refresh);
    _checkGeneration(generation);
    _notify();
  }

  Future<void> register(
    String name,
    String email,
    String password, {
    bool remember = true,
  }) async {
    final generation = _generation;
    await api.post('/api/auth/registro/', {
      'nombre': name.trim(),
      'email': email.trim(),
      'password': password,
    });
    _checkGeneration(generation);
    await login(email, password, remember: remember);
  }

  Future<void> updateProfile({String? name, String? phone}) async {
    final generation = _generation;
    final identity = account?.email;
    if (identity == null) {
      throw const ApiException(
        'Inicia sesión para editar tu perfil.',
        status: 401,
      );
    }
    final result = await authorized(
      (token) => api.patch('/api/auth/perfil/', {
        if (name != null) 'nombre': name.trim(),
        if (phone != null) 'telefono': phone.trim(),
      }, token: token),
    );
    _checkGeneration(generation);
    final updated = Account.fromJson(_object(result));
    if (updated.email != identity) {
      throw const ApiException(
        'No pudimos verificar la actualización de tu perfil.',
      );
    }
    account = updated;
    _notify();
  }

  Future<T> authorized<T>(Future<T> Function(String token) operation) async {
    final generation = _generation;
    final token = _access ?? await _renew();
    try {
      final result = await operation(token);
      _checkGeneration(generation);
      return result;
    } on ApiException catch (error) {
      _checkGeneration(generation);
      if (error.status != 401) rethrow;
      final replacement = _access != null && _access != token
          ? _access!
          : await _renew();
      try {
        final result = await operation(replacement);
        _checkGeneration(generation);
        return result;
      } on ApiException catch (retryError) {
        if (generation == _generation && retryError.status == 401) {
          await _clear();
        }
        rethrow;
      }
    }
  }

  void _checkGeneration(int generation) {
    if (_disposed || generation != _generation) {
      throw const ApiException(
        'La sesión cambió. Vuelve a intentarlo.',
        status: 401,
      );
    }
  }

  Future<String> _renew() {
    if (_refresh == null) {
      throw const ApiException('Inicia sesión para continuar.', status: 401);
    }
    if (_renewal != null) return _renewal!;
    late final Future<String> renewal;
    renewal = _refreshSession(_refresh!, _generation).whenComplete(() {
      if (identical(_renewal, renewal)) _renewal = null;
    });
    _renewal = renewal;
    return renewal;
  }

  Future<String> _refreshSession(String refresh, int generation) async {
    try {
      final result = _object(
        await api.post('/api/auth/token/refresh/', {'refresh': refresh}),
      );
      final access = _token(result, 'access');
      final nextRefresh = result.containsKey('refresh')
          ? _token(result, 'refresh')
          : refresh;
      _checkGeneration(generation);
      _access = access;
      _refresh = nextRefresh;
      await _saveRefresh(_refresh);
      _checkGeneration(generation);
      return access;
    } on ApiException catch (error) {
      if (generation == _generation &&
          (error.status == 401 || error.status == 400)) {
        await _clear();
      }
      rethrow;
    }
  }

  Future<void> _saveRefresh(String? value) {
    if (!_persist) return Future.value();
    if (!_rememberSession) value = null;
    final storedValue = value;
    return _storageWrites = _storageWrites.then((_) async {
      try {
        if (storedValue == null) {
          await _storage.delete(key: _storageKey);
        } else {
          await _storage.write(key: _storageKey, value: storedValue);
        }
      } on Exception {
        // Session remains available in memory if secure storage is unavailable.
      }
    });
  }

  Future<void> _clear() async {
    ++_generation;
    _access = null;
    _refresh = null;
    _renewal = null;
    account = null;
    _notify();
    await _saveRefresh(null);
  }

  Future<void> logout() async {
    final refresh = _refresh;
    await _clear();
    if (refresh == null) return;
    try {
      await api.post('/api/auth/token/revoke/', {'refresh': refresh});
    } on ApiException {
      // Local access has already ended. The server token expires normally.
    }
  }

  void _notify() {
    if (!_disposed) notifyListeners();
  }

  Map<String, dynamic> _object(Object? value) {
    if (value is Map<String, dynamic>) return value;
    throw const ApiException('El servidor devolvió una respuesta inesperada.');
  }

  String _token(Map<String, dynamic> data, String field) {
    final value = data[field];
    if (value is String && value.trim().isNotEmpty) return value;
    throw const ApiException(
      'No pudimos confirmar el acceso. Intenta de nuevo.',
    );
  }

  @override
  void dispose() {
    _disposed = true;
    ++_generation;
    _renewal = null;
    _access = null;
    _refresh = null;
    account = null;
    super.dispose();
  }
}
