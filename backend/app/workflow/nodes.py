from app.services.llm_service import get_llm_service
from app.models import case as case_dao
from app.models import message as message_dao


def classify_intent(state: dict) -> dict:
    """Classify user intent and create a case if valid."""
    llm = get_llm_service()
    user_message = state['incoming_message']
    wechat_user_id = state['wechat_user_id']

    intent = llm.classify_intent(user_message)

    if intent == 'unknown':
        return {
            'intent': 'unknown',
            'response_text': "I'm sorry, I'm not sure what service you need. "
                           "Could you please let me know if you need a tow truck or body shop repair?",
            'collection_complete': False,
        }

    # Create a new case
    new_case = case_dao.create(wechat_user_id, intent)

    # Log the inbound message
    message_dao.create(
        wechat_user_id=wechat_user_id,
        direction='inbound',
        content=user_message,
        case_id=new_case.id,
    )

    return {
        'intent': intent,
        'case_id': new_case.id,
        'case_type': intent,
        'collection_complete': False,
    }


def collect_info(state: dict) -> dict:
    """Extract fields, update case, and generate a collection response."""
    llm = get_llm_service()
    wechat_user_id = state['wechat_user_id']
    user_message = state['incoming_message']
    case_id = state.get('case_id')

    # Get conversation history for this case
    conversation_history = []
    if case_id:
        msgs = message_dao.get_by_case(case_id)
        conversation_history = [message_dao.to_dict(m) for m in msgs]

    # Extract fields from message
    extracted = llm.extract_fields(user_message, conversation_history)

    # Merge into state - don't overwrite non-None with None
    field_names = ['customer_name', 'phone_number', 'location', 'vehicle_info', 'damage_description']
    updates = {}
    for field in field_names:
        extracted_val = extracted.get(field)
        if extracted_val is not None:
            updates[field] = extracted_val
        elif state.get(field) is not None:
            updates[field] = state[field]

    # Build collected_fields for response generation
    collected_fields = {}
    for field in field_names:
        if field in updates and updates[field] is not None:
            collected_fields[field] = updates[field]
        elif state.get(field) is not None:
            collected_fields[field] = state[field]
        else:
            collected_fields[field] = None

    # Update case in DB
    if case_id:
        db_updates = {k: v for k, v in collected_fields.items() if v is not None}
        if db_updates:
            case_dao.update(case_id, **db_updates)

    # Check if all fields collected
    all_collected = all(collected_fields.get(f) is not None for f in field_names)
    collection_complete = False

    if all_collected and case_id:
        case_dao.update(case_id, status='pending_review')
        collection_complete = True

    # Generate response
    case_type = state.get('case_type', 'tow_truck')
    response = llm.generate_collection_response(case_type, conversation_history, collected_fields)

    # Log outbound message
    if case_id:
        message_dao.create(
            wechat_user_id=wechat_user_id,
            direction='outbound',
            content=response,
            case_id=case_id,
        )

    result = {
        'response_text': response,
        'collection_complete': collection_complete,
    }
    result.update(collected_fields)
    return result


def route_after_classify(state: dict) -> str:
    """Route based on intent classification."""
    if state.get('intent') == 'unknown':
        return '__end__'
    return 'collect_info'
