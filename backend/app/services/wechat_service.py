import hashlib
import time
import xmltodict
import httpx


def verify_signature(signature: str, timestamp: str, nonce: str, token: str) -> bool:
    """Verify WeChat signature using SHA1(sorted([token, timestamp, nonce]))."""
    params = sorted([token, timestamp, nonce])
    raw = ''.join(params)
    computed = hashlib.sha1(raw.encode('utf-8')).hexdigest()
    return computed == signature


def parse_message(xml_data: str) -> dict:
    """Parse WeChat XML message into a dict."""
    parsed = xmltodict.parse(xml_data)
    msg = parsed.get('xml', {})
    return {
        'to_user': msg.get('ToUserName', ''),
        'from_user': msg.get('FromUserName', ''),
        'create_time': msg.get('CreateTime', ''),
        'msg_type': msg.get('MsgType', ''),
        'content': msg.get('Content', ''),
        'msg_id': msg.get('MsgId', ''),
    }


def build_text_reply(to_user: str, from_user: str, content: str) -> str:
    """Build a WeChat XML text reply with CDATA."""
    timestamp = int(time.time())
    return (
        f"<xml>"
        f"<ToUserName><![CDATA[{to_user}]]></ToUserName>"
        f"<FromUserName><![CDATA[{from_user}]]></FromUserName>"
        f"<CreateTime>{timestamp}</CreateTime>"
        f"<MsgType><![CDATA[text]]></MsgType>"
        f"<Content><![CDATA[{content}]]></Content>"
        f"</xml>"
    )


def _get_access_token(app_id: str, app_secret: str) -> str:
    """Get access token from WeChat API."""
    url = (
        f"https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    )
    response = httpx.get(url)
    data = response.json()
    return data.get('access_token', '')


def send_customer_service_message(openid: str, content: str,
                                   app_id: str, app_secret: str) -> None:
    """Send a customer service message via WeChat API."""
    access_token = _get_access_token(app_id, app_secret)
    url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
    payload = {
        "touser": openid,
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    httpx.post(url, json=payload)
