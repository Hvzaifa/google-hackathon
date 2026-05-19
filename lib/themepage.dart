import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color kPurple900 = Color(0xFF1E1B4B);
  static const Color kPurple700 = Color(0xFF4C1D95);
  static const Color kPurple400 = Color(0xFF7C3AED);
  static const Color kPurple300 = Color(0xFFA78BFA);
  static const Color kPurple200 = Color(0xFFC4B5FD);
  static const Color kPurple100 = Color(0xFFDDD6FE);
  static const Color kPurple50 = Color(0xFFEDE9FE);

  static final inputDecoration = InputDecoration(
    filled: true,
    fillColor: Colors.white,
    border: OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: BorderSide(color: kPurple200),
    ),
    enabledBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: BorderSide(color: kPurple200),
    ),
    focusedBorder: OutlineInputBorder(
      borderRadius: BorderRadius.circular(16),
      borderSide: BorderSide(color: kPurple400, width: 2),
    ),
    contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
  );

  static final buttonStyle = ElevatedButton.styleFrom(
    backgroundColor: kPurple400,
    foregroundColor: Colors.white,
    elevation: 0,
    padding: const EdgeInsets.symmetric(vertical: 16),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
    textStyle: GoogleFonts.dmSans(fontSize: 16, fontWeight: FontWeight.w600),
  );
}