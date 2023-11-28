from enum import Enum
from pydantic import BaseModel

class ValueInputOption(str, Enum):
    RAW = "RAW"
    USER_ENTERED = "USER_ENTERED"
class MessageType(str, Enum):
    HUMAN = "Human"
    AI = "AI"

class SpreadSheetRow(BaseModel):
    createdAt: str
    messageType: MessageType
    content: str
    updatedAt: str