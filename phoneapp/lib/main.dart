import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/request_provider.dart';
import 'providers/auth_provider.dart';
import 'providers/cases_provider.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => RequestProvider()..loadShops()),
        ChangeNotifierProvider(create: (context) => AuthProvider()),
        ChangeNotifierProvider(create: (context) => CasesProvider()),
      ],
      child: const QuickTowApp(),
    ),
  );
}

class QuickTowApp extends StatelessWidget {
  const QuickTowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'QuickTow',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: Colors.white,
        appBarTheme: const AppBarTheme(
          elevation: 0,
          backgroundColor: Colors.white,
          foregroundColor: Colors.black,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
