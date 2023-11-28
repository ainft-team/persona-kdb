from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse # for SSE(Server Sent Events)
# from apscheduler.schedulers.background import BackgroundScheduler
from typing import List, Optional, Union
import random
from collections import Counter
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from api.db import get_db, get_rtdb
from api.schema import (
    User, 
    Message, 
    Conversation, 
    SoulStoneRewardTx
)
from api.enums import (
    MessageStatus, 
    ConversationStatus, 
    SoulstoneRewardStatus,
    UserLevel,
    UserType,
    MessageType,
    ConversationType,
)
from api.models import(
    MarsQuestionMessageModel,
    MarsReplyMessageModel, 
    SoulstoneRewardModel, 
    ConversationModel
)
from api.utils import now, encode_query

from components.core.chatbot import (
    mars, 
    mars_with_knowledge,
    mars_ens_knowledge,
    mars_questionaire,
)


v1_router = APIRouter()
_debug=True

@v1_router.get("/generate_question", response_model=MarsQuestionMessageModel)
async def generate_question(
    recipient_id: str = Query(..., description="discord user ID", example="10000000000000"),
    db = Depends(get_db),
): 
    try:
        question = mars_questionaire()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error, the core langchain doesn't work{'' if _debug else str(e)}"
        )
    return MarsQuestionMessageModel(
        status=MessageStatus.SUCCESS,
        content=question,
        to_user_id=recipient_id,
        timestamp=now(),
    ).dict()

@v1_router.post("/reply", response_model=MarsReplyMessageModel)
async def reply(
    content: str = Query(..., 
                    description="user's input query to the Mars",
                    example="Hi Elon, how are you?"),
    sender_id: str = Query(..., description="discord user ID", example="10000000000000"),
    sender_name: str = Query(..., description="discord user name", example="Elon Musk"),
    sender_discriminator: str = Query(..., description="discord user discriminator", example="0001"),
    parent_message_id: str = Query(None, description="discord parent message ID", example="10000000000000"),
    db = Depends(get_db),
):
    try:
        response = mars_with_knowledge(input=content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error, the core langchain doesn't work{'' if _debug else str(e)}"
        )
    return MarsReplyMessageModel(
        status=MessageStatus.SUCCESS,
        content=response,
        from_user_id=sender_id,
        from_username=f"{sender_name}#{sender_discriminator}",
        from_conversation_id=parent_message_id,
        parent_message_id=parent_message_id,
        timestamp=now(),
    ).dict()
