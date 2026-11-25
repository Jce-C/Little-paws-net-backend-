import 'package:flutter/material.dart';

import '../adoption/adoption_screens.dart' show StatusPanel;
import '../auth/account_screen.dart';
import '../auth/session.dart';
import '../design/lpn_app_bar.dart';

/// Drafts and receipts belong to one signed-in identity, never the next one.
class SessionActionGate extends StatelessWidget {
  const SessionActionGate({
    super.key,
    required this.session,
    required this.title,
    required this.message,
    required this.form,
  });
  final Session session;
  final String title, message;
  final Widget Function(Key identity) form;

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: session,
    builder: (context, _) {
      if (session.restoring) {
        return Scaffold(
          appBar: lpnAppBar(context, title),
          body: const Center(child: CircularProgressIndicator()),
        );
      }
      if (!session.signedIn) {
        return Scaffold(
          appBar: lpnAppBar(context, title),
          body: SingleChildScrollView(
            child: StatusPanel(
              message: message,
              action: () => openLogin(context, session),
              actionLabel: 'Iniciar sesión',
            ),
          ),
        );
      }
      return form(ValueKey((session.identityRevision, session.account!.email)));
    },
  );
}
