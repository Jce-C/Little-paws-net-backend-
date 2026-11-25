import '../design/form_surfaces.dart';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../core/api_client.dart';
import '../design/lpn_app_bar.dart';
import '../adoption/adoption_screens.dart' show messageFor;
import '../explore/session_action_gate.dart';
import 'session.dart';

class AvatarData {
  const AvatarData._(this.path);
  final Uri path;
  static AvatarData? parse(Object? value) {
    if (value is! Map) return null;
    final path = value['url'];
    if (path is! String ||
        !RegExp(
          r'^/api/comunidad/perfiles/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/foto/$',
        ).hasMatch(path)) {
      return null;
    }
    for (final key in ['ancho', 'alto', 'bytes']) {
      final n = value[key];
      if (n is! int || n < 1 || n > (key == 'bytes' ? 64 * 1024 : 256)) {
        return null;
      }
    }
    return AvatarData._(Uri.parse(path));
  }
}

class PublicAvatar extends StatelessWidget {
  const PublicAvatar({
    super.key,
    required this.value,
    required this.name,
    required this.origin,
    this.radius = 20,
  });
  final Object? value;
  final String name;
  final Uri origin;
  final double radius;
  @override
  Widget build(BuildContext context) {
    final photo = AvatarData.parse(value);
    final initial = name.trim().isEmpty
        ? '?'
        : name.trim().characters.first.toUpperCase();
    final fallback = Center(
      child: Text(
        initial,
        style: TextStyle(fontSize: radius * .7, fontWeight: FontWeight.w700),
      ),
    );
    return ExcludeSemantics(
      child: ClipOval(
        child: SizedBox.square(
          dimension: radius * 2,
          child: ColoredBox(
            color: const Color(0xffe7ecfa),
            child: photo == null
                ? fallback
                : Image.network(
                    origin.resolveUri(photo.path).toString(),
                    fit: BoxFit.cover,
                    cacheWidth:
                        (radius * 2 * MediaQuery.devicePixelRatioOf(context))
                            .ceil()
                            .clamp(40, 256),
                    frameBuilder: (context, child, frame, sync) =>
                        frame != null || sync ? child : fallback,
                    errorBuilder: (context, error, stack) => fallback,
                  ),
          ),
        ),
      ),
    );
  }
}

class AvatarScreen extends StatelessWidget {
  const AvatarScreen({super.key, required this.session, this.choose});
  final Session session;
  final Future<Uint8List?> Function()? choose;
  @override
  Widget build(BuildContext context) => SessionActionGate(
    session: session,
    title: 'Foto de perfil',
    message: 'Inicia sesión para cambiar tu foto.',
    form: (identity) =>
        _AvatarForm(key: identity, session: session, choose: choose),
  );
}

class _AvatarForm extends StatefulWidget {
  const _AvatarForm({super.key, required this.session, this.choose});
  final Session session;
  final Future<Uint8List?> Function()? choose;
  @override
  State<_AvatarForm> createState() => _AvatarFormState();
}

class _AvatarFormState extends State<_AvatarForm> {
  Uint8List? _selected;
  Object? _published;
  bool _busy = false,
      _consent = false,
      _leave = false,
      _uncertain = false,
      _confirming = false;
  String? _error;
  late Future<void> _data = _load();
  Future<void> _load() async {
    final raw = await widget.session.authorized(
      (token) =>
          widget.session.api.get('/api/auth/foto-publica/', token: token),
    );
    if (raw is! Map ||
        !raw.containsKey('foto_publica') ||
        raw['foto_publica'] != null &&
            AvatarData.parse(raw['foto_publica']) == null) {
      throw const ApiException('No pudimos verificar la foto publicada.');
    }
    if (mounted) {
      setState(() {
        _published = raw['foto_publica'];
        _uncertain = false;
      });
    }
  }

