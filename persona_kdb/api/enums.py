from enum import Enum

# Status
class MessageStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    IN_PROGRESS = "in_progress"
class ConversationStatus(str, Enum):
    PREPARED = "prepared"
    IN_PROGRESS = "in_progress"
class SoulstoneRewardStatus(str, Enum):
    ACCEPTED = "accepted"
    PAID = "paid"
    REJECTED = "rejected"

# Type
class UserLevel(str, Enum):
    ADMIN = "admin"
    HOLDER = "holder"
    GUEST = "guest"
class UserType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
class MessageType(str, Enum):
    USER_FIRST = "user_first"
    ASSISTANT_FIRST = "assistant_first"
    USER_REPLY = "user_reply"
    ASSISTANT_REPLY = "assiatant_reply"
class ConversationType(str, Enum):
    START_BY_USER = "start_by_user"
    USER_MENTION_BY_ASSISTANT = "user_mention_by_assistant"
    PUBLIC_BY_ASSISTANT = "public_by_assistant"
