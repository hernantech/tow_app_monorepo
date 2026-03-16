import json
import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


_llm_service_instance = None


class LLMService:
    def __init__(self, api_key: str = ''):
        kwargs = {
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 1024,
            'temperature': 0.3,
        }
        key = api_key or os.getenv('ANTHROPIC_API_KEY', '')
        if key:
            kwargs['api_key'] = key
        self.llm = ChatAnthropic(**kwargs)

    def classify_intent(self, user_message: str) -> str:
        """Classify user intent as tow_truck, body_shop, or unknown."""
        system_prompt = (
            "You are an auto-accident intake assistant. Classify the user's message into one of these categories:\n"
            "- 'tow_truck': The user needs towing service (car broke down, accident needs towing, stuck on road)\n"
            "- 'body_shop': The user needs body repair (dent, scratch, collision damage repair)\n"
            "- 'unknown': The message doesn't clearly indicate either service\n\n"
            "Respond with ONLY one of: tow_truck, body_shop, unknown"
        )
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]
        response = self.llm.invoke(messages)
        result = response.content.strip().lower()
        if result in ('tow_truck', 'body_shop', 'unknown'):
            return result
        return 'unknown'

    def extract_fields(self, user_message: str, conversation_history: list) -> dict:
        """Extract customer info fields from user message."""
        system_prompt = (
            "You are an auto-accident intake assistant. Extract the following fields from the user's message:\n"
            "- customer_name: The customer's name\n"
            "- phone_number: Their phone number\n"
            "- location: Their current location or address\n"
            "- vehicle_info: Vehicle make, model, color, or license plate\n"
            "- damage_description: Description of damage or issue\n\n"
            "Return a JSON object with these keys. Use null for fields not mentioned.\n"
            "Return ONLY the JSON object, no other text."
        )
        messages = [SystemMessage(content=system_prompt)]
        for msg in conversation_history:
            if msg.get('direction') == 'inbound':
                messages.append(HumanMessage(content=msg.get('content', '')))
            else:
                messages.append(AIMessage(content=msg.get('content', '')))
        messages.append(HumanMessage(content=user_message))

        response = self.llm.invoke(messages)
        try:
            return json.loads(response.content.strip())
        except (json.JSONDecodeError, TypeError):
            return {}

    def generate_collection_response(self, case_type: str, conversation_history: list,
                                      collected_fields: dict) -> str:
        """Generate an empathetic response asking for missing fields."""
        missing = [k for k, v in collected_fields.items()
                   if v is None and k in ('customer_name', 'phone_number', 'location',
                                           'vehicle_info', 'damage_description')]

        service_name = "towing" if case_type == "tow_truck" else "body repair"
        system_prompt = (
            f"You are a friendly and empathetic auto-accident intake assistant for {service_name} service. "
            "You are chatting on WeChat. Keep responses concise and warm.\n"
            f"Missing information: {', '.join(missing) if missing else 'none'}\n"
            f"Already collected: {json.dumps({k: v for k, v in collected_fields.items() if v is not None})}\n\n"
            "Ask for the missing information naturally. If all info is collected, confirm the details."
        )
        messages = [SystemMessage(content=system_prompt)]
        for msg in conversation_history:
            if msg.get('direction') == 'inbound':
                messages.append(HumanMessage(content=msg.get('content', '')))
            else:
                messages.append(AIMessage(content=msg.get('content', '')))

        response = self.llm.invoke(messages)
        return response.content.strip()


def get_llm_service(api_key: str = '') -> LLMService:
    """Return a singleton LLMService instance."""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService(api_key=api_key)
    return _llm_service_instance
