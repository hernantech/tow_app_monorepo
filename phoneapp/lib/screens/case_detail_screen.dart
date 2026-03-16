import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/cases_provider.dart';

class CaseDetailScreen extends StatefulWidget {
  final int caseId;

  const CaseDetailScreen({super.key, required this.caseId});

  @override
  State<CaseDetailScreen> createState() => _CaseDetailScreenState();
}

class _CaseDetailScreenState extends State<CaseDetailScreen> {
  final _noteController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CasesProvider>().loadCaseDetail(widget.caseId);
    });
  }

  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }

  Future<void> _addNote() async {
    final note = _noteController.text.trim();
    if (note.isEmpty) return;
    await context.read<CasesProvider>().addNote(widget.caseId, note);
    _noteController.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Case #${widget.caseId}'),
        centerTitle: true,
      ),
      body: Consumer<CasesProvider>(
        builder: (context, casesProvider, child) {
          if (casesProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (casesProvider.error != null) {
            return Center(
              child: Text(
                'Error: ${casesProvider.error}',
                style: const TextStyle(color: Colors.red),
              ),
            );
          }
          final caseData = casesProvider.selectedCase;
          if (caseData == null) {
            return const Center(child: Text('Case not found'));
          }

          final caseInfo = caseData['case'] ?? caseData;
          final messages = (caseData['messages'] as List<dynamic>?) ?? [];
          final notes = (caseData['notes'] as List<dynamic>?) ?? [];

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildCustomerInfoCard(caseInfo),
                const SizedBox(height: 16),
                _buildStatusUpdateSection(caseInfo),
                const SizedBox(height: 16),
                _buildConversationSection(messages),
                const SizedBox(height: 16),
                _buildNotesSection(notes),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildCustomerInfoCard(Map<String, dynamic> caseInfo) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Customer Info',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            _infoRow('Name', caseInfo['customer_name'] ?? 'N/A'),
            _infoRow('Phone', caseInfo['phone_number'] ?? 'N/A'),
            _infoRow('Location', caseInfo['location'] ?? 'N/A'),
            _infoRow('Vehicle', caseInfo['vehicle_info'] ?? 'N/A'),
            _infoRow('Damage', caseInfo['damage_description'] ?? 'N/A'),
            _infoRow('Type', caseInfo['case_type'] ?? 'N/A'),
          ],
        ),
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: Colors.grey,
              ),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  Widget _buildStatusUpdateSection(Map<String, dynamic> caseInfo) {
    final currentStatus = caseInfo['status'] as String? ?? 'collecting_info';
    final statuses = [
      'collecting_info',
      'pending_review',
      'assigned',
      'in_progress',
      'completed',
      'cancelled',
    ];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Update Status',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              initialValue: currentStatus,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              ),
              items: statuses.map((status) {
                return DropdownMenuItem(
                  value: status,
                  child: Text(_statusLabel(status)),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null && value != currentStatus) {
                  context.read<CasesProvider>().updateCaseStatus(widget.caseId, value);
                }
              },
            ),
          ],
        ),
      ),
    );
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'collecting_info':
        return 'Collecting Info';
      case 'pending_review':
        return 'Pending Review';
      case 'assigned':
        return 'Assigned';
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  Widget _buildConversationSection(List<dynamic> messages) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Conversation History',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            if (messages.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 8),
                child: Text(
                  'No messages yet',
                  style: TextStyle(color: Colors.grey),
                ),
              )
            else
              ...messages.map((msg) => _buildMessageBubble(msg)),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(Map<String, dynamic> msg) {
    final isInbound = msg['direction'] == 'inbound';
    return Align(
      alignment: isInbound ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.65,
        ),
        decoration: BoxDecoration(
          color: isInbound ? Colors.grey[200] : Colors.blue[100],
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              msg['content'] ?? '',
              style: const TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 4),
            Text(
              msg['created_at'] ?? '',
              style: TextStyle(fontSize: 10, color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotesSection(List<dynamic> notes) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Notes',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            if (notes.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 8),
                child: Text(
                  'No notes yet',
                  style: TextStyle(color: Colors.grey),
                ),
              )
            else
              ...notes.map((note) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.note, size: 16, color: Colors.grey),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(note['note'] ?? ''),
                              Text(
                                note['created_at'] ?? '',
                                style: TextStyle(
                                  fontSize: 11,
                                  color: Colors.grey[500],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  )),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _noteController,
                    decoration: const InputDecoration(
                      hintText: 'Add a note...',
                      border: OutlineInputBorder(),
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 8,
                      ),
                    ),
                    maxLines: 2,
                    minLines: 1,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _addNote,
                  icon: const Icon(Icons.send, color: Colors.blue),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
