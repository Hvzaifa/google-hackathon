import 'dart:ui';
import 'package:chatbotui/chatpage.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage>
    with SingleTickerProviderStateMixin {
  late AnimationController pulseController;
  late Animation<double> pulseAnim;

  // ── colour palette ─────────────────────────────────────────
  static const Color kPurple900 = Color(0xFF1E1B4B);
  static const Color kPurple700 = Color(0xFF4C1D95);
  static const Color kPurple400 = Color(0xFF7C3AED);
  static const Color kPurple300 = Color(0xFFA78BFA);
  static const Color kPurple200 = Color(0xFFC4B5FD);
  static const Color kPurple100 = Color(0xFFDDD6FE);
  static const Color kPurple50 = Color(0xFFEDE9FE);

  @override
  void initState() {
    super.initState();
    pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    pulseAnim = Tween<double>(begin: 0.95, end: 1.05).animate(
      CurvedAnimation(parent: pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // soft lavender gradient at the top
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(
              height: 360,
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
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 50),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // ── title ──────────────────────────────────
                  RichText(
                    text: TextSpan(
                      children: [
                        TextSpan(
                          text: "SERVIS ",
                          style: GoogleFonts.archivoBlack(
                            color: kPurple900,
                            fontSize: 52,
                            fontWeight: FontWeight.w700,
                            height: 1.1,
                          ),
                        ),
                        TextSpan(
                          text: "AI",
                          style: GoogleFonts.oswald(
                            color: kPurple400,
                            fontSize: 52,
                            fontWeight: FontWeight.w700,
                            height: 1.1,
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 10),

                  // ── subtitle ───────────────────────────────
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 32),
                    child: Text(
                      "Service at your doorstep,\nin a single prompt.",
                      textAlign: TextAlign.center,
                      style: GoogleFonts.dmSans(
                        color: const Color(0xFF6B7280),
                        fontSize: 20,
                        fontWeight: FontWeight.w400,
                        height: 1.65,
                      ),
                    ),
                  ),

                  const SizedBox(height: 28),

                  // ── animated orb ───────────────────────────
                  ScaleTransition(
                    scale: pulseAnim,
                    child: SizedBox(
                      width: 200,
                      height: 200,
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          // outer ring
                          Container(
                            width: 200,
                            height: 200,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: kPurple300.withOpacity(0.4),
                                width: 1.5,
                              ),
                            ),
                          ),
                          // middle ring
                          Container(
                            width: 160,
                            height: 160,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: kPurple300.withOpacity(0.6),
                                width: 1.5,
                              ),
                            ),
                          ),
                          // inner ring
                          Container(
                            width: 120,
                            height: 120,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: kPurple200.withOpacity(0.8),
                                width: 1.5,
                              ),
                            ),
                          ),
                          // bot face — white core with purple accents
                          Container(
                            width: 88,
                            height: 88,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: Colors.white,
                              border: Border.all(color: kPurple200, width: 2),
                              boxShadow: [
                                BoxShadow(
                                  color: kPurple50,
                                  blurRadius: 0,
                                  spreadRadius: 12,
                                ),
                                BoxShadow(
                                  color: const Color.fromARGB(
                                    255,
                                    155,
                                    124,
                                    249,
                                  ).withOpacity(0.9),
                                  blurRadius: 24,
                                  spreadRadius: 12,
                                ),
                              ],
                            ),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    _buildEye(),
                                    const SizedBox(width: 12),
                                    _buildEye(),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                Container(
                                  width: 22,
                                  height: 5,
                                  decoration: BoxDecoration(
                                    color: kPurple200,
                                    borderRadius: const BorderRadius.only(
                                      bottomLeft: Radius.circular(8),
                                      bottomRight: Radius.circular(8),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 30),

                  // ── hint text ──────────────────────────────
                  Text(
                    "Get instant services in a single prompt",
                    style: GoogleFonts.dmSans(
                      color: kPurple300,
                      fontSize: 13,
                      fontWeight: FontWeight.w400,
                      letterSpacing: 0.1,
                    ),
                  ),

                  const Spacer(),

                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 28),
                    child: ClipRRect(
                      child: Container(
                        decoration: BoxDecoration(
                          color: kPurple400.withOpacity(1),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: kPurple400.withOpacity(0.3),
                            width: 1.5,
                          ),
                        ),
                        child: Material(
                          color: Colors.transparent,
                          child: InkWell(
                            borderRadius: BorderRadius.circular(20),
                            splashColor: kPurple100.withOpacity(0.4),
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => const ChatPage(),
                                ),
                              );
                            },
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                vertical: 16,
                                horizontal: 24,
                              ),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(
                                    "Get Started",
                                    style: GoogleFonts.dmSans(
                                      fontSize: 15,
                                      fontWeight: FontWeight.w500,
                                      color: Colors.white,
                                      letterSpacing: 0.2,
                                    ),
                                  ),
                                  const SizedBox(width: 10),
                                  Container(
                                    width: 26,
                                    height: 26,
                                    decoration: const BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: kPurple400,
                                    ),
                                    child: const Icon(
                                      Icons.arrow_forward,
                                      color: Colors.white,
                                      size: 14,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEye() {
    return Container(
      width: 12,
      height: 12,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: kPurple400,
        boxShadow: [
          BoxShadow(color: kPurple300.withOpacity(0.5), blurRadius: 6),
        ],
      ),
    );
  }
}
