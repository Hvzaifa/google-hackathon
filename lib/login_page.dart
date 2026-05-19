// import 'package:chatbotui/themepage.dart';
// import 'package:flutter/material.dart';
// import 'package:google_fonts/google_fonts.dart';
// import 'package:supabase_flutter/supabase_flutter.dart';

// class LoginScreen extends StatefulWidget {
//   const LoginScreen({super.key});

//   @override
//   State<LoginScreen> createState() => _LoginScreenState();
// }

// class _LoginScreenState extends State<LoginScreen>
//     with SingleTickerProviderStateMixin {
//   final supabase = Supabase.instance.client;
//   bool _isLoading = false;

//   late AnimationController _pulseController;
//   late Animation<double> _pulseAnim;

//   static const Color kPurple900 = Color(0xFF1E1B4B);
//   static const Color kPurple400 = Color(0xFF7C3AED);
//   static const Color kPurple300 = Color(0xFFA78BFA);
//   static const Color kPurple200 = Color(0xFFC4B5FD);
//   static const Color kPurple50 = Color(0xFFEDE9FE);

//   @override
//   void initState() {
//     super.initState();
//     _pulseController = AnimationController(
//       vsync: this,
//       duration: const Duration(seconds: 2),
//     )..repeat(reverse: true);

//     _pulseAnim = Tween<double>(begin: 0.95, end: 1.05).animate(
//       CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
//     );
//   }

//   @override
//   void dispose() {
//     _pulseController.dispose();
//     super.dispose();
//   }

//   Future<void> _signInWithGoogle() async {
//     setState(() => _isLoading = true);
//     try {
//       await supabase.auth.signInWithOAuth(
//         OAuthProvider.google,
//         redirectTo: 'com.servis.ai://login-callback',
//       );
//     } catch (e) {
//       if (mounted) {
//         ScaffoldMessenger.of(
//           context,
//         ).showSnackBar(SnackBar(content: Text('Error: $e')));
//       }
//     } finally {
//       if (mounted) setState(() => _isLoading = false);
//     }
//   }

//   Widget _buildEye() {
//     return Container(
//       width: 12,
//       height: 12,
//       decoration: BoxDecoration(
//         shape: BoxShape.circle,
//         color: kPurple400,
//         boxShadow: [
//           BoxShadow(color: kPurple300.withOpacity(0.5), blurRadius: 6),
//         ],
//       ),
//     );
//   }

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       backgroundColor: Colors.white,
//       body: Stack(
//         children: [
//           // same soft lavender gradient from HomePage
//           Positioned(
//             top: 0,
//             left: 0,
//             right: 0,
//             child: Container(
//               height: 360,
//               decoration: const BoxDecoration(
//                 gradient: LinearGradient(
//                   begin: Alignment.topCenter,
//                   end: Alignment.bottomCenter,
//                   colors: [Color(0xFFF3F0FF), Colors.white],
//                 ),
//               ),
//             ),
//           ),

//           SafeArea(
//             child: Padding(
//               padding: const EdgeInsets.symmetric(vertical: 50),
//               child: Column(
//                 crossAxisAlignment: CrossAxisAlignment.center,
//                 children: [
//                   // title — same as HomePage
//                   RichText(
//                     text: TextSpan(
//                       children: [
//                         TextSpan(
//                           text: "SERVIS ",
//                           style: GoogleFonts.archivoBlack(
//                             color: kPurple900,
//                             fontSize: 52,
//                             fontWeight: FontWeight.w700,
//                             height: 1.1,
//                           ),
//                         ),
//                         TextSpan(
//                           text: "AI",
//                           style: GoogleFonts.oswald(
//                             color: kPurple400,
//                             fontSize: 52,
//                             fontWeight: FontWeight.w700,
//                             height: 1.1,
//                           ),
//                         ),
//                       ],
//                     ),
//                   ),

//                   const SizedBox(height: 10),

//                   Text(
//                     "Sign in to continue",
//                     style: GoogleFonts.dmSans(
//                       color: const Color(0xFF6B7280),
//                       fontSize: 20,
//                       fontWeight: FontWeight.w400,
//                     ),
//                   ),

//                   const SizedBox(height: 28),