  Future<void> _pick() async {
    if (_busy) return;
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      Uint8List? bytes;
      if (widget.choose != null) {
        bytes = await widget.choose!();
      } else {
        final picker = ImagePicker();
        // Never restore a previous account's interrupted selection.
        if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
          await picker.retrieveLostData();
        }
        final file = await picker.pickImage(
          source: ImageSource.gallery,
          requestFullMetadata: false,
        );
        if (file != null) {
          if (await file.length() > 5 * 1024 * 1024) {
            throw const ApiException('Elige una imagen de hasta 5 MB.');
          }
          bytes = await file.readAsBytes();
        }
      }
      if (bytes != null && mounted) {
        if (bytes.isEmpty || bytes.length > 5 * 1024 * 1024) {
          throw const ApiException('Elige una imagen de hasta 5 MB.');
        }
        setState(() {
          _selected = bytes;
          _consent = false;
        });
      }
    } on Exception catch (e) {
      if (mounted) {
        setState(
          () =>
              _error = messageFor(e, 'No pudimos abrir la imagen. Elige otra.'),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _save({bool remove = false}) async {
    if (_busy || _uncertain || _confirming) return;
    if (!remove && (_selected == null || !_consent)) {
      setState(() => _error = 'Elige una foto y autoriza su publicación.');
      return;
    }
    if (remove) {
      _confirming = true;
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('¿Retirar tu foto pública?'),
          content: const Text('Se mostrará tu inicial en Comunidad.'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Cancelar'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Retirar foto'),
            ),
          ],
        ),
      );
      _confirming = false;
      if (confirmed != true || !mounted) return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      if (remove) {
        await widget.session.authorized(
          (token) => widget.session.api.delete(
            '/api/auth/foto-publica/',
            token: token,
          ),
        );
        if (mounted) setState(() => _published = null);
      } else {
        final raw = await widget.session.authorized(
          (token) =>
              widget.session.api.uploadProfilePhoto(_selected!, token: token),
        );
        if (raw is! Map || AvatarData.parse(raw['foto_publica']) == null) {
          throw const ApiException('No pudimos confirmar la publicación.');
        }
        if (mounted) setState(() => _published = raw['foto_publica']);
      }
      if (mounted) {
        setState(() {
          _selected = null;
          _consent = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(remove ? 'Foto retirada.' : 'Foto publicada.'),
          ),
        );
      }
    } on Exception catch (e) {
      if (mounted) {
        setState(() {
          _error = messageFor(e, 'No pudimos confirmar el cambio.');
          _uncertain =
              e is! ApiException || e.status == null || e.status! >= 500;
        });
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _cancel() async {
    if (_busy) return;
    if (_selected != null) {
      final discard = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('¿Descartar la foto seleccionada?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Seguir editando'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Descartar'),
            ),
          ],
        ),
      );
      if (discard != true || !mounted) return;
    }
    if (!mounted) return;
    setState(() => _leave = true);
    await WidgetsBinding.instance.endOfFrame;
    if (mounted) Navigator.pop(context, true);
  }

  @override
  Widget build(BuildContext context) => PopScope(
    canPop: _leave || !_busy && _selected == null,
    onPopInvokedWithResult: (didPop, _) {
      if (!didPop) _cancel();
    },
    child: Scaffold(
      appBar: lpnAppBar(context, 'Foto de perfil'),
      bottomNavigationBar: LpnKeyboardSafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (_error != null)
                Semantics(
                  liveRegion: true,
                  child: Text(
                    _error!,
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                ),
              Wrap(
                alignment: WrapAlignment.end,
                spacing: 12,
                children: [
                  TextButton(
                    onPressed: _busy ? null : _cancel,
                    child: const Text('Cerrar'),
                  ),
                  if (_selected != null)
                    FilledButton(
                      onPressed: _busy || _uncertain || !_consent
                          ? null
                          : () => _save(),
                      child: Text(_busy ? 'Publicando…' : 'Publicar foto'),
                    ),
                  if (_uncertain)
                    TextButton(
                      onPressed: _busy
                          ? null
                          : () => setState(() {
                              _data = _load();
                            }),
                      child: const Text('Comprobar estado'),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
      body: FutureBuilder<void>(
        future: _data,
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return Center(
              child: TextButton(
                onPressed: () => setState(() {
                  _data = _load();
                }),
                child: Text(
                  '${messageFor(snapshot.error, 'No pudimos consultar tu foto.')} Reintentar',
                ),
              ),
            );
          }
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          return ListView(
            padding: const EdgeInsets.all(24),
            children: [
              Center(
                child: _selected == null
                    ? PublicAvatar(
                        value: _published,
                        name: widget.session.account?.name ?? '',
                        origin: widget.session.api.base,
                        radius: 56,
                      )
                    : ClipOval(
                        child: Image.memory(
                          _selected!,
                          width: 112,
                          height: 112,
                          fit: BoxFit.cover,
                          errorBuilder: (_, error, stack) =>
                              const Icon(Icons.broken_image_outlined, size: 80),
                        ),
                      ),
              ),
              const SizedBox(height: 24),
              OutlinedButton.icon(
                onPressed: _busy ? null : _pick,
                icon: const Icon(Icons.photo_library_outlined),
                label: const Text('Elegir foto'),
              ),
              const SizedBox(height: 12),
              const Text(
                'Tu foto será pública junto a tus mensajes. JPEG, PNG o WebP; hasta 5 MB.',
              ),
              if (_selected != null)
                CheckboxListTile(
                  contentPadding: EdgeInsets.zero,
                  value: _consent,
                  onChanged: _busy
                      ? null
                      : (v) => setState(() => _consent = v == true),
                  title: const Text('Quiero mostrar esta foto en Comunidad.'),
                ),
              if (_published != null)
                TextButton(
                  onPressed: _busy || _uncertain
                      ? null
                      : () => _save(remove: true),
                  child: const Text('Retirar foto pública'),
                ),
            ],
          );
        },
      ),
    ),
  );
}
