import 'dart:async';
import 'package:chatbotui/services/supabase_services.dart';
import 'package:chatbotui/themepage.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final supabase = Supabase.instance.client;
  final SupabaseService _supabaseService = SupabaseService();
  
  bool _isLoading = false;
  bool _isLogin = true; // Toggle between Login and Register

  late StreamSubscription<AuthState> _authStateSubscription;

  // Text Controllers
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _usernameController = TextEditingController();

  static const Color kPurple900 = Color(0xFF1E1B4B);
  static const Color kPurple400 = Color(0xFF7C3AED);
  static const Color kPurple300 = Color(0xFFA78BFA);
  static const Color kPurple200 = Color(0xFFC4B5FD);
  static const Color kPurple50 = Color(0xFFEDE9FE);

  @override
  void initState() {
    super.initState();

    // Listen for sign-in events (especially from deep links like Google OAuth)
    // and close the LoginScreen so AuthGate can take over.
    _authStateSubscription = supabase.auth.onAuthStateChange.listen((data) {
      if (data.event == AuthChangeEvent.signedIn) {
        if (mounted && Navigator.canPop(context)) {
          Navigator.of(context).popUntil((route) => route.isFirst);
        }
      }
    });
  }

  @override
  void dispose() {
    _authStateSubscription.cancel();
    _emailController.dispose();
    _passwordController.dispose();
    _usernameController.dispose();
    super.dispose();
  }

  void _showError(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
    }
  }

  Future<void> _submitAuth() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();
    final username = _usernameController.text.trim();

    if (email.isEmpty || password.isEmpty) {
      _showError('Please fill in all fields');
      return;
    }

    if (!_isLogin && username.isEmpty) {
      _showError('Please enter a username');
      return;
    }

    setState(() => _isLoading = true);

    try {
      if (_isLogin) {
        await _supabaseService.signIn(email, password);
      } else {
        await _supabaseService.signUp(email, password, username);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Account created! Please check your email to verify (if enabled) or sign in.')),
          );
          // Automatically switch to login mode after successful signup
          setState(() {
            _isLogin = true;
          });
        }
      }
    } on AuthException catch (e) {
      _showError(e.message);
    } catch (e) {
      _showError('An unexpected error occurred: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _signInWithGoogle() async {
    setState(() => _isLoading = true);
    try {
      await supabase.auth.signInWithOAuth(
        OAuthProvider.google,
        redirectTo: 'com.servis.ai://login-callback',
      );
    } catch (e) {
      _showError('Google Auth Error: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // soft lavender gradient
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(
              height: 300,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Color(0xFFF3F0FF), Colors.white],
                ),
              ),
            ),
          ),

          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 20),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      // Logo
                      Text(
                        "SERVIS AI",
                        style: GoogleFonts.archivoBlack(
                          color: kPurple900,
                          fontSize: 22,
                          letterSpacing: 1.2,
                        ),
                      ),
                      
                      const SizedBox(height: 40),

                      // Dynamic Header
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          _isLogin ? "Welcome back 👋" : "Create account ✨",
                          style: GoogleFonts.dmSans(
                            color: kPurple900,
                            fontSize: 32,
                            fontWeight: FontWeight.w700,
                            letterSpacing: -0.5,
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Align(
                        alignment: Alignment.centerLeft,
                        child: Text(
                          _isLogin 
                              ? "Sign in to access your dashboard" 
                              : "Sign up to start finding services instantly",
                          style: GoogleFonts.dmSans(
                            color: const Color(0xFF6B7280),
                            fontSize: 16,
                            fontWeight: FontWeight.w400,
                          ),
                        ),
                      ),

                      const SizedBox(height: 32),

                      // Sleek Tab Switcher
                      Container(
                        height: 52,
                        decoration: BoxDecoration(
                          color: kPurple50,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Row(
                          children: [
                            Expanded(
                              child: GestureDetector(
                                onTap: () => setState(() => _isLogin = true),
                                child: Container(
                                  margin: const EdgeInsets.all(4),
                                  decoration: BoxDecoration(
                                    color: _isLogin ? Colors.white : Colors.transparent,
                                    borderRadius: BorderRadius.circular(12),
                                    boxShadow: _isLogin 
                                        ? [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8, offset: const Offset(0, 2))]
                                        : null,
                                  ),
                                  child: Center(
                                    child: Text(
                                      "Sign In",
                                      style: GoogleFonts.dmSans(
                                        color: _isLogin ? kPurple900 : kPurple400,
                                        fontWeight: _isLogin ? FontWeight.bold : FontWeight.w600,
                                        fontSize: 15,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ),
                            Expanded(
                              child: GestureDetector(
                                onTap: () => setState(() => _isLogin = false),
                                child: Container(
                                  margin: const EdgeInsets.all(4),
                                  decoration: BoxDecoration(
                                    color: !_isLogin ? Colors.white : Colors.transparent,
                                    borderRadius: BorderRadius.circular(12),
                                    boxShadow: !_isLogin 
                                        ? [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8, offset: const Offset(0, 2))]
                                        : null,
                                  ),
                                  child: Center(
                                    child: Text(
                                      "Sign Up",
                                      style: GoogleFonts.dmSans(
                                        color: !_isLogin ? kPurple900 : kPurple400,
                                        fontWeight: !_isLogin ? FontWeight.bold : FontWeight.w600,
                                        fontSize: 15,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 32),

                      // Input Fields
                      if (!_isLogin) ...[
                        TextField(
                          controller: _usernameController,
                          decoration: AppTheme.inputDecoration.copyWith(
                            labelText: 'Username',
                            prefixIcon: const Icon(Icons.person_outline, color: kPurple400),
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],

                      TextField(
                        controller: _emailController,
                        keyboardType: TextInputType.emailAddress,
                        decoration: AppTheme.inputDecoration.copyWith(
                          labelText: 'Email',
                          prefixIcon: const Icon(Icons.email_outlined, color: kPurple400),
                        ),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      TextField(
                        controller: _passwordController,
                        obscureText: true,
                        decoration: AppTheme.inputDecoration.copyWith(
                          labelText: 'Password',
                          prefixIcon: const Icon(Icons.lock_outline, color: kPurple400),
                        ),
                      ),

                      const SizedBox(height: 24),

                      // Main Auth Button (Email/Password)
                      SizedBox(
                        width: double.infinity,
                        height: 54,
                        child: ElevatedButton(
                          onPressed: _isLoading ? null : _submitAuth,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: kPurple400,
                            foregroundColor: Colors.white,
                            elevation: 0,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(20),
                            ),
                          ),
                          child: _isLoading
                              ? const SizedBox(
                                  width: 24,
                                  height: 24,
                                  child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                                )
                              : Text(
                                  _isLogin ? 'Sign In' : 'Create Account',
                                  style: GoogleFonts.dmSans(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w600,
                                    letterSpacing: 0.5,
                                  ),
                                ),
                        ),
                      ),

                      const SizedBox(height: 20),

                      // Divider
                      Row(
                        children: [
                          Expanded(child: Divider(color: Colors.grey.shade300)),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            child: Text(
                              "OR",
                              style: GoogleFonts.dmSans(color: Colors.grey.shade500, fontSize: 12),
                            ),
                          ),
                          Expanded(child: Divider(color: Colors.grey.shade300)),
                        ],
                      ),

                      const SizedBox(height: 20),

                      // Google sign-in button
                      Container(
                        width: double.infinity,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: kPurple200, width: 1.5),
                        ),
                        child: Material(
                          color: Colors.transparent,
                          child: InkWell(
                            borderRadius: BorderRadius.circular(20),
                            splashColor: kPurple50,
                            onTap: _isLoading ? null : _signInWithGoogle,
                            child: Padding(
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Image.network(
                                    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/120px-Google_%22G%22_logo.svg.png',
                                    height: 24,
                                    width: 24,
                                    errorBuilder: (context, error, stackTrace) => const Icon(
                                      Icons.g_mobiledata, 
                                      color: Color(0xFF4285F4), 
                                      size: 32,
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Text(
                                    "Continue with Google",
                                    style: GoogleFonts.dmSans(
                                      fontSize: 15,
                                      fontWeight: FontWeight.w600,
                                      color: kPurple900,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),

                      const SizedBox(height: 24),

                      const SizedBox(height: 32),
                      
                      Text(
                        "By continuing, you agree to our Terms & Privacy Policy",
                        style: GoogleFonts.dmSans(
                          color: const Color(0xFF9CA3AF),
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
