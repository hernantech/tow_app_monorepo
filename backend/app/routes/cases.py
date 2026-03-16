from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import case as case_dao
from app.models import message as message_dao
from app.models import case_note as case_note_dao
from app.workflow.runner import process_incoming_message

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


@cases_bp.route('/api/chat', methods=['POST'])
def chat():
    """Send a message to the AI intake agent. No auth required (simulates WeChat user)."""
    data = request.get_json()
    if not data or not data.get('message'):
        return jsonify({'error': 'Message is required'}), 400

    user_id = data.get('user_id', 'app_user_default')
    message_text = data['message']

    try:
        response_text = process_incoming_message(user_id, message_text)
        # Find the active case for this user to return case_id
        active_case = case_dao.get_active_by_wechat_user(user_id)
        return jsonify({
            'response': response_text,
            'case_id': active_case.id if active_case else None,
            'status': active_case.status if active_case else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
