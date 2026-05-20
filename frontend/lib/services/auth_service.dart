import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  static final AuthService instance = AuthService._internal();
  AuthService._internal();

  final SupabaseClient _client = Supabase.instance.client;

  // Web Client ID from Google Cloud Console
  // TODO: Replace with your actual Web Client ID
  static const String _webClientId =
      '812695577546-lj3a9g993dv80ugp98f6a2kvnunt1siu.apps.googleusercontent.com';
  // iOS Client ID from Google Cloud Console
  // TODO: Replace with your actual iOS Client ID (only needed for iOS)
  static const String _iosClientId =
      'YOUR_IOS_CLIENT_ID.apps.googleusercontent.com';

  Future<bool> signInWithGoogle() async {
    try {
      if (kIsWeb) {
        return await _signInWeb();
      } else {
        return await _signInNative();
      }
    } on AuthException catch (e) {
      throw Exception('Auth error: ${e.message}');
    } catch (e) {
      throw Exception('Google sign-in failed: $e');
    }
  }

  Future<bool> _signInWeb() async {
    await _client.auth.signInWithOAuth(OAuthProvider.google);
    return true;
  }

  Future<bool> _signInNative() async {
    final GoogleSignIn googleSignIn = GoogleSignIn(
      clientId: _iosClientId, // only needed for iOS
      serverClientId: _webClientId, // required for both Android & iOS
    );

    final googleUser = await googleSignIn.signIn();
    if (googleUser == null) return false; // user cancelled

    final googleAuth = await googleUser.authentication;
    final idToken = googleAuth.idToken;
    final accessToken = googleAuth.accessToken;

    if (idToken == null) throw Exception('No ID Token found.');
    if (accessToken == null) throw Exception('No Access Token found.');

    await _client.auth.signInWithIdToken(
      provider: OAuthProvider.google,
      idToken: idToken,
      accessToken: accessToken,
    );

    return true;
  }

  Future<void> signOut() async {
    await _client.auth.signOut();
  }

  User? get currentUser => _client.auth.currentUser;
}
