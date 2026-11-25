import 'package:flutter/material.dart';

import 'lpn_theme.dart';

/// Validate once and reveal the first invalid control after errors are laid out.
bool validateLpnForm(GlobalKey<FormState> key) {
  final form = key.currentState;
  if (form == null) return false;
  final invalid = form.validateGranularly();
  if (invalid.isEmpty) return true;
  final first = invalid.first;
  WidgetsBinding.instance.addPostFrameCallback((_) {
    if (!first.mounted) return;
    FocusNode? editable, fallback;
    void visit(Element element) {
      final widget = element.widget;
      if (widget is EditableText) editable ??= widget.focusNode;
      final node = Focus.maybeOf(element, createDependency: false);
      if (fallback == null &&
          node != null &&
          node.canRequestFocus &&
          !node.skipTraversal) {
        var belongsToField = false;
        node.context?.visitAncestorElements((ancestor) {
          belongsToField = identical(ancestor, first.context);
          return !belongsToField;
        });
        if (belongsToField) fallback = node;
      }
      element.visitChildElements(visit);
    }

    first.context.visitChildElements(visit);
    (editable ?? fallback)?.requestFocus();
    Scrollable.ensureVisible(
      first.context,
      alignment: .1,
      duration: MediaQuery.disableAnimationsOf(first.context)
          ? Duration.zero
          : const Duration(milliseconds: 180),
    );
  });
  return false;
}

abstract final class LpnFormPalette {
  static const tones = [
    Color(0xffedf1fc),
    Color(0xffedf4e9),
    Color(0xfffff2d9),
    Color(0xfff8e9ed),
    Color(0xfff0eafa),
  ];
}

/// Bounded forms keep every field mounted so off-screen inputs still validate.
/// Use lazy lists for catalogs, not for a single form's registered validators.
class LpnFormScrollView extends StatelessWidget {
  const LpnFormScrollView({
    super.key,
    this.controller,
    this.padding,
    required this.children,
  });
  final ScrollController? controller;
  final EdgeInsetsGeometry? padding;
  final List<Widget> children;
  @override
  Widget build(BuildContext context) => SingleChildScrollView(
    controller: controller,
    padding: padding,
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: children,
    ),
  );
}

/// Reading surfaces stay quiet; the glass layer belongs to navigation/actions.
class LpnFormSection extends StatelessWidget {
  const LpnFormSection({
    super.key,
    required this.title,
    required this.icon,
    required this.children,
    this.description,
    this.tone = 0,
  });
  final int tone;
  final String title;
  final IconData icon;
  final String? description;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: LpnFormPalette.tones[tone % LpnFormPalette.tones.length],
      borderRadius: BorderRadius.circular(20),
      border: Border.all(
        color: MediaQuery.highContrastOf(context)
            ? LpnColors.sage
            : LpnColors.controlEdge.withValues(alpha: .45),
      ),
      boxShadow: LpnMaterials.solid(context)
          ? null
          : const [
              BoxShadow(
                color: Color(0x0a423222),
                blurRadius: 20,
                offset: Offset(0, 6),
              ),
            ],
    ),
    child: Material(
      type: MaterialType.transparency,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: LpnColors.paper,
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, size: 20, color: LpnColors.sage),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Semantics(
                    header: true,
                    child: Text(
                      title,
                      style: const TextStyle(
                        fontSize: 16,
                        height: 1.3,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
          if (description != null) ...[
            const SizedBox(height: 12),
            Text(
              description!,
              style: const TextStyle(
                fontSize: 14,
                height: 1.5,
                color: LpnColors.muted,
              ),
            ),
          ],
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 12),
            child: Divider(height: 1, color: Color(0x338a7c70)),
          ),
          ...children,
        ],
      ),
    ),
  );
}

class LpnFieldLabel extends StatelessWidget {
  const LpnFieldLabel({super.key, required this.label, required this.child});
  final String label;
  final Widget child;
  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      ExcludeSemantics(
        child: Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            height: 1.4,
          ),
        ),
      ),
      const SizedBox(height: 6),
      Semantics(label: label, child: child),
    ],
  );
}

/// Use only in Scaffold.bottomNavigationBar; body footers are already resized.
class LpnKeyboardSafeArea extends StatelessWidget {
  const LpnKeyboardSafeArea({super.key, this.top = false, required this.child});
  final bool top;
  final Widget child;
  @override
  Widget build(BuildContext context) => _keyboardLeavesRoom(context)
      ? Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.viewInsetsOf(context).bottom,
          ),
          child: SafeArea(top: top, child: child),
        )
      : const SizedBox.shrink();
}

// A landscape IME can leave less than an app bar and an editable line. Reserve
// that space for the draft; native keyboard dismissal restores the actions.
bool _keyboardLeavesRoom(BuildContext context) {
  final media = MediaQuery.of(context);
  return media.viewInsets.bottom == 0 ||
      media.size.height - media.viewInsets.bottom >= 180;
}

class LpnActionBar extends StatelessWidget {
  const LpnActionBar({
    super.key,
    required this.child,
    this.avoidKeyboard = false,
  });
  final Widget child;

  /// Set for Scaffold.bottomNavigationBar; leave false inside the resized body.
  final bool avoidKeyboard;
  @override
  Widget build(BuildContext context) =>
      avoidKeyboard && !_keyboardLeavesRoom(context)
      ? const SizedBox.shrink()
      : Padding(
          padding: EdgeInsets.only(
            bottom: avoidKeyboard ? MediaQuery.viewInsetsOf(context).bottom : 0,
          ),
          child: DecoratedBox(
            decoration: const BoxDecoration(
              color: LpnColors.canvas,
              border: Border(top: BorderSide(color: LpnColors.line)),
            ),
            child: SafeArea(
              top: false,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                child: child,
              ),
            ),
          ),
        );
}

class LpnStepProgress extends StatelessWidget {
  const LpnStepProgress({
    super.key,
    required this.step,
    required this.titles,
    required this.icons,
  });
  final int step;
  final List<String> titles;
  final List<IconData> icons;
  @override
  Widget build(BuildContext context) => Semantics(
    label: 'Paso ${step + 1} de ${titles.length}: ${titles[step]}',
    child: ExcludeSemantics(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(
            'Paso ${step + 1} de ${titles.length}: ${titles[step]}',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              for (var i = 0; i < titles.length; i++) ...[
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: i <= step ? LpnColors.sage : LpnColors.paper,
                    border: Border.all(
                      color: i <= step ? LpnColors.sage : LpnColors.controlEdge,
                    ),
                  ),
                  child: Icon(
                    i < step ? Icons.check : icons[i],
                    size: 16,
                    color: i <= step ? LpnColors.paper : LpnColors.muted,
                  ),
                ),
                if (i < titles.length - 1)
                  Expanded(
                    child: Container(
                      height: 2,
                      color: i < step ? LpnColors.sage : LpnColors.line,
                    ),
                  ),
              ],
            ],
          ),
        ],
      ),
    ),
  );
}
