class BodyShop {
  final String id;
  final String name;
  final String address;
  final double lat;
  final double lng;
  final bool isPartner;

  BodyShop({
    required this.id,
    required this.name,
    required this.address,
    required this.lat,
    required this.lng,
    required this.isPartner,
  });

  factory BodyShop.fromJson(Map<String, dynamic> json) {
    return BodyShop(
      id: json['id'] as String,
      name: json['name'] as String,
      address: json['address'] as String,
      lat: (json['lat'] as num).toDouble(),
      lng: (json['lng'] as num).toDouble(),
      isPartner: json['isPartner'] as bool,
    );
  }
}
