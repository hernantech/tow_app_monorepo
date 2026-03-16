from typing import Optional, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class IntakeState(TypedDict):
    wechat_user_id: str
    incoming_message: str
    messages: Annotated[list[BaseMessage], add_messages]
    intent: Optional[str]
    case_id: Optional[int]
    case_type: Optional[str]
    customer_name: Optional[str]
    phone_number: Optional[str]
    location: Optional[str]
    vehicle_info: Optional[str]
    damage_description: Optional[str]
    collection_complete: bool
    response_text: str
