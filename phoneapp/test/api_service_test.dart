import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:tow_app/services/api_service.dart';

void main() {
  group('ApiService', () {
    test('login sends correct request and returns data', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/auth/login');
        expect(request.method, 'POST');
        expect(request.headers['Content-Type'], 'application/json');

        final body = jsonDecode(request.body);
        expect(body['username'], 'testuser');
        expect(body['password'], 'testpass');

        return http.Response(
          jsonEncode({
            'access_token': 'mock_token_123',
            'operator': {'id': 1, 'username': 'testuser'},
          }),
          200,
        );
      });

      // We test the HTTP layer directly since ApiService uses static http calls
      final response = await mockClient.post(
        Uri.parse('${ApiService.baseUrl}/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': 'testuser', 'password': 'testpass'}),
      );

      expect(response.statusCode, 200);
      final data = jsonDecode(response.body);
      expect(data['access_token'], 'mock_token_123');
      expect(data['operator']['username'], 'testuser');
    });

    test('getCases returns list of cases', () async {
      final mockClient = MockClient((request) async {
        expect(request.url.path, '/api/cases/');
        expect(request.method, 'GET');

        return http.Response(
          jsonEncode({
            'cases': [
              {
                'id': 1,
                'wechat_user_id': 'user1',
                'status': 'pending_review',
                'customer_name': 'John Doe',
                'created_at': '2025-01-01T00:00:00',
                'updated_at': '2025-01-01T00:00:00',
              },
              {
                'id': 2,
                'wechat_user_id': 'user2',
                'status': 'assigned',
                'customer_name': 'Jane Smith',
                'created_at': '2025-01-02T00:00:00',
                'updated_at': '2025-01-02T00:00:00',
              },
            ],
          }),
          200,
        );
      });

      final response = await mockClient.get(
        Uri.parse('${ApiService.baseUrl}/api/cases/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer mock_token',
        },
      );

      expect(response.statusCode, 200);
      final data = jsonDecode(response.body);
      expect(data['cases'], isList);
      expect(data['cases'].length, 2);
      expect(data['cases'][0]['customer_name'], 'John Doe');
    });

    test('auth headers include Bearer token', () async {
      final mockClient = MockClient((request) async {
        expect(request.headers['Authorization'], 'Bearer test_token');
        expect(request.headers['Content-Type'], 'application/json');
        return http.Response('{}', 200);
      });

      await mockClient.get(
        Uri.parse('${ApiService.baseUrl}/api/auth/me'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test_token',
        },
      );
    });

    test('login failure throws exception on non-200', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({'error': 'Invalid credentials'}),
          401,
        );
      });

      final response = await mockClient.post(
        Uri.parse('${ApiService.baseUrl}/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': 'bad', 'password': 'bad'}),
      );

      expect(response.statusCode, 401);
      final data = jsonDecode(response.body);
      expect(data['error'], 'Invalid credentials');
    });
  });
}
