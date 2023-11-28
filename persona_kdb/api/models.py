from pydantic import BaseModel, Field
from typing import Optional, Union, Dict
from datetime import datetime

from api.enums import ConversationStatus, MessageStatus, SoulstoneRewardStatus
from api.schema import Message, Conversation
    
class ConversationModel(BaseModel):
    user_id: str
    discord_id: Optional[str]
    message_count: Optional[int]
    created_at: Optional[Union[float, str, datetime]]
    updated_at: Optional[Union[float, str, datetime]]
    status: Optional[ConversationStatus]
    messages: Optional[dict[str, Message]]

class MarsQuestionMessageModel(BaseModel):
    status: MessageStatus
    content: str
    to_user_id: str
    timestamp: Optional[Union[float, str, datetime]]
class MarsReplyMessageModel(BaseModel):
    status: MessageStatus
    content: Optional[str]
    from_user_id: str
    from_username: str
    from_conversation_id: str
    parent_message_id: str
    timestamp: Optional[Union[float, str, datetime]]

class SoulstoneRewardModel(BaseModel):
    status: SoulstoneRewardStatus
    discord_id: Optional[str]
    thread_id: Optional[str]
    amount: Optional[float]
    timestamp: Optional[Union[float, str, datetime]]