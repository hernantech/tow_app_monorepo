from flask import Blueprint, request, current_app
from app.services.wechat_service import verify_signature, parse_message, build_text_reply
from app.workflow.runner import process_incoming_message

wechat_bp = Blueprint('wechat', __name__)


@wechat_bp.route('/wechat/', methods=['GET'])
def verify():
    """WeChat server verification endpoint."""
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    echostr = request.args.get('echostr', '')
    token = current_app.config.get('WECHAT_TOKEN', 'default_token')

    if verify_signature(signature, timestamp, nonce, token):
        return echostr
    return 'Invalid signature', 403


@wechat_bp.route('/wechat/', methods=['POST'])
def handle_message():
    """Handle incoming WeChat messages."""
    try:
        xml_data = request.data.decode('utf-8')
        msg = parse_message(xml_data)

        # Only handle text messages
        if msg.get('msg_type') != 'text':
            reply = build_text_reply(
                msg['from_user'], msg['to_user'],
                "Sorry, I can only process text messages at the moment."
            )
            return reply, 200, {'Content-Type': 'application/xml'}

        # Process the message
        response_text = process_incoming_message(msg['from_user'], msg['content'])

        reply = build_text_reply(msg['from_user'], msg['to_user'], response_text)
        return reply, 200, {'Content-Type': 'application/xml'}
    except Exception as e:
        current_app.logger.error(f"Error handling WeChat message: {e}")
        return 'error', 500
