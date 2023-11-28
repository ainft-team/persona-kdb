from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime

from api.enums import MessageType, ConversationType
#####
# Schema for firebase
#####
#"v2_rewards"
# the key of the document is the tx_id
class SoulStoneRewardTx(BaseModel):
    tx_id: str
    amount: int
    recipient_id: str
    status: str
    created_at: Union[float, str, datetime]
#"v2_users"
# the key of the document is the user's discord id
class User(BaseModel):
    id: str
    name: str
    discriminator: Optional[str]
    level: str
    role: str
    message_count_with_mars: int
    conversation_count_with_mars: int
    soulstone_reward: int
    soulstone_reward_txs: Optional[dict[str, SoulStoneRewardTx]] # {tx_id: SoulStoneRewardTx}
#"v2_messages"
# the key of the document is the message id
class Message(BaseModel):
    id: str
    type: MessageType
    content: str
    status: str
    created_at: Union[float, str, datetime]
    sender_id: str
    parent_message_id: Optional[str] # If none, it's the root message
#"v2_conversations"
# the key of the document is the first message id
class Conversation(BaseModel):
    id: str
    type: ConversationType    
    status: Optional[str]
    message_count: Optional[int]
    created_at: Optional[Union[float, str, datetime]]
    updated_at: Optional[Union[float, str, datetime]]
    starter_user: str # Discord ID of the user or bot who started the conversation
    participants: dict[str, int] # {discord_id: message_count}
    messages: dict[str, Message] # {message_order: Message}