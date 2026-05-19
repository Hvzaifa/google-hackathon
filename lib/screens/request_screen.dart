import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import '../providers/orchestration_provider.dart';
import '../themepage.dart';
import 'results_screen.dart';

class RequestScreen extends ConsumerStatefulWidget {
  const RequestScreen({super.key});

  @override
  ConsumerState<RequestScreen> createState() => _RequestScreenState();
}

class _RequestScreenState extends ConsumerState<RequestScreen> {
  final TextEditingController _controller = TextEditingController();

  // Simulation flags
  bool _simulateMapsFailure = false;
  bool _simulateNoProviders = false;
  bool _simulateBookingFailure = false;
  bool _simulatePaymentFailure = false;
  bool _simulateProviderCancellation = false;

  void _submit() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    ref
        .read(orchestrationProvider.notifier)
        .sendRequest(
          text,
          simulateMapsFailure: _simulateMapsFailure,
          simulateNoProviders: _simulateNoProviders,
          simulateBookingFailure: _simulateBookingFailure,
          simulatePaymentFailure: _simulatePaymentFailure,
          simulateProviderCancellation: _simulateProviderCancellation,
        );

    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const ResultsScreen()),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      // resizeToAvoidBottomInset keeps scaffold from fighting the keyboard
      resizeToAvoidBottomInset: true,
      body: Stack(
        children: [
          // Gradient background
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
            child: Column(
              children: [
                // Header (fixed at top)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
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
                      Container(
                        width: 42,
                        height: 42,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [AppTheme.kPurple400, AppTheme.kPurple700],
                          ),
                          borderRadius: BorderRadius.circular(14),
                          boxShadow: [
                            BoxShadow(
                              color: AppTheme.kPurple400.withValues(alpha: 0.4),
                              blurRadius: 10,
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.smart_toy_outlined,
                          color: Colors.white,
                          size: 22,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Text(
                        'SERVIS AI',
                        style: GoogleFonts.archivoBlack(
                          color: AppTheme.kPurple900,
                          fontSize: 16,
                        ),
                      ),
                      const Spacer(),
                      GestureDetector(
                        onTap: _showSettingsModal,
                        child: Container(
                          width: 38,
                          height: 38,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: AppTheme.kPurple200),
                          ),
                          child: const Icon(
                            Icons.tune,
                            color: AppTheme.kPurple700,
                            size: 18,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // Scrollable body — prevents pixel overflow when keyboard opens
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 20),
                        Text(
                          'What service do\nyou need?',
                          style: GoogleFonts.dmSans(
                            fontSize: 28,
                            fontWeight: FontWeight.w700,
                            color: AppTheme.kPurple900,
                            height: 1.3,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Type in Roman Urdu or English. Our AI will understand.',
                          style: GoogleFonts.dmSans(
                            fontSize: 14,
                            color: AppTheme.kPurple300,
                          ),
                        ),
                        const SizedBox(height: 28),

                        // Text input
                        Container(
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: AppTheme.kPurple200),
                            boxShadow: [
                              BoxShadow(
                                color: AppTheme.kPurple100.withValues(
                                  alpha: 0.5,
                                ),
                                blurRadius: 12,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: TextField(
                            controller: _controller,
                            maxLines: 3,
                            minLines: 2,
                            style: GoogleFonts.dmSans(
                              color: AppTheme.kPurple900,
                              fontSize: 15,
                            ),
                            textInputAction: TextInputAction.done,
                            onSubmitted: (_) => _submit(),
                            decoration: InputDecoration(
                              hintText:
                                  'e.g. Mera AC kharab hai, G-13 Islamabad mein repair chahiye',
                              hintStyle: GoogleFonts.dmSans(
                                color: AppTheme.kPurple300.withValues(
                                  alpha: 0.6,
                                ),
                                fontSize: 14,
                              ),
                              border: InputBorder.none,
                              contentPadding: const EdgeInsets.all(16),
                            ),
                          ),
                        ),

                        const SizedBox(height: 14),

                        // Example chips
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            _exampleChip('AC repair in G-13'),
                            _exampleChip('Plumber chahiye F-8'),
                            _exampleChip('Electrician aaj subah'),
                          ],
                        ),

                        const SizedBox(height: 30),

                        // Data source info box
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.blue.withValues(alpha: 0.05),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: Colors.blue.withValues(alpha: 0.15),
                            ),
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Icon(
                                Icons.info_outline,
                                size: 16,
                                color: Colors.blue[400],
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  'Provide the location as precise as Possible eg; (Bahria Town Phase 4 Islamabad) for the best results instead of Bahria Town Phase 4\nWith the Area add the city name as well',
                                  style: GoogleFonts.dmSans(
                                    fontSize: 11,
                                    color: Colors.blue[700],
                                    height: 1.4,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 30),

                        // Submit button
                        SizedBox(
                          width: double.infinity,
                          child: GestureDetector(
                            onTap: _submit,
                            child: Container(
                              padding: const EdgeInsets.symmetric(vertical: 16),
                              decoration: BoxDecoration(
                                gradient: const LinearGradient(
                                  colors: [
                                    AppTheme.kPurple400,
                                    AppTheme.kPurple700,
                                  ],
                                ),
                                borderRadius: BorderRadius.circular(16),
                                boxShadow: [
                                  BoxShadow(
                                    color: AppTheme.kPurple400.withValues(
                                      alpha: 0.4,
                                    ),
                                    blurRadius: 14,
                                    offset: const Offset(0, 6),
                                  ),
                                ],
                              ),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(
                                    'Find Service',
                                    style: GoogleFonts.dmSans(
                                      fontSize: 16,
                                      fontWeight: FontWeight.w600,
                                      color: Colors.white,
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  const Icon(
                                    Icons.arrow_forward,
                                    color: Colors.white,
                                    size: 18,
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ),

                        const SizedBox(height: 20),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _exampleChip(String text) {
    return GestureDetector(
      onTap: () => _controller.text = text,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: AppTheme.kPurple50,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppTheme.kPurple200),
        ),
        child: Text(
          text,
          style: GoogleFonts.dmSans(fontSize: 12, color: AppTheme.kPurple700),
        ),
      ),
    );
  }

  void _showSettingsModal() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Simulation Toggles',
                    style: GoogleFonts.dmSans(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.kPurple900,
                    ),
                  ),
                  const SizedBox(height: 10),
                  _toggle('Simulate Maps Failure', _simulateMapsFailure, (v) {
                    setModalState(() => _simulateMapsFailure = v);
                    setState(() => _simulateMapsFailure = v);
                  }),
                  _toggle('Simulate No Providers', _simulateNoProviders, (v) {
                    setModalState(() => _simulateNoProviders = v);
                    setState(() => _simulateNoProviders = v);
                  }),
                  _toggle('Simulate Booking Failure', _simulateBookingFailure, (
                    v,
                  ) {
                    setModalState(() => _simulateBookingFailure = v);
                    setState(() => _simulateBookingFailure = v);
                  }),
                  _toggle('Simulate Payment Failure', _simulatePaymentFailure, (
                    v,
                  ) {
                    setModalState(() => _simulatePaymentFailure = v);
                    setState(() => _simulatePaymentFailure = v);
                  }),
                  _toggle(
                    'Simulate Provider Cancellation',
                    _simulateProviderCancellation,
                    (v) {
                      setModalState(() => _simulateProviderCancellation = v);
                      setState(() => _simulateProviderCancellation = v);
                    },
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Widget _toggle(String title, bool value, ValueChanged<bool> onChanged) {
    return SwitchListTile(
      title: Text(title, style: const TextStyle(fontSize: 14)),
      value: value,
      activeTrackColor: AppTheme.kPurple200,
      activeColor: AppTheme.kPurple700,
      onChanged: onChanged,
    );
  }
}
