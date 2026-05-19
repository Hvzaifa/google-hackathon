import 'package:flutter/material.dart';

class ChatMessage {
  final String text;
  final bool isUser;
  final String time;
  const ChatMessage({required this.text, required this.isUser, required this.time});
}
 
class ChatPage extends StatefulWidget {
  const ChatPage({super.key});
 
  @override
  State<ChatPage> createState() => _ChatPageState();
}
 
class _ChatPageState extends State<ChatPage> with TickerProviderStateMixin {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isTyping = false;
 
  static const Color kPurple900 = Color(0xFF1E1B4B);
  static const Color kPurple700 = Color(0xFF4C1D95);
  static const Color kPurple400 = Color(0xFF7C3AED);
  static const Color kPurple300 = Color(0xFFA78BFA);
  static const Color kPurple200 = Color(0xFFC4B5FD);
  static const Color kPurple100 = Color(0xFFDDD6FE);
  static const Color kPurple50  = Color(0xFFEDE9FE);

  final List<ChatMessage> _messages = [
    const ChatMessage(
      text: "Hello! I'm Nova, your AI assistant. How can I help you today? 👋",
      isUser: false,
      time: '09:41',
    ),
  ];
 
  late AnimationController _dotController;
  late Animation<double> _dotAnim;
 
