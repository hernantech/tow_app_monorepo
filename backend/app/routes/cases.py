from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import case as case_dao
from app.models import message as message_dao
from app.models import case_note as case_note_dao
from app.workflow.runner import process_incoming_message
from app.database import get_db

cases_bp = Blueprint('cases', __name__)

ALLOWED_UPDATE_FIELDS = {
    'status', 'customer_name', 'phone_number', 'location',
    'vehicle_info', 'damage_description', 'preferred_shop_id',
    'assigned_operator_id', 'case_type',
}


@cases_bp.route('/api/cases/', methods=['GET'])
@jwt_required()
def list_cases():
    """List cases with optional filters."""
    status = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    cases = case_dao.list_all(status=status, limit=limit, offset=offset)
    return jsonify({'cases': [case_dao.to_dict(c) for c in cases]})


@cases_bp.route('/api/cases/<int:case_id>', methods=['GET'])
@jwt_required()
def get_case(case_id):
    """Get a single case with messages and notes."""
    case = case_dao.get_by_id(case_id)
    if case is None:
        return jsonify({'error': 'Case not found'}), 404

    messages = message_dao.get_by_case(case_id)
    notes = case_note_dao.get_by_case(case_id)

    return jsonify({
        'case': case_dao.to_dict(case),
        'messages': [message_dao.to_dict(m) for m in messages],
        'notes': [case_note_dao.to_dict(n) for n in notes],
    })


@cases_bp.route('/api/cases/<int:case_id>', methods=['PATCH'])
@jwt_required()
def update_case(case_id):
    """Update allowed case fields."""
    case = case_dao.get_by_id(case_id)
    if case is None:
        return jsonify({'error': 'Case not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing request body'}), 400

    # Filter to allowed fields
    updates = {k: v for k, v in data.items() if k in ALLOWED_UPDATE_FIELDS}
    invalid_fields = [k for k in data.keys() if k not in ALLOWED_UPDATE_FIELDS]
    if invalid_fields:
        return jsonify({'error': f'Invalid fields: {", ".join(invalid_fields)}'}), 400

    if not updates:
        return jsonify({'error': 'No valid fields to update'}), 400

    updated_case = case_dao.update(case_id, **updates)
    return jsonify(case_dao.to_dict(updated_case))


@cases_bp.route('/api/cases/<int:case_id>/notes', methods=['POST'])
@jwt_required()
def add_note(case_id):
    """Add a note to a case."""
    case = case_dao.get_by_id(case_id)
    if case is None:
        return jsonify({'error': 'Case not found'}), 404

    data = request.get_json()
    if not data or not data.get('note'):
        return jsonify({'error': 'Note text is required'}), 400

    operator_id = int(get_jwt_identity())
    note = case_note_dao.create(case_id, operator_id, data['note'])
    return jsonify(case_note_dao.to_dict(note)), 201


def _check_device_limit(device_id):
    """Check message count for device. Returns (allowed, count, limit)."""
    limit = current_app.config.get('CHAT_MSG_LIMIT_PER_DEVICE', 75)
    with get_db() as db:
        row = db.execute(
            "SELECT message_count FROM device_usage WHERE device_id = ?",
            (device_id,)
        ).fetchone()
        count = row['message_count'] if row else 0
    return count < limit, count, limit


def _increment_device_count(device_id):
    """Increment message count for a device, creating the row if needed."""
    with get_db() as db:
        db.execute("""
            INSERT INTO device_usage (device_id, message_count, first_seen, last_seen)
            VALUES (?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(device_id) DO UPDATE SET
                message_count = message_count + 1,
                last_seen = CURRENT_TIMESTAMP
        """, (device_id,))


@cases_bp.route('/api/chat', methods=['POST'])
def chat():
    """Send a message to the AI intake agent. Requires API key and device ID."""
    # Validate API key
    expected_key = current_app.config.get('CHAT_API_KEY', '')
    provided_key = request.headers.get('X-API-Key', '')
    if not expected_key or provided_key != expected_key:
        return jsonify({'error': 'Invalid or missing API key'}), 401

    # Validate device ID
    device_id = request.headers.get('X-Device-ID', '')
    if not device_id:
        return jsonify({'error': 'Device ID is required'}), 400

    # Check rate limit
    allowed, count, limit = _check_device_limit(device_id)
    if not allowed:
        return jsonify({
            'error': 'Message limit reached for this device',
            'used': count,
            'limit': limit,
        }), 429

    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'error': 'Message is required'}), 400

    user_id = data.get('user_id', device_id)
    message_text = data['message']

    try:
        response_text = process_incoming_message(user_id, message_text)
        _increment_device_count(device_id)
        active_case = case_dao.get_active_by_wechat_user(user_id)

        # Return remaining count so the app can show it
        remaining = limit - (count + 1)
        return jsonify({
            'response': response_text,
            'case_id': active_case.id if active_case else None,
            'status': active_case.status if active_case else None,
            'remaining_messages': remaining,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
