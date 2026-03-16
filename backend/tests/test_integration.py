import hashlib
import pytest
from unittest.mock import patch, MagicMock
from app.models import case as case_dao
from app.models import operator as operator_dao
from app.models import message as message_dao


def _make_wechat_xml(from_user, content, msg_id='123'):
    return f"""<xml>
        <ToUserName><![CDATA[gh_service]]></ToUserName>
        <FromUserName><![CDATA[{from_user}]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
        <MsgId>{msg_id}</MsgId>
    </xml>"""


@patch('app.routes.wechat.process_incoming_message')
def test_full_intake_flow(mock_process, client, app):
    """Multi-message WeChat conversation."""
    # First message
    mock_process.return_value = "Hi! I see you need a tow. What's your name?"
    xml = _make_wechat_xml('e2e_user_1', 'I need a tow truck', '1001')
    response = client.post('/wechat/', data=xml, content_type='application/xml')
    assert response.status_code == 200
    assert b"What's your name?" in response.data or b'tow' in response.data.lower()

    # Second message
    mock_process.return_value = "Thanks John! Where are you located?"
    xml = _make_wechat_xml('e2e_user_1', 'My name is John, phone 555-1234', '1002')
    response = client.post('/wechat/', data=xml, content_type='application/xml')
    assert response.status_code == 200

    # Third message
    mock_process.return_value = "Got it! We have all your info. A tow truck is on the way!"
    xml = _make_wechat_xml('e2e_user_1', 'I am at 123 Main St, blue Honda Civic, flat tire', '1003')
    response = client.post('/wechat/', data=xml, content_type='application/xml')
    assert response.status_code == 200


def test_operator_views_case(client, app):
    """Create case, login, list, detail, update, add note."""
    with app.app_context():
        # Create operator and case
        operator_dao.create('op1', 'pass123', 'Operator One', 'admin')
        case = case_dao.create('wechat_user_x', 'tow_truck')
        case_dao.update(case.id, customer_name='Test Customer')
        message_dao.create('wechat_user_x', 'inbound', 'I need help', case_id=case.id)

    # Login
    login_resp = client.post('/api/auth/login', json={
        'username': 'op1', 'password': 'pass123'
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # List cases
    list_resp = client.get('/api/cases/', headers=headers)
    assert list_resp.status_code == 200
    cases = list_resp.get_json()['cases']
    assert len(cases) >= 1

    # Get detail
    detail_resp = client.get(f'/api/cases/{case.id}', headers=headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.get_json()
    assert detail['case']['customer_name'] == 'Test Customer'
    assert len(detail['messages']) == 1

    # Update case
    update_resp = client.patch(f'/api/cases/{case.id}',
        json={'status': 'assigned'},
        headers=headers
    )
    assert update_resp.status_code == 200
    assert update_resp.get_json()['status'] == 'assigned'

    # Add note
    note_resp = client.post(f'/api/cases/{case.id}/notes',
        json={'note': 'Dispatched tow truck'},
        headers=headers
    )
    assert note_resp.status_code == 201


@patch('app.routes.wechat.process_incoming_message')
def test_concurrent_wechat_users(mock_process, client, app):
    """Two users create separate cases."""
    mock_process.return_value = "I'll help you with that!"

    # User A
    xml_a = _make_wechat_xml('user_a', 'I need a tow truck', '2001')
    resp_a = client.post('/wechat/', data=xml_a, content_type='application/xml')
    assert resp_a.status_code == 200

    # User B
    xml_b = _make_wechat_xml('user_b', 'I need body repair', '2002')
    resp_b = client.post('/wechat/', data=xml_b, content_type='application/xml')
    assert resp_b.status_code == 200

    # Both should get responses
    assert b"help you" in resp_a.data
    assert b"help you" in resp_b.data


@patch('app.routes.wechat.process_incoming_message')
def test_returning_user_resumes_case(mock_process, client, app):
    """Same user, same case reused."""
    mock_process.return_value = "Welcome back! Let's continue."

    # First message
    xml1 = _make_wechat_xml('returning_e2e', 'Help me', '3001')
    resp1 = client.post('/wechat/', data=xml1, content_type='application/xml')
    assert resp1.status_code == 200

    # Second message - should go to same case
    mock_process.return_value = "Got your info. Anything else?"
    xml2 = _make_wechat_xml('returning_e2e', 'My name is Bob', '3002')
    resp2 = client.post('/wechat/', data=xml2, content_type='application/xml')
    assert resp2.status_code == 200

    # Verify process_incoming_message was called with same user both times
    assert mock_process.call_count == 2
    assert mock_process.call_args_list[0][0][0] == 'returning_e2e'
    assert mock_process.call_args_list[1][0][0] == 'returning_e2e'
