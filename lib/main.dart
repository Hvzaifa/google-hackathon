import 'package:chatbotui/auth_gate.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Supabase.initialize(
    url: 'https://nqyjwhlkeferpuahdont.supabase.co',
    anonKey:
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5xeWp3aGxrZWZlcnB1YWhkb250Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkwMjc0NzEsImV4cCI6MjA5NDYwMzQ3MX0.AIUUWLqbQ6nwyKMEDAfZqOvCRtSlNPNWmURU93uNBeM',
  );

  runApp(const ProviderScope(child: MyApp()));
}

final supabase = Supabase.instance.client;

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'ServisAI',
      home: const AuthGate(),
    );
  }
}