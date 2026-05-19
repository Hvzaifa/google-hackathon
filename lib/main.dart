import 'package:chatbotui/homepage.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Future<void> main() async {
//   WidgetsFlutterBinding.ensureInitialized();

//   await Supabase.initialize(
//     url: 'https://your-project.supabase.co',
//     anonKey: 'YOUR_SUPABASE_ANON_KEY',
//   );

//   runApp(const ProviderScope(child: MyApp()));
// }

// final supabase = Supabase.instance.client;

void main() {
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Chat App',
      home: const HomePage(),
    );
  }
}