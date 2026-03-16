import 'package:intl/intl.dart';

class IntakeCase {
  final int id;
  final String wechatUserId;
  final String? caseType;
  final String status;
  final String? customerName;
  final String? phoneNumber;
  final String? location;
  final String? vehicleInfo;
  final String? damageDescription;
  final String? preferredShopId;
  final int? assignedOperatorId;
  final String createdAt;
  final String updatedAt;

  IntakeCase({
    required this.id,
    required this.wechatUserId,
    this.caseType,
    required this.status,
    this.customerName,
    this.phoneNumber,
    this.location,
    this.vehicleInfo,
    this.damageDescription,
    this.preferredShopId,
    this.assignedOperatorId,
    required this.createdAt,
    required this.updatedAt,
  });

  factory IntakeCase.fromJson(Map<String, dynamic> json) {
    return IntakeCase(
      id: json['id'],
      wechatUserId: json['wechat_user_id'],
      caseType: json['case_type'],
      status: json['status'],
      customerName: json['customer_name'],
      phoneNumber: json['phone_number'],
      location: json['location'],
      vehicleInfo: json['vehicle_info'],
      damageDescription: json['damage_description'],
      preferredShopId: json['preferred_shop_id'],
      assignedOperatorId: json['assigned_operator_id'],
      createdAt: json['created_at'] ?? '',
      updatedAt: json['updated_at'] ?? '',
    );
  }

  String get statusDisplay {
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

  String get caseTypeDisplay {
    switch (caseType) {
      case 'tow_truck':
        return 'Tow Truck';
      case 'body_shop':
        return 'Body Shop';
      default:
        return caseType ?? 'Unknown';
    }
  }

  String get formattedDate {
    try {
      final date = DateTime.parse(createdAt);
      return DateFormat('MMM d, yyyy h:mm a').format(date);
    } catch (_) {
      return createdAt;
    }
  }
}
