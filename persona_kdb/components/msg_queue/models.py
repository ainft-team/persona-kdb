from pydantic import BaseModel, Field

class KafkaMessage(BaseModel):
    key: str = Field(..., description="The key of the message")
    value: str = Field(..., description="The value of the message")
    topic: str = Field(..., description="The topic of the message")
    partition: int = Field(..., description="The partition of the message")
    offset: int = Field(..., description="The offset of the message")
    timestamp: int = Field(..., description="The timestamp of the message")