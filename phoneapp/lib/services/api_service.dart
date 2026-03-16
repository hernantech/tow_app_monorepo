import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:5001';
  // This is a shared secret between the app and backend, not a user credential.
  // It prevents unauthenticated callers from hitting the AI endpoint directly.
  // It is expected to be in the app binary — this is the standard approach for
  // mobile API keys. The actual LLM key (Anthropic) stays server-side only.
  // Must match the CHAT_API_KEY value in backend/.env.
  static const String _chatApiKey = 'y3x_3x-lzghfsIHvPon1q5EONwHe6ZM09zwUHR5IDao';
  static const _storage = FlutterSecureStorage();

  static Future<String> getDeviceId() async {
    var deviceId = await _storage.read(key: 'device_id');
    if (deviceId == null) {
      deviceId = 'dev_${DateTime.now().millisecondsSinceEpoch}_${Object().hashCode}';
      await _storage.write(key: 'device_id', value: deviceId);
    }
    return deviceId;
  }

  static Future<String?> getToken() async {
    return await _storage.read(key: 'access_token');
  }

  static Future<void> saveToken(String token) async {
    await _storage.write(key: 'access_token', value: token);
  }

  static Future<void> clearToken() async {
    await _storage.delete(key: 'access_token');
  }

  static Future<Map<String, String>> _authHeaders() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  static Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await saveToken(data['access_token']);
      return data;
    }
    throw Exception(jsonDecode(response.body)['error'] ?? 'Login failed');
  }

  static Future<Map<String, dynamic>> getMe() async {
    final headers = await _authHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/api/auth/me'),
      headers: headers,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Not authenticated');
  }

  static Future<List<dynamic>> getCases({String? status, int limit = 50, int offset = 0}) async {
    final headers = await _authHeaders();
    final params = <String, String>{
      'limit': limit.toString(),
      'offset': offset.toString(),
    };
    if (status != null) params['status'] = status;
    final uri = Uri.parse('$baseUrl/api/cases/').replace(queryParameters: params);
    final response = await http.get(uri, headers: headers);
    if (response.statusCode == 200) {
      return jsonDecode(response.body)['cases'];
    }
    throw Exception('Failed to load cases');
  }

  static Future<Map<String, dynamic>> getCase(int id) async {
    final headers = await _authHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl/api/cases/$id'),
      headers: headers,
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Case not found');
  }

  static Future<Map<String, dynamic>> updateCase(int id, Map<String, dynamic> updates) async {
    final headers = await _authHeaders();
    final response = await http.patch(
      Uri.parse('$baseUrl/api/cases/$id'),
      headers: headers,
      body: jsonEncode(updates),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to update case');
  }

  static Future<Map<String, dynamic>> addNote(int id, String note) async {
    final headers = await _authHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl/api/cases/$id/notes'),
      headers: headers,
      body: jsonEncode({'note': note}),
    );
    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to add note');
  }

  static Future<Map<String, dynamic>> sendChatMessage(String message, {String? userId}) async {
    final deviceId = await getDeviceId();
    final response = await http.post(
      Uri.parse('$baseUrl/api/chat'),
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': _chatApiKey,
        'X-Device-ID': deviceId,
      },
      body: jsonEncode({
        'message': message,
        if (userId != null) 'user_id': userId,
      }),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    if (response.statusCode == 429) {
      final data = jsonDecode(response.body);
      throw Exception(data['error'] ?? 'Rate limit exceeded');
    }
    throw Exception('Failed to send message');
  }
}
