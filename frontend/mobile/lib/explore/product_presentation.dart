import 'package:flutter/material.dart';

import 'cop_amount.dart';
import 'product_photo.dart';

int? productStock(Map<String, dynamic> row) {
  final value = row['existencias'];
  return value is int && value >= 0 ? value : null;
}

class ProductPresentation extends StatelessWidget {
  const ProductPresentation({
    super.key,
    required this.row,
    required this.origin,
  });
  final Map<String, dynamic> row;
  final Uri origin;
  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, constraints) {
      final stock = productStock(row);
      final info = Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${row['categoria'] ?? 'Producto'}',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 6),
          Text(
            '${row['nombre'] ?? 'Producto'}',
            style: Theme.of(context).textTheme.headlineSmall,
          ),
          if ('${row['tienda'] ?? ''}'.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text('${row['tienda']}'),
            ),
          const SizedBox(height: 16),
          Text(
            CopAmount.parse(row['precio'])?.formatted ?? 'Precio no disponible',
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 6),
          Text(
            stock == null
                ? 'Disponibilidad no confirmada'
                : stock == 0
                ? 'Agotado'
                : '$stock disponibles',
          ),
        ],
      );
      final photo = ClipRRect(
        borderRadius: BorderRadius.circular(22),
        child: SizedBox.square(
          dimension: 128,
          child: PublicProductImage(row: row, origin: origin),
        ),
      );
      if (constraints.maxWidth < 300 ||
          MediaQuery.textScalerOf(context).scale(14) >= 22) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [photo, const SizedBox(height: 20), info],
        );
      }
      return Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          photo,
          const SizedBox(width: 20),
          Expanded(child: info),
        ],
      );
    },
  );
}
