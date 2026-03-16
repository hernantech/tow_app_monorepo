import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../models/intake_case.dart';

class CasesProvider extends ChangeNotifier {
  List<IntakeCase> _cases = [];
  List<IntakeCase> get cases => _cases;

  Map<String, dynamic>? _selectedCase;
  Map<String, dynamic>? get selectedCase => _selectedCase;

  String? _statusFilter;
  String? get statusFilter => _statusFilter;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _error;
  String? get error => _error;

  Future<void> loadCases({String? status}) async {
    _isLoading = true;
    _statusFilter = status;
    _error = null;
    notifyListeners();

    try {
      final data = await ApiService.getCases(status: status);
      _cases = data.map((json) => IntakeCase.fromJson(json)).toList();
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
  }

  Future<void> loadCaseDetail(int id) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _selectedCase = await ApiService.getCase(id);
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
  }

  Future<void> updateCaseStatus(int id, String status) async {
    try {
      await ApiService.updateCase(id, {'status': status});
      await loadCaseDetail(id);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> addNote(int id, String note) async {
    try {
      await ApiService.addNote(id, note);
      await loadCaseDetail(id);
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }
}
