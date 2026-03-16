import hashlib
import pytest
from unittest.mock import patch


def _make_signature(token, timestamp, nonce):
    params = sorted([token, timestamp, nonce])
    raw = ''.join(params)
    return hashlib.sha1(raw.encode('utf-8')).hexdigest()


def test_get_valid_signature(client):
    token = 'test_token'
    timestamp = '1234567890'
    nonce = 'abc123'
    echostr = 'echo_test_string'
    signature = _make_signature(token, timestamp, nonce)

    response = client.get(
        f'/wechat/?signature={signature}&timestamp={timestamp}&nonce={nonce}&echostr={echostr}'
    )
    assert response.status_code == 200
    assert response.data.decode() == echostr


def test_get_invalid_signature(client):
    response = client.get(
        '/wechat/?signature=invalid&timestamp=123&nonce=abc&echostr=test'
    )
    assert response.status_code == 403


@patch('app.routes.wechat.process_incoming_message')
def test_post_text_message(mock_process, client):
    mock_process.return_value = 'Thank you for your message!'

    xml = """<xml>
        <ToUserName><![CDATA[gh_service]]></ToUserName>
        <FromUserName><![CDATA[user_openid]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[I need a tow truck]]></Content>
        <MsgId>1234567890</MsgId>
    </xml>"""

    response = client.post('/wechat/', data=xml, content_type='application/xml')
    assert response.status_code == 200
    assert b'Thank you for your message!' in response.data
    mock_process.assert_called_once_with('user_openid', 'I need a tow truck')


@patch('app.routes.wechat.process_incoming_message')
def test_post_image_message(mock_process, client):
    xml = """<xml>
        <ToUserName><![CDATA[gh_service]]></ToUserName>
        <FromUserName><![CDATA[user_openid]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[image]]></MsgType>
        <PicUrl><![CDATA[http://example.com/pic.jpg]]></PicUrl>
        <MsgId>1234567890</MsgId>
    </xml>"""

    response = client.post('/wechat/', data=xml, content_type='application/xml')
    assert response.status_code == 200
    assert b'text messages' in response.data
    mock_process.assert_not_called()


@patch('app.routes.wechat.process_incoming_message')
def test_post_with_error(mock_process, client):
    mock_process.side_effect = Exception('LLM error')

    xml = """<xml>
        <ToUserName><![CDATA[gh_service]]></ToUserName>
        <FromUserName><![CDATA[user_openid]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[Help]]></Content>
        <MsgId>1234567890</MsgId>
    </xml>"""

    response = client.post('/wechat/', data=xml, content_type='application/xml')
    assert response.status_code == 500