//                   // same animated orb from HomePage
//                   ScaleTransition(
//                     scale: _pulseAnim,
//                     child: SizedBox(
//                       width: 200,
//                       height: 200,
//                       child: Stack(
//                         alignment: Alignment.center,
//                         children: [
//                           Container(
//                             width: 200,
//                             height: 200,
//                             decoration: BoxDecoration(
//                               shape: BoxShape.circle,
//                               border: Border.all(
//                                 color: kPurple300.withOpacity(0.4),
//                                 width: 1.5,
//                               ),
//                             ),
//                           ),
//                           Container(
//                             width: 160,
//                             height: 160,
//                             decoration: BoxDecoration(
//                               shape: BoxShape.circle,
//                               border: Border.all(
//                                 color: kPurple300.withOpacity(0.6),
//                                 width: 1.5,
//                               ),
//                             ),
//                           ),
//                           Container(
//                             width: 120,
//                             height: 120,
//                             decoration: BoxDecoration(
//                               shape: BoxShape.circle,
//                               border: Border.all(
//                                 color: kPurple200.withOpacity(0.8),
//                                 width: 1.5,
//                               ),
//                             ),
//                           ),
//                           Container(
//                             width: 88,
//                             height: 88,
//                             decoration: BoxDecoration(
//                               shape: BoxShape.circle,
//                               color: Colors.white,
//                               border: Border.all(color: kPurple200, width: 2),
//                               boxShadow: [
//                                 BoxShadow(
//                                   color: kPurple50,
//                                   blurRadius: 0,
//                                   spreadRadius: 12,
//                                 ),
//                                 BoxShadow(
//                                   color: const Color(
//                                     0xFF9B7CF9,
//                                   ).withOpacity(0.9),
//                                   blurRadius: 24,
//                                   spreadRadius: 12,
//                                 ),
//                               ],
//                             ),
//                             child: Column(
//                               mainAxisAlignment: MainAxisAlignment.center,
//                               children: [
//                                 Row(
//                                   mainAxisAlignment: MainAxisAlignment.center,
//                                   children: [
//                                     _buildEye(),
//                                     const SizedBox(width: 12),
//                                     _buildEye(),
//                                   ],
//                                 ),
//                                 const SizedBox(height: 8),
//                                 Container(
//                                   width: 22,
//                                   height: 5,
//                                   decoration: BoxDecoration(
//                                     color: kPurple200,
//                                     borderRadius: const BorderRadius.only(
//                                       bottomLeft: Radius.circular(8),
//                                       bottomRight: Radius.circular(8),
//                                     ),
//                                   ),
//                                 ),
//                               ],
//                             ),
//                           ),
//                         ],
//                       ),
//                     ),
//                   ),

//                   const SizedBox(height: 30),

//                   Text(
//                     "Your AI-powered service companion",
//                     style: GoogleFonts.dmSans(
//                       color: kPurple300,
//                       fontSize: 13,
//                       fontWeight: FontWeight.w400,
//                       letterSpacing: 0.1,
//                     ),
//                   ),

//                   const Spacer(),

//                   // Google sign-in button — same style as "Get Started"
//                   Padding(
//                     padding: const EdgeInsets.symmetric(horizontal: 28),
//                     child: Container(
//                       decoration: BoxDecoration(
//                         color: Colors.white,
//                         borderRadius: BorderRadius.circular(20),
//                         border: Border.all(color: kPurple200, width: 1.5),
//                         boxShadow: [
//                           BoxShadow(
//                             color: kPurple300.withOpacity(0.15),
//                             blurRadius: 16,
//                             offset: const Offset(0, 4),
//                           ),
//                         ],
//                       ),
//                       child: Material(
//                         color: Colors.transparent,
//                         child: InkWell(
//                           borderRadius: BorderRadius.circular(20),
//                           splashColor: kPurple50,
//                           onTap: _isLoading ? null : _signInWithGoogle,
//                           child: Padding(
//                             padding: const EdgeInsets.symmetric(
//                               vertical: 16,
//                               horizontal: 24,
//                             ),
//                             child: Row(
//                               mainAxisAlignment: MainAxisAlignment.center,
//                               children: [
//                                 if (_isLoading)
//                                   const SizedBox(
//                                     width: 22,
//                                     height: 22,
//                                     child: CircularProgressIndicator(
//                                       strokeWidth: 2,
//                                       color: Color(0xFF7C3AED),
//                                     ),
//                                   )
//                                 else ...[
//                                   Image.asset(
//                                     'assets/google_logo.png',
//                                     height: 22,
//                                   ),
//                                   const SizedBox(width: 12),
//                                   Text(
//                                     "Continue with Google",
//                                     style: GoogleFonts.dmSans(
//                                       fontSize: 15,
//                                       fontWeight: FontWeight.w600,
//                                       color: kPurple900,
//                                       letterSpacing: 0.2,
//                                     ),
//                                   ),
//                                 ],
//                               ],
//                             ),
//                           ),
//                         ),
//                       ),
//                     ),
//                   ),

//                   const SizedBox(height: 16),

//                   Text(
//                     "By continuing, you agree to our Terms & Privacy Policy",
//                     style: GoogleFonts.dmSans(
//                       color: const Color(0xFF9CA3AF),
//                       fontSize: 11,
//                     ),
//                   ),

//                   const SizedBox(height: 12),
//                 ],
//               ),
//             ),
//           ),
//         ],
//       ),
//     );
//   }
// }
