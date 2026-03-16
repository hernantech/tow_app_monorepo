import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final List<_ChatMessage> _messages = [];
  bool _isLoading = false;
  String? _caseStatus;
  int? _remainingMessages;
  final String _userId = 'app_user_${DateTime.now().millisecondsSinceEpoch}';

  @override
  void initState() {
    super.initState();
    _messages.add(_ChatMessage(
      text: "Hi! I'm the QuickTow intake assistant. Tell me about your car situation and I'll help you get the right service.",
      isUser: false,
    ));
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _isLoading) return;

    setState(() {
      _messages.add(_ChatMessage(text: text, isUser: true));
      _isLoading = true;
    });
    _controller.clear();
    _scrollToBottom();

    try {
      final result = await ApiService.sendChatMessage(text, userId: _userId);
      setState(() {
        _messages.add(_ChatMessage(
          text: result['response'] ?? 'No response',
          isUser: false,
        ));
        _caseStatus = result['status'];
        _remainingMessages = result['remaining_messages'];
        _isLoading = false;
      });
    } catch (e) {
      final errorMsg = e.toString().replaceFirst('Exception: ', '');
      setState(() {
        _messages.add(_ChatMessage(
          text: errorMsg.contains('limit')
              ? 'You have reached the message limit for this device. Please contact support for assistance.'
              : 'Connection error. Make sure the backend is running.',
          isUser: false,
          isError: true,
        ));
        _isLoading = false;
      });
    }
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
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
      appBar: AppBar(
        title: const Text('AI Intake Assistant'),
        centerTitle: true,
        actions: [
          if (_remainingMessages != null)
            Padding(
              padding: const EdgeInsets.only(right: 4),
              child: Chip(
                label: Text(
                  '$_remainingMessages left',
                  style: TextStyle(
                    fontSize: 11,
                    color: _remainingMessages! < 10 ? Colors.red[800] : Colors.grey[700],
                  ),
                ),
                backgroundColor: _remainingMessages! < 10 ? Colors.red[50] : Colors.grey[100],
              ),
            ),
          if (_caseStatus != null)
            Padding(
              padding: const EdgeInsets.only(right: 12),
              child: Chip(
                label: Text(
                  _caseStatus == 'pending_review' ? 'Complete' : 'In Progress',
                  style: TextStyle(
                    fontSize: 11,
                    color: _caseStatus == 'pending_review'
                        ? Colors.green[800]
                        : Colors.orange[800],
                  ),
                ),
                backgroundColor: _caseStatus == 'pending_review'
                    ? Colors.green[50]
                    : Colors.orange[50],
              ),
            ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                return _buildBubble(msg);
              },
            ),
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              child: Row(
                children: [
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  SizedBox(width: 8),
                  Text('AI is thinking...', style: TextStyle(color: Colors.grey)),
                ],
              ),
            ),
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            padding: const EdgeInsets.fromLTRB(16, 8, 8, 24),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: 'Describe your car situation...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 10,
                      ),
                    ),
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _sendMessage(),
                    maxLines: 3,
                    minLines: 1,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _isLoading ? null : _sendMessage,
                  icon: const Icon(Icons.send),
                  color: Colors.blue,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBubble(_ChatMessage msg) {
    return Align(
      alignment: msg.isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: msg.isError
              ? Colors.red[50]
              : msg.isUser
                  ? Colors.blue[600]
                  : Colors.grey[200],
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(msg.isUser ? 16 : 4),
            bottomRight: Radius.circular(msg.isUser ? 4 : 16),
          ),
        ),
        child: Text(
          msg.text,
          style: TextStyle(
            fontSize: 15,
            color: msg.isError
                ? Colors.red[800]
                : msg.isUser
                    ? Colors.white
                    : Colors.black87,
          ),
        ),
      ),
    );
  }
}

class _ChatMessage {
  final String text;
  final bool isUser;
  final bool isError;

  _ChatMessage({required this.text, required this.isUser, this.isError = false});
}
