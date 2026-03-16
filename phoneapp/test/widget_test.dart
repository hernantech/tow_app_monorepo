import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:tow_app/main.dart';
import 'package:tow_app/screens/login_screen.dart';
import 'package:provider/provider.dart';
import 'package:tow_app/providers/request_provider.dart';
import 'package:tow_app/providers/auth_provider.dart';
import 'package:tow_app/providers/cases_provider.dart';

void main() {
  testWidgets('App renders home screen', (WidgetTester tester) async {
    await tester.pumpWidget(const QuickTowApp());
    expect(find.text('QuickTow'), findsOneWidget);
    expect(find.text('Request a Tow'), findsOneWidget);
  });

  testWidgets('Home screen shows operator login button', (WidgetTester tester) async {
    await tester.pumpWidget(const QuickTowApp());
    expect(find.text('Operator Login'), findsOneWidget);
  });

  testWidgets('Login screen renders', (WidgetTester tester) async {
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => RequestProvider()),
          ChangeNotifierProvider(create: (_) => AuthProvider()),
          ChangeNotifierProvider(create: (_) => CasesProvider()),
        ],
        child: const MaterialApp(home: LoginScreen()),
      ),
    );
    expect(find.text('Operator Login'), findsOneWidget);
    expect(find.byType(TextField), findsNWidgets(2));
    expect(find.text('Login'), findsOneWidget);
  });
}
