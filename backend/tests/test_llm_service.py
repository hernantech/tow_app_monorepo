import pytest
from unittest.mock import patch, MagicMock
from app.services.llm_service import LLMService


@pytest.fixture
def llm_service():
    with patch('app.services.llm_service.ChatAnthropic') as MockChat:
        service = LLMService(api_key='test-key')
        yield service, MockChat


def test_classify_tow_truck(app, llm_service):
    service, _ = llm_service
    with app.app_context():
        mock_response = MagicMock()
        mock_response.content = 'tow_truck'
        service.llm.invoke = MagicMock(return_value=mock_response)

        result = service.classify_intent('My car broke down on the highway')
        assert result == 'tow_truck'


def test_classify_body_shop(app, llm_service):
    service, _ = llm_service
    with app.app_context():
        mock_response = MagicMock()
        mock_response.content = 'body_shop'
        service.llm.invoke = MagicMock(return_value=mock_response)

        result = service.classify_intent('I have a dent in my car door')
        assert result == 'body_shop'


def test_classify_unknown(app, llm_service):
    service, _ = llm_service
    with app.app_context():
        mock_response = MagicMock()
        mock_response.content = 'unknown'
        service.llm.invoke = MagicMock(return_value=mock_response)

        result = service.classify_intent('Hello there')
        assert result == 'unknown'


def test_generate_returns_string(app, llm_service):
    service, _ = llm_service
    with app.app_context():
        mock_response = MagicMock()
        mock_response.content = 'I understand you need help. Could you tell me your name?'
        service.llm.invoke = MagicMock(return_value=mock_response)

        result = service.generate_collection_response(
            'tow_truck', [],
            {'customer_name': None, 'phone_number': None, 'location': None,
             'vehicle_info': None, 'damage_description': None}
        )
        assert isinstance(result, str)
        assert len(result) > 0


def test_extract_parses_json(app, llm_service):
    service, _ = llm_service
    with app.app_context():
        mock_response = MagicMock()
        mock_response.content = '{"customer_name": "John", "phone_number": "555-1234", "location": null, "vehicle_info": null, "damage_description": null}'
        service.llm.invoke = MagicMock(return_value=mock_response)

        result = service.extract_fields('My name is John, call me at 555-1234', [])
        assert result['customer_name'] == 'John'
        assert result['phone_number'] == '555-1234'
        assert result['location'] is None


def test_extract_handles_invalid_json(app, llm_service):
    service, _ = llm_service
    with app.app_context():
        mock_response = MagicMock()
        mock_response.content = 'This is not valid JSON at all'
        service.llm.invoke = MagicMock(return_value=mock_response)

        result = service.extract_fields('some message', [])
        assert result == {}
