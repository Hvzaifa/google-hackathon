import 'package:chatbotui/screens/request_screen.dart';
import 'package:chatbotui/username_screen.dart';
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'homepage.dart';
import 'login_page.dart';

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<AuthState>(
      stream: Supabase.instance.client.auth.onAuthStateChange,
      builder: (context, snapshot) {
        // Still connecting to auth stream
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        final session = snapshot.data?.session;

        // Not logged in → show landing page
        if (session == null) {
          return const HomePage();
        }

        // Logged in → check if user has set a username in profiles
        return FutureBuilder<Map<String, dynamic>?>(
          future: Supabase.instance.client
              .from('profiles')
              .select('username')
              .eq('id', session.user.id)
              .maybeSingle(),
          builder: (context, snap) {
            if (snap.connectionState == ConnectionState.waiting) {
              return const Scaffold(
                body: Center(child: CircularProgressIndicator()),
              );
            }
            final hasUsername =
                snap.hasData && snap.data?['username'] != null;
            return hasUsername
                ? const RequestScreen()
                : const UsernameScreen();
          },
        );
      },
    );
  }
}
