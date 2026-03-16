import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/body_shop.dart';

class RequestProvider extends ChangeNotifier {
  List<BodyShop> _shops = [];
  List<BodyShop> get shops => _shops;

  BodyShop? _selectedShop;
  BodyShop? get selectedShop => _selectedShop;

  String _currentLocation = '';
  String get currentLocation => _currentLocation;

  bool _isLoading = true;
  bool get isLoading => _isLoading;

  Future<void> loadShops() async {
    try {
      final String response =
          await rootBundle.loadString('assets/body_shops.json');
      final List<dynamic> data = json.decode(response);
      _shops = data.map((json) => BodyShop.fromJson(json)).toList();
    } catch (e) {
      debugPrint("Error loading shops JSON: $e");
      _shops = [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void setLocation(String location) {
    _currentLocation = location;
    notifyListeners();
  }

  void selectShop(BodyShop? shop) {
    _selectedShop = shop;
    notifyListeners();
  }

  double get estimatedPrice {
    if (_selectedShop == null) return 0.0;
    return _selectedShop!.isPartner ? 0.0 : 150.0;
  }

  bool get isReadyToSubmit {
    return _currentLocation.trim().isNotEmpty && _selectedShop != null;
  }

  void reset() {
    _selectedShop = null;
    _currentLocation = '';
    notifyListeners();
  }
}
