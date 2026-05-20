import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseService {
  final supabase = Supabase.instance.client;

  Future<void> signUp(String email, String password, String username) async {
    await supabase.auth.signUp(
      email: email,
      password: password,
      data: {'username': username},
      emailRedirectTo: 'com.servis.ai://login-callback',
    );
  }

  Future<void> signIn(String email, String password) async {
    await supabase.auth.signInWithPassword(email: email, password: password);
  }
}