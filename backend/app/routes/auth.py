from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import operator as operator_dao

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate operator and return JWT."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing request body'}), 400

    username = data.get('username', '')
    password = data.get('password', '')

    operator = operator_dao.get_by_username(username)
    if operator is None or not operator_dao.verify_password(operator, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(operator.id))
    return jsonify({
        'access_token': access_token,
        'operator': operator_dao.to_dict(operator),
    })


@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
def me():
    """Get current operator info."""
    operator_id = int(get_jwt_identity())
    operator = operator_dao.get_by_id(operator_id)
    if operator is None:
        return jsonify({'error': 'Operator not found'}), 404
    return jsonify({'operator': operator_dao.to_dict(operator)})


@auth_bp.route('/api/auth/register', methods=['POST'])
@jwt_required()
def register():
    """Register a new operator (admin only)."""
    current_id = int(get_jwt_identity())
    current_operator = operator_dao.get_by_id(current_id)
    if current_operator is None or current_operator.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing request body'}), 400

    username = data.get('username', '')
    password = data.get('password', '')
    full_name = data.get('full_name', '')
    role = data.get('role', 'operator')

    if not username or not password or not full_name:
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if username already exists
    existing = operator_dao.get_by_username(username)
    if existing:
        return jsonify({'error': 'Username already exists'}), 409

    new_operator = operator_dao.create(username, password, full_name, role)
    return jsonify(operator_dao.to_dict(new_operator)), 201
