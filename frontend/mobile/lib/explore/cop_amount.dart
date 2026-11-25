/// Decimal COP values stay exact; binary floating point never prices an order.
class CopAmount {
  const CopAmount._(this.cents);
  final BigInt cents;
  static CopAmount? parse(Object? value) {
    if (value is! String ||
        !RegExp(r'^\d{1,24}(\.\d{1,2})?$').hasMatch(value)) {
      return null;
    }
    final parts = value.split('.');
    final fraction = parts.length == 1 ? '00' : parts[1].padRight(2, '0');
    return CopAmount._(
      BigInt.parse(parts[0]) * BigInt.from(100) + BigInt.parse(fraction),
    );
  }

  CopAmount times(int quantity) {
    if (quantity < 0) throw ArgumentError.value(quantity);
    return CopAmount._(cents * BigInt.from(quantity));
  }

  String get formatted {
    final whole = (cents ~/ BigInt.from(100)).toString().replaceAllMapped(
      RegExp(r'\B(?=(\d{3})+(?!\d))'),
      (_) => '.',
    );
    final fraction = (cents % BigInt.from(100)).toString().padLeft(2, '0');
    return '\$$whole${fraction == '00' ? '' : ',$fraction'} COP';
  }
}
