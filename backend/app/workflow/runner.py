from app.workflow.graph import intake_graph
from app.workflow.nodes import collect_info
from app.models import case as case_dao
from app.models import message as message_dao


def process_incoming_message(wechat_user_id: str, message_text: str) -> str:
    """Process an incoming WeChat message and return a response."""
    # Check for active case
    active_case = case_dao.get_active_by_wechat_user(wechat_user_id)

    if active_case:
        # Log inbound message
        message_dao.create(
            wechat_user_id=wechat_user_id,
            direction='inbound',
            content=message_text,
            case_id=active_case.id,
        )

        # Reconstruct state and call collect_info directly
        state = {
            'wechat_user_id': wechat_user_id,
            'incoming_message': message_text,
            'messages': [],
            'intent': active_case.case_type,
            'case_id': active_case.id,
            'case_type': active_case.case_type,
            'customer_name': active_case.customer_name,
            'phone_number': active_case.phone_number,
            'location': active_case.location,
            'vehicle_info': active_case.vehicle_info,
            'damage_description': active_case.damage_description,
            'collection_complete': False,
            'response_text': '',
        }
        result = collect_info(state)
        return result.get('response_text', '')
    else:
        # New user - invoke full graph
        initial_state = {
            'wechat_user_id': wechat_user_id,
            'incoming_message': message_text,
            'messages': [],
            'intent': None,
            'case_id': None,
            'case_type': None,
            'customer_name': None,
            'phone_number': None,
            'location': None,
            'vehicle_info': None,
            'damage_description': None,
            'collection_complete': False,
            'response_text': '',
        }
        result = intake_graph.invoke(initial_state)
        return result.get('response_text', '')
