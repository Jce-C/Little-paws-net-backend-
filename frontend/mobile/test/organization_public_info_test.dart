import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/explore/organization_public_info.dart';

void main() {
  testWidgets(
    'Only explicitly public contact is shown, never internal WhatsApp',
    (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: OrganizationPublicInfo(
                row: {
                  'whatsapp': '3009991234',
                  'descripcion': 'Texto anterior',
                  'perfil_publico': {
                    'descripcion': 'Texto publicado',
                    'servicios': 'Orientación',
                    'correo': 'publico@example.invalid',
                    'telefono': '+57 300 123 4567',
                  },
                },
              ),
            ),
          ),
        ),
      );
      expect(find.text('Texto publicado'), findsOneWidget);
      expect(find.text('Texto anterior'), findsNothing);
      expect(find.text('3009991234'), findsNothing);
      expect(find.text('publico@example.invalid'), findsOneWidget);
      expect(find.text('Servicios'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Legacy organizations retain description and honest empty state',
    (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: OrganizationPublicInfo(
              row: {'descripcion': 'Descripción de la entidad'},
            ),
          ),
        ),
      );
      expect(find.text('Descripción de la entidad'), findsOneWidget);
      expect(
        find.text('Contacto y servicios: no publicados en el catálogo.'),
        findsOneWidget,
      );
    },
  );
}
