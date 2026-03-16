import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  bool _isAuthenticated = false;
  bool get isAuthenticated => _isAuthenticated;

  Map<String, dynamic>? _operator;
  Map<String, dynamic>? get operator => _operator;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _error;
  String? get error => _error;

  Future<void> checkAuth() async {
    try {
      final token = await ApiService.getToken();
      if (token != null) {
        final me = await ApiService.getMe();
        _operator = me['operator'];
        _isAuthenticated = true;
      }
    } catch (_) {
      _isAuthenticated = false;
      _operator = null;
      await ApiService.clearToken();
    }
    notifyListeners();
  }

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final data = await ApiService.login(username, password);
      _operator = data['operator'];
      _isAuthenticated = true;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString().replaceFirst('Exception: ', '');
      _isAuthenticated = false;
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await ApiService.clearToken();
    _isAuthenticated = false;
    _operator = null;
    _error = null;
    notifyListeners();
  }
}
