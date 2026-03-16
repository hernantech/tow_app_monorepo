import pytest
from unittest.mock import patch, MagicMock
from app.workflow.runner import process_incoming_message
from app.models import case as case_dao


@pytest.fixture
def mock_llm(app):
    """Mock the LLM service singleton."""
    with patch('app.workflow.nodes.get_llm_service') as mock_get:
        mock_service = MagicMock()
        mock_get.return_value = mock_service
        yield mock_service


def test_new_user_tow_truck_flow(app, mock_llm):
    with app.app_context():
        mock_llm.classify_intent.return_value = 'tow_truck'
        mock_llm.extract_fields.return_value = {
            'customer_name': 'John',
            'phone_number': None,
            'location': None,
            'vehicle_info': None,
            'damage_description': None,
        }
        mock_llm.generate_collection_response.return_value = "Hi John! Can you tell me your location?"

        response = process_incoming_message('new_user_1', 'I need a tow truck, my name is John')
        assert 'John' in response or 'location' in response.lower() or len(response) > 0

        # Verify case was created
        case = case_dao.get_active_by_wechat_user('new_user_1')
        assert case is not None
        assert case.case_type == 'tow_truck'


def test_unknown_intent(app, mock_llm):
    with app.app_context():
        mock_llm.classify_intent.return_value = 'unknown'

        response = process_incoming_message('new_user_2', 'Hello there')
        assert 'not sure' in response.lower() or 'tow truck' in response.lower() or 'body shop' in response.lower()

        # No case should be created
        case = case_dao.get_active_by_wechat_user('new_user_2')
        assert case is None


def test_returning_user(app, mock_llm):
    with app.app_context():
        # First message - create case
        mock_llm.classify_intent.return_value = 'tow_truck'
        mock_llm.extract_fields.return_value = {
            'customer_name': 'Jane',
            'phone_number': None,
            'location': None,
            'vehicle_info': None,
            'damage_description': None,
        }
        mock_llm.generate_collection_response.return_value = "Hi Jane! Where are you?"
        process_incoming_message('returning_user', 'I need a tow, my name is Jane')

        # Second message - same user, existing case
        mock_llm.extract_fields.return_value = {
            'customer_name': None,
            'phone_number': '555-1234',
            'location': '123 Main St',
            'vehicle_info': None,
            'damage_description': None,
        }
        mock_llm.generate_collection_response.return_value = "Got it! What vehicle do you have?"
        response = process_incoming_message('returning_user', 'I am at 123 Main St, phone 555-1234')

        assert len(response) > 0

        # Should still be the same case
        case = case_dao.get_active_by_wechat_user('returning_user')
        assert case is not None
        assert case.phone_number == '555-1234'
        assert case.location == '123 Main St'
        assert case.customer_name == 'Jane'  # Preserved from first message


def test_collection_completes(app, mock_llm):
    with app.app_context():
        # First message creates case
        mock_llm.classify_intent.return_value = 'body_shop'
        mock_llm.extract_fields.return_value = {
            'customer_name': 'Bob',
            'phone_number': '555-9999',
            'location': '456 Oak Ave',
            'vehicle_info': 'Red Toyota Camry',
            'damage_description': 'Front bumper dent',
        }
        mock_llm.generate_collection_response.return_value = "Thank you! We have all your info."

        response = process_incoming_message('complete_user', 'I need body work. Name Bob, phone 555-9999, at 456 Oak Ave, red Toyota Camry, front bumper dent')

        assert len(response) > 0

        case = case_dao.get_active_by_wechat_user('complete_user')
        # Case should be pending_review now (no longer active collecting)
        # But get_active returns non-completed/cancelled, so pending_review is still "active"
        assert case is not None
        assert case.status == 'pending_review'


def test_state_reconstruction(app, mock_llm):
    with app.app_context():
        # Create a case manually
        case = case_dao.create('reconstruct_user', 'tow_truck')
        case_dao.update(case.id, customer_name='Alice', phone_number='555-0000')

        # Now incoming message should reconstruct state
        mock_llm.extract_fields.return_value = {
            'customer_name': None,
            'phone_number': None,
            'location': '789 Elm St',
            'vehicle_info': None,
            'damage_description': None,
        }
        mock_llm.generate_collection_response.return_value = "Thanks Alice! What vehicle?"

        response = process_incoming_message('reconstruct_user', 'I am at 789 Elm St')
        assert len(response) > 0

        updated_case = case_dao.get_by_id(case.id)
        assert updated_case.customer_name == 'Alice'  # Preserved
        assert updated_case.phone_number == '555-0000'  # Preserved
        assert updated_case.location == '789 Elm St'  # New
