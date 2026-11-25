import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/main.dart';

void main() {
  test(
    'A build without an API origin never silently targets an old service',
    () {
      expect(ApiClient.fromEnvironment, throwsArgumentError);
    },
  );
  testWidgets(
    'Unconfigured application displays a usable notice without creating a network client',
    (tester) async {
      var clients = 0;
      final app = HttpOverrides.runZoned(
        configuredApp,
        createHttpClient: (_) {
          clients++;
          throw StateError('No network client expected');
        },
      );
      await tester.pumpWidget(app);
      await tester.pump(const Duration(seconds: 2));
      expect(find.text('Esta versión aún no está conectada'), findsOneWidget);
      expect(find.byType(TextField), findsNothing);
      expect(clients, 0);
      expect(tester.takeException(), isNull);
    },
  );
}
