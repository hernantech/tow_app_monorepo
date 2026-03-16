import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../models/body_shop.dart';

class ShopMap extends StatelessWidget {
  final List<BodyShop> shops;
  final BodyShop? selectedShop;
  final ValueChanged<BodyShop> onShopTapped;

  const ShopMap({
    super.key,
    required this.shops,
    required this.selectedShop,
    required this.onShopTapped,
  });

  // Center on Riverside, CA
  static const _riversideCenter = LatLng(33.9425, -117.3950);

  @override
  Widget build(BuildContext context) {
    final center = selectedShop != null
        ? LatLng(selectedShop!.lat, selectedShop!.lng)
        : _riversideCenter;

    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: SizedBox(
        height: 260,
        child: FlutterMap(
          options: MapOptions(
            initialCenter: center,
            initialZoom: 12.0,
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.example.tow_app',
            ),
            MarkerLayer(
              markers: shops.map((shop) {
                final isSelected = selectedShop?.id == shop.id;
                return Marker(
                  point: LatLng(shop.lat, shop.lng),
                  width: isSelected ? 48 : 36,
                  height: isSelected ? 48 : 36,
                  child: GestureDetector(
                    onTap: () => onShopTapped(shop),
                    child: Icon(
                      Icons.location_on,
                      color: isSelected
                          ? Colors.blue
                          : shop.isPartner
                              ? Colors.green
                              : Colors.red,
                      size: isSelected ? 48 : 36,
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}
