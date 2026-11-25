import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:little_paws_net/design/lpn_theme.dart';
import 'package:little_paws_net/design/adoption_form_style.dart';
import 'package:little_paws_net/design/community_surface.dart';

void main() {
  test(
    'Small text palette pairs meet 4.5 contrast against reading surfaces',
    () {
      final text = {
        'ink': LpnColors.ink,
        'muted': LpnColors.muted,
        'sage': LpnColors.sage,
      };
      final surfaces = {
        for (var i = 0; i < evaluationTints.length; i++)
          'evaluation-$i': evaluationTints[i],
        'paper': LpnColors.paper,
        'canvas': LpnColors.canvas,
        'welcome': LpnColors.welcome,
        'butter': LpnColors.butter,
        'blush': LpnColors.blush,
        'sageSoft': LpnColors.sageSoft,
        for (var i = 0; i < CommunitySurface.tones.length; i++)
          'community-$i': CommunitySurface.tones[i],
      };
      double ratio(Color a, Color b) {
        final x = a.computeLuminance();
        final y = b.computeLuminance();
        return (math.max(x, y) + .05) / (math.min(x, y) + .05);
      }

      for (final fg in text.entries) {
        for (final bg in surfaces.entries) {
          expect(
            ratio(fg.value, bg.value),
            greaterThanOrEqualTo(4.5),
            reason: '${fg.key} text on ${bg.key}',
          );
        }
      }
      expect(
        ratio(LpnColors.paper, LpnColors.charcoal),
        greaterThanOrEqualTo(4.5),
      );
    },
  );
}
