import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../themepage.dart';

class FeedbackScreen extends StatefulWidget {
  const FeedbackScreen({super.key});

  @override
  State<FeedbackScreen> createState() => _FeedbackScreenState();
}

class _FeedbackScreenState extends State<FeedbackScreen>
    with SingleTickerProviderStateMixin {
  int _rating = 0;
  final TextEditingController _commentController = TextEditingController();
  bool _submitted = false;
  late AnimationController _checkController;
  late Animation<double> _checkScale;

  @override
  void initState() {
    super.initState();
    _checkController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _checkScale = CurvedAnimation(
      parent: _checkController,
      curve: Curves.elasticOut,
    );
  }

  @override
  void dispose() {
    _commentController.dispose();
    _checkController.dispose();
    super.dispose();
  }

  void _submitFeedback() {
    if (_rating <= 0) return;
    setState(() => _submitted = true);
    _checkController.forward();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      resizeToAvoidBottomInset: true,
      body: Stack(
        children: [
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(
              height: 260,
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
            child: Column(
              children: [
                // Fixed header
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.8),
                    border: const Border(
                      bottom: BorderSide(color: AppTheme.kPurple100),
                    ),
                  ),
                  child: Row(
                    children: [
                      GestureDetector(
                        onTap: () => Navigator.pop(context),
                        child: Container(
                          width: 38,
                          height: 38,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: AppTheme.kPurple200),
                          ),
                          child: const Icon(
                            Icons.arrow_back_ios_new_rounded,
                            color: AppTheme.kPurple700,
                            size: 16,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        'Feedback',
                        style: GoogleFonts.dmSans(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: AppTheme.kPurple900,
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: _submitted ? _buildThankYou() : _buildForm(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildForm() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: IntrinsicHeight(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 20),
                  Text(
                    'How was your\nexperience?',
                    style: GoogleFonts.dmSans(
                      fontSize: 26,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.kPurple900,
                      height: 1.3,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    'Your feedback helps us match you with better providers.',
                    style: GoogleFonts.dmSans(
                      fontSize: 13,
                      color: AppTheme.kPurple300,
                    ),
                  ),
                  const SizedBox(height: 28),

                  // Star rating in a card
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(
                        vertical: 20, horizontal: 16),
                    decoration: BoxDecoration(
                      color: AppTheme.kPurple50.withValues(alpha: 0.5),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppTheme.kPurple100),
                    ),
                    child: Column(
                      children: [
                        Text(
                          _rating == 0
                              ? 'Tap a star to rate'
                              : _ratingLabel(_rating),
                          style: GoogleFonts.dmSans(
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                            color: _rating == 0
                                ? AppTheme.kPurple300
                                : AppTheme.kPurple700,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: List.generate(5, (i) {
                            return GestureDetector(
                              onTap: () => setState(() => _rating = i + 1),
                              child: AnimatedContainer(
                                duration: const Duration(milliseconds: 200),
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 6),
                                child: Icon(
                                  i < _rating
                                      ? Icons.star_rounded
                                      : Icons.star_border_rounded,
                                  size: i < _rating ? 44 : 40,
                                  color: i < _rating
                                      ? Colors.amber
                                      : AppTheme.kPurple200,
                                ),
                              ),
                            );
                          }),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 20),

                  // Comment box
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppTheme.kPurple200),
                      boxShadow: [
                        BoxShadow(
                          color: AppTheme.kPurple100.withValues(alpha: 0.3),
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: TextField(
                      controller: _commentController,
                      maxLines: 4,
                      minLines: 3,
                      style: GoogleFonts.dmSans(
                        fontSize: 14,
                        color: AppTheme.kPurple900,
                      ),
                      decoration: InputDecoration(
                        hintText: 'Share your thoughts (optional)...',
                        hintStyle: GoogleFonts.dmSans(
                          color: AppTheme.kPurple300.withValues(alpha: 0.6),
                          fontSize: 14,
                        ),
                        border: InputBorder.none,
                        contentPadding: const EdgeInsets.all(16),
                      ),
                    ),
                  ),

                  const Spacer(),
                  const SizedBox(height: 24),

                  // Submit button
                  SizedBox(
                    width: double.infinity,
                    child: GestureDetector(
                      onTap: _submitFeedback,
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        decoration: BoxDecoration(
                          gradient: _rating > 0
                              ? const LinearGradient(
                                  colors: [
                                    AppTheme.kPurple400,
                                    AppTheme.kPurple700
                                  ],
                                )
                              : null,
                          color: _rating > 0 ? null : Colors.grey[200],
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: _rating > 0
                              ? [
                                  BoxShadow(
                                    color: AppTheme.kPurple400
                                        .withValues(alpha: 0.4),
                                    blurRadius: 12,
                                    offset: const Offset(0, 4),
                                  ),
                                ]
                              : null,
                        ),
                        child: Center(
                          child: Text(
                            'Submit Feedback',
                            style: GoogleFonts.dmSans(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color:
                                  _rating > 0 ? Colors.white : Colors.grey[400],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 16),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildThankYou() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ScaleTransition(
              scale: _checkScale,
              child: Container(
                width: 90,
                height: 90,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Colors.green.withValues(alpha: 0.15),
                      Colors.green.withValues(alpha: 0.05),
                    ],
                  ),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.check_circle_rounded,
                    size: 52, color: Colors.green),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Thank you!',
              style: GoogleFonts.dmSans(
                fontSize: 24,
                fontWeight: FontWeight.w700,
                color: AppTheme.kPurple900,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Your feedback helps us improve\nservice matching for everyone.',
              textAlign: TextAlign.center,
              style: GoogleFonts.dmSans(
                fontSize: 14,
                color: AppTheme.kPurple300,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 28),
            GestureDetector(
              onTap: () => Navigator.pop(context),
              child: Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 28, vertical: 12),
                decoration: BoxDecoration(
                  color: AppTheme.kPurple50,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppTheme.kPurple200),
                ),
                child: Text(
                  'Back to Results',
                  style: GoogleFonts.dmSans(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.kPurple700,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _ratingLabel(int rating) {
    switch (rating) {
      case 1:
        return 'Poor';
      case 2:
        return 'Fair';
      case 3:
        return 'Good';
      case 4:
        return 'Very Good';
      case 5:
        return 'Excellent!';
      default:
        return '';
    }
  }
}
