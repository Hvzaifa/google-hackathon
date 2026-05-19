import 'package:chatbotui/themepage.dart';
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:google_fonts/google_fonts.dart';

class UsernameScreen extends StatefulWidget {
  const UsernameScreen({super.key});

  @override
  State<UsernameScreen> createState() => _UsernameScreenState();
}

class _UsernameScreenState extends State<UsernameScreen> {
  final _usernameController = TextEditingController();
  final _supabase = Supabase.instance.client;
  bool _isLoading = false;

  Future<void> _saveUsername() async {
    final username = _usernameController.text.trim();
    if (username.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a username')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      final user = _supabase.auth.currentUser!;
      await _supabase.from('profiles').upsert({
        'id': user.id,
        'username': username,
      });
      // Navigate to chatbot home
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/chat');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'What should we call you?',
                style: GoogleFonts.archivoBlack(
                  fontSize: 28,
                  color: AppTheme.kPurple900,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              Text(
                'This name will be used by our AI to address you.',
                style: GoogleFonts.dmSans(
                  fontSize: 16,
                  color: AppTheme.kPurple700,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              TextField(
                controller: _usernameController,
                decoration: AppTheme.inputDecoration.copyWith(
                  hintText: 'e.g., Alex, Sarah, TechGuru',
                  labelText: 'Your username',
                ),
                style: GoogleFonts.dmSans(),
                textInputAction: TextInputAction.done,
                onSubmitted: (_) => _saveUsername(),
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: _isLoading ? null : _saveUsername,
                style: AppTheme.buttonStyle,
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text('Continue to Chat', style: GoogleFonts.dmSans()),
              ),
            ],
          ),
        ),
      ),
    );
  }
}