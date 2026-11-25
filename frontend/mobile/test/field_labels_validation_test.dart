import 'dart:ui' show Tristate;
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:little_paws_net/auth/session.dart';
import 'package:little_paws_net/core/api_client.dart';
import 'package:little_paws_net/pets/personal_pet_screen.dart';
import 'package:little_paws_net/design/form_surfaces.dart';

void main() {
  testWidgets(
    'Leaving an invalid form before focus recovery does not touch disposed controls',
    (tester) async {
      final form = GlobalKey<FormState>();
      await tester.pumpWidget(
        MaterialApp(
          home: Material(
            child: Form(
              key: form,
              child: TextFormField(validator: (_) => 'Completa el dato'),
            ),
          ),
        ),
      );
      expect(validateLpnForm(form), isFalse);
      await tester.pumpWidget(const SizedBox());
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'Pet registration validates required fields even after scrolling to the photograph',
    (tester) async {
      var writes = 0;
      final api = ApiClient(
        base: Uri.parse('http://127.0.0.1:8016'),
        client: MockClient((r) async {
          Object data = {};
          if (r.url.path == '/api/auth/token/') {
            data = {'access': 'synthetic', 'refresh': 'synthetic-refresh'};
          } else if (r.url.path == '/api/auth/perfil/') {
            data = {'nombre': 'Persona QA', 'email': 'qa@example.invalid'};
          } else if (r.method != 'GET') {
            writes++;
          }
          return http.Response(
            jsonEncode(data),
            200,
            headers: {'content-type': 'application/json'},
          );
        }),
      );
      final session = Session(api);
      addTearDown(session.dispose);
      addTearDown(api.close);
      await session.restore();
      await session.login(
        'qa@example.invalid',
        'synthetic-password',
        remember: false,
      );
      await tester.pumpWidget(
        MaterialApp(home: PersonalPetScreen(session: session)),
      );
      await tester.pumpAndSettle();
      await tester.scrollUntilVisible(
        find.text('Fotografía de tu mascota'),
        400,
        scrollable: find.byType(Scrollable).first,
      );
      await tester.tap(find.byKey(const Key('personal-save')));
      await tester.pumpAndSettle();
      expect(writes, 0);
      final name = find.byKey(const Key('personal-nombre'));
      expect(
        tester
            .widget<EditableText>(
              find.descendant(of: name, matching: find.byType(EditableText)),
            )
            .focusNode
            .hasFocus,
        isTrue,
      );
      expect(find.text('Completa este dato.'), findsWidgets);
      await tester.enterText(name, 'Luna QA');
      await tester.pumpAndSettle();
      expect(
        find.text('Completa este dato.'),
        findsOneWidget,
        reason:
            'Correcting Name clears only that error without another submit.',
      );
      expect(writes, 0);
      expect(tester.takeException(), isNull);
    },
  );
  testWidgets(
    'External caption names the editable control exactly once after typing',
    (tester) async {
      final handle = tester.ensureSemantics();
      try {
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: LpnFieldLabel(label: 'Ciudad', child: TextFormField()),
            ),
          ),
        );
        await tester.enterText(find.byType(TextFormField), 'Riohacha');
        await tester.pumpAndSettle();
        final node = tester.getSemantics(find.byType(EditableText));
        expect(node.getSemanticsData().flagsCollection.isTextField, isTrue);
        expect(node.label, 'Ciudad');
        expect(node.value, 'Riohacha');
        final labels = <String>[];
        void visit(SemanticsNode node) {
          if (node.label.contains('Ciudad')) labels.add(node.label);
          node.visitChildren((child) {
            visit(child);
            return true;
          });
        }

        visit(
          tester
              .binding
              .renderViews
              .first
              .owner!
              .semanticsOwner!
              .rootSemanticsNode!,
        );
        expect(labels, ['Ciudad']);
      } finally {
        handle.dispose();
      }
    },
  );
  testWidgets(
    'External caption preserves separate choices and their selected state',
    (tester) async {
      final handle = tester.ensureSemantics();
      try {
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: LpnFieldLabel(
                label: 'Vivienda',
                child: Wrap(
                  children: [
                    ChoiceChip(
                      label: const Text('Casa'),
                      selected: true,
                      onSelected: (_) {},
                    ),
                    ChoiceChip(
                      label: const Text('Apartamento'),
                      selected: false,
                      onSelected: (_) {},
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
        final casa = tester.getSemantics(find.byType(ChoiceChip).first);
        final apartment = tester.getSemantics(find.byType(ChoiceChip).last);
        expect(casa.label, contains('Casa'));
        expect(apartment.label, contains('Apartamento'));
        expect(
          casa.getSemanticsData().flagsCollection.isSelected,
          Tristate.isTrue,
        );
        expect(
          apartment.getSemanticsData().flagsCollection.isSelected,
          Tristate.isFalse,
        );
      } finally {
        handle.dispose();
      }
    },
  );
  testWidgets(
    'External caption names a dropdown without repeating its visible title',
    (tester) async {
      final handle = tester.ensureSemantics();
      try {
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: LpnFieldLabel(
                label: 'Tenencia',
                child: DropdownButtonFormField<String>(
                  initialValue: 'own',
                  items: const [
                    DropdownMenuItem(value: 'own', child: Text('Propia')),
                  ],
                  onChanged: (_) {},
                ),
              ),
            ),
          ),
        );
        final node = tester.getSemantics(find.byType(DropdownButton<String>));
        expect(node.label, contains('Tenencia'));
        expect(node.label.split('Tenencia').length, 2);
      } finally {
        handle.dispose();
      }
    },
  );
  for (final kind in ['texto', 'selector', 'opciones']) {
    testWidgets(
      'Validation reveals and focuses first invalid $kind while preserving valid data',
      (tester) async {
        final form = GlobalKey<FormState>();
        final control = GlobalKey();
        final valid = TextEditingController(text: 'Dato conservado');
        addTearDown(valid.dispose);
        Widget input;
        if (kind == 'texto') {
          input = TextFormField(
            key: control,
            decoration: const InputDecoration(labelText: 'Ciudad'),
            validator: (v) =>
                v == null || v.isEmpty ? 'Indica la ciudad' : null,
          );
        } else if (kind == 'selector') {
          input = DropdownButtonFormField<String>(
            key: control,
            decoration: const InputDecoration(labelText: 'Ciudad'),
            items: const [
              DropdownMenuItem(value: 'rio', child: Text('Riohacha')),
            ],
            onChanged: (_) {},
            validator: (v) => v == null ? 'Selecciona la ciudad' : null,
          );
        } else {
          input = FormField<bool>(
            key: control,
            validator: (v) => v == true ? null : 'Selecciona una opción',
            builder: (state) => Column(
              children: [
                TextButton(
                  onPressed: () => state.didChange(true),
                  child: const Text('Casa'),
                ),
                if (state.hasError) Text(state.errorText!),
              ],
            ),
          );
        }
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: Form(
                key: form,
                child: SingleChildScrollView(
                  child: Column(
                    children: [
                      TextFormField(controller: valid),
                      const SizedBox(height: 700),
                      input,
                      const SizedBox(height: 100),
                      FilledButton(
                        onPressed: () => validateLpnForm(form),
                        child: const Text('Continuar'),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        );
        await tester.ensureVisible(find.text('Continuar'));
        await tester.tap(find.text('Continuar'));
        await tester.pumpAndSettle();
        expect(form.currentState!.validateGranularly(), isNotEmpty);
        final rect = tester.getRect(find.byKey(control));
        expect(rect.top, greaterThanOrEqualTo(0));
        expect(rect.top, lessThan(400));
        expect(valid.text, 'Dato conservado');
        var focusedInside = false;
        FocusManager.instance.primaryFocus!.context!.visitAncestorElements((
          element,
        ) {
          focusedInside = identical(
            element,
            tester.element(find.byKey(control)),
          );
          return !focusedInside;
        });
        expect(focusedInside, isTrue);
        if (kind == 'texto') {
          await tester.enterText(find.byKey(control), 'Riohacha');
        } else if (kind == 'selector') {
          await tester.sendKeyEvent(LogicalKeyboardKey.space);
          await tester.pumpAndSettle();
          await tester.tap(find.text('Riohacha').last);
          await tester.pumpAndSettle();
        } else {
          await tester.sendKeyEvent(LogicalKeyboardKey.space);
          await tester.pumpAndSettle();
        }
        expect(validateLpnForm(form), isTrue);
        await tester.pumpAndSettle();
        expect(tester.takeException(), isNull);
      },
    );
  }
}