  @override
  void initState() {
    super.initState();
    _dotController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    )..repeat(reverse: true);
    _dotAnim = Tween<double>(begin: 0, end: 6).animate(
      CurvedAnimation(parent: _dotController, curve: Curves.easeInOut),
    );
  }
 
  @override
  void dispose() {
    _dotController.dispose();
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }
 
  void _sendMessage() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
 
    final now = TimeOfDay.now();
    final timeStr = '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}';
 
    setState(() {
      _messages.add(ChatMessage(text: text, isUser: true, time: timeStr));
      _isTyping = true;
    });
    _controller.clear();
    _scrollToBottom();
 
    Future.delayed(const Duration(seconds: 2), () {
      setState(() {
        _isTyping = false;
        _messages.add(ChatMessage(
          text: "That's a great question! I'm processing your request and will provide the best answer I can. Is there anything else you'd like to know?",
          isUser: false,
          time: timeStr,
        ));
      });
      _scrollToBottom();
    });
  }
 
  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }
 
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          // Match the soft lavender gradient from HomePage
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
                // Header
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.8),
                    border: const Border(
                      bottom: BorderSide(color: kPurple100),
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
                            border: Border.all(color: kPurple200),
                          ),
                          child: const Icon(Icons.arrow_back_ios_new_rounded,
                              color: kPurple700, size: 16),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Container(
                        width: 42,
                        height: 42,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [kPurple400, kPurple700],
                          ),
                          borderRadius: BorderRadius.circular(14),
                          boxShadow: [
                            BoxShadow(
                              color: kPurple400.withOpacity(0.4),
                              blurRadius: 10,
                            ),
                          ],
                        ),
                        child: const Icon(Icons.smart_toy_outlined,
                            color: Colors.white, size: 22),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'SERVIS AI',
                              style: TextStyle(
                                color: kPurple900,
                                fontSize: 15,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          
                          ],
                        ),
                      ),
                      Container(
                        width: 38,
                        height: 38,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: kPurple200),
                        ),
                        child: const Icon(Icons.more_vert_rounded,
                            color: kPurple700, size: 18),
                      ),
                    ],
                  ),
                ),
 
                // Messages
                Expanded(
                  child: ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length + (_isTyping ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (_isTyping && index == _messages.length) {
                        return _buildTypingIndicator();
                      }
                      final msg = _messages[index];
                      return _buildMessage(msg);
                    },
                  ),
                ),
 
                
                const SizedBox(height: 8),
 
                // Input bar
                Container(
                  padding: const EdgeInsets.fromLTRB(16, 10, 16, 16),
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    border: Border(
                      top: BorderSide(color: kPurple100),
                    ),
                  ),
                  child: Row(
                    children: [
                      // Mic
                      Container(
                        width: 46,
                        height: 46,
                        decoration: BoxDecoration(
                          color: kPurple50,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: kPurple100),
                        ),
                        child: const Icon(Icons.mic_none_rounded,
                            color: kPurple400, size: 20),
                      ),
                      const SizedBox(width: 10),
                      // Text field
                      Expanded(
                        child: Container(
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: kPurple200),
                          ),
                          child: TextField(
                            controller: _controller,
                            style: const TextStyle(color: kPurple900, fontSize: 14),
                            maxLines: 1,
                            onSubmitted: (_) => _sendMessage(),
                            decoration: const InputDecoration(
                              hintText: 'Ask anything…',
                              hintStyle: TextStyle(color: kPurple300, fontSize: 14),
                              border: InputBorder.none,
                              contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      // Send
                      GestureDetector(
                        onTap: _sendMessage,
                        child: Container(
                          width: 46,
                          height: 46,
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(
                              colors: [kPurple400, kPurple700],
                            ),
                            borderRadius: BorderRadius.circular(14),
                            boxShadow: [
                              BoxShadow(
                                color: kPurple400.withOpacity(0.4),
                                blurRadius: 12,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: const Icon(Icons.send_rounded, color: Colors.white, size: 20),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
 
  Widget _buildMessage(ChatMessage msg) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment:
            msg.isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment:
                msg.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              if (!msg.isUser) ...[
                Container(
                  width: 30,
                  height: 30,
                  margin: const EdgeInsets.only(right: 8, bottom: 4),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [kPurple400, kPurple700],
                    ),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.smart_toy_outlined,
                      color: Colors.white, size: 16),
                ),
              ],
              Flexible(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  decoration: BoxDecoration(
                    gradient: msg.isUser
                        ? const LinearGradient(
                            colors: [kPurple400, kPurple700],
                          )
                        : null,
                    color: msg.isUser
                        ? null
                        : kPurple50,
                    borderRadius: BorderRadius.only(
                      topLeft: const Radius.circular(18),
                      topRight: const Radius.circular(18),
                      bottomLeft: Radius.circular(msg.isUser ? 18 : 4),
                      bottomRight: Radius.circular(msg.isUser ? 4 : 18),
                    ),
                    border: msg.isUser
                        ? null
                        : Border.all(color: kPurple100),
                    boxShadow: msg.isUser
                        ? [
                            BoxShadow(
                              color: kPurple400.withOpacity(0.3),
                              blurRadius: 12,
                              offset: const Offset(0, 4),
                            ),
                          ]
                        : null,
                  ),
                  child: Text(
                    msg.text,
                    style: TextStyle(
                      color: msg.isUser ? Colors.white : kPurple900,
                      fontSize: 14,
                      height: 1.5,
                    ),
                  ),
                ),
              ),
            ],
          ),
          Padding(
            padding: EdgeInsets.only(
              top: 4,
              left: msg.isUser ? 0 : 46,
              right: msg.isUser ? 4 : 0,
            ),
            child: Text(
              msg.time,
              style: const TextStyle(color: Colors.black38, fontSize: 10),
            ),
          ),
        ],
      ),
    );
  }
 
  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Container(
            width: 30,
            height: 30,
            margin: const EdgeInsets.only(right: 8, bottom: 4),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [kPurple400, kPurple700],
              ),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(Icons.smart_toy_outlined, color: Colors.white, size: 16),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            decoration: BoxDecoration(
              color: kPurple50,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(18),
                topRight: Radius.circular(18),
                bottomRight: Radius.circular(18),
                bottomLeft: Radius.circular(4),
              ),
              border: Border.all(color: kPurple100),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (i) {
                return AnimatedBuilder(
                  animation: _dotController,
                  builder: (_, __) {
                    final delay = i * 0.15;
                    final value = (_dotController.value - delay).clamp(0.0, 1.0);
                    final offset = (value < 0.5 ? value * 2 : 2 - value * 2) * 5;
                    return Container(
                      margin: const EdgeInsets.symmetric(horizontal: 2.5),
                      child: Transform.translate(
                        offset: Offset(0, -offset),
                        child: Container(
                          width: 7,
                          height: 7,
                          decoration: const BoxDecoration(
                            shape: BoxShape.circle,
                            color: kPurple400,
                          ),
                        ),
                      ),
                    );
                  },
                );
              }),
            ),
          ),
        ],
      ),
    );
  }
 
  Widget _buildSuggestion(String label) {
    return GestureDetector(
      onTap: () {
        _controller.text = label;
        _sendMessage();
      },
      child: Container(
        margin: const EdgeInsets.only(right: 8),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: kPurple50,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: kPurple200),
        ),
        child: Text(
          label,
          style: const TextStyle(
            color: kPurple700,
            fontSize: 12,
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    );
  }
}