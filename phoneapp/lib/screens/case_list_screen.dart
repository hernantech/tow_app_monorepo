import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/cases_provider.dart';
import '../models/intake_case.dart';
import 'case_detail_screen.dart';

class CaseListScreen extends StatefulWidget {
  const CaseListScreen({super.key});

  @override
  State<CaseListScreen> createState() => _CaseListScreenState();
}

class _CaseListScreenState extends State<CaseListScreen> {
  String? _selectedFilter;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CasesProvider>().loadCases();
    });
  }

  void _onFilterChanged(String? status) {
    setState(() {
      _selectedFilter = status;
    });
    context.read<CasesProvider>().loadCases(status: status);
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'collecting_info':
        return Colors.orange;
      case 'pending_review':
        return Colors.amber;
      case 'assigned':
        return Colors.blue;
      case 'in_progress':
        return Colors.indigo;
      case 'completed':
        return Colors.green;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _caseTypeIcon(String? caseType) {
    switch (caseType) {
      case 'tow_truck':
        return Icons.local_shipping;
      case 'body_shop':
        return Icons.car_repair;
      default:
        return Icons.description;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Cases'),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              final navigator = Navigator.of(context);
              await context.read<AuthProvider>().logout();
              if (mounted) {
                navigator.popUntil((route) => route.isFirst);
              }
            },
          ),
        ],
      ),
      body: Column(
        children: [
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                _buildFilterChip('All', null),
                const SizedBox(width: 8),
                _buildFilterChip('Pending Review', 'pending_review'),
                const SizedBox(width: 8),
                _buildFilterChip('Assigned', 'assigned'),
                const SizedBox(width: 8),
                _buildFilterChip('In Progress', 'in_progress'),
              ],
            ),
          ),
          Expanded(
            child: Consumer<CasesProvider>(
              builder: (context, casesProvider, child) {
                if (casesProvider.isLoading) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (casesProvider.error != null) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          'Error loading cases',
                          style: TextStyle(color: Colors.red[700]),
                        ),
                        const SizedBox(height: 8),
                        ElevatedButton(
                          onPressed: () => casesProvider.loadCases(status: _selectedFilter),
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  );
                }
                if (casesProvider.cases.isEmpty) {
                  return const Center(
                    child: Text(
                      'No cases found',
                      style: TextStyle(fontSize: 16, color: Colors.grey),
                    ),
                  );
                }
                return RefreshIndicator(
                  onRefresh: () => casesProvider.loadCases(status: _selectedFilter),
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: casesProvider.cases.length,
                    itemBuilder: (context, index) {
                      final intakeCase = casesProvider.cases[index];
                      return _buildCaseCard(intakeCase);
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label, String? status) {
    final isSelected = _selectedFilter == status;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) => _onFilterChanged(status),
      selectedColor: Colors.blue[100],
    );
  }

  Widget _buildCaseCard(IntakeCase intakeCase) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _statusColor(intakeCase.status).withValues(alpha: 0.15),
          child: Icon(
            _caseTypeIcon(intakeCase.caseType),
            color: _statusColor(intakeCase.status),
          ),
        ),
        title: Text(
          intakeCase.customerName ?? 'Case #${intakeCase.id}',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: _statusColor(intakeCase.status).withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                intakeCase.statusDisplay,
                style: TextStyle(
                  fontSize: 12,
                  color: _statusColor(intakeCase.status),
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              intakeCase.formattedDate,
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => CaseDetailScreen(caseId: intakeCase.id),
            ),
          );
        },
      ),
    );
  }
}
