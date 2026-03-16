import hashlib
import pytest
from app.services.wechat_service import verify_signature, parse_message, build_text_reply


def test_valid_signature(app):
    token = 'test_token'
    timestamp = '1234567890'
    nonce = 'abc123'
    params = sorted([token, timestamp, nonce])
    raw = ''.join(params)
    signature = hashlib.sha1(raw.encode('utf-8')).hexdigest()

    assert verify_signature(signature, timestamp, nonce, token) is True


def test_invalid_signature(app):
    assert verify_signature('invalidsig', '1234567890', 'abc123', 'test_token') is False


def test_xml_parsing(app):
    xml = """<xml>
        <ToUserName><![CDATA[gh_test]]></ToUserName>
        <FromUserName><![CDATA[user_openid]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[Hello!]]></Content>
        <MsgId>1234567890</MsgId>
    </xml>"""

    result = parse_message(xml)
    assert result['to_user'] == 'gh_test'
    assert result['from_user'] == 'user_openid'
    assert result['msg_type'] == 'text'
    assert result['content'] == 'Hello!'
    assert result['msg_id'] == '1234567890'


def test_reply_building(app):
    reply = build_text_reply('user123', 'gh_service', 'Hello back!')
    assert '<ToUserName><![CDATA[user123]]></ToUserName>' in reply
    assert '<FromUserName><![CDATA[gh_service]]></FromUserName>' in reply
    assert '<Content><![CDATA[Hello back!]]></Content>' in reply
    assert '<MsgType><![CDATA[text]]></MsgType>' in reply


def test_empty_field_handling(app):
    xml = """<xml>
        <ToUserName><![CDATA[gh_test]]></ToUserName>
        <FromUserName><![CDATA[user_openid]]></FromUserName>
        <CreateTime>1348831860</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
    </xml>"""

    result = parse_message(xml)
    assert result['to_user'] == 'gh_test'
    assert result['content'] == ''
    assert result['msg_id'] == ''
