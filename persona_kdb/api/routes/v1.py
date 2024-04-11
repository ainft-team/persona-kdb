import json
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse # for SSE(Server Sent Events)
# from apscheduler.schedulers.background import BackgroundScheduler
from typing import List, Optional, Union
import random
from collections import Counter
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from api.db import get_db
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
    mars_evaluation,
    mars_questionaire,
    mars_with_knowledge_web
)
from components.kdb.firebase import FirebaseUtils
from components.kdb.gsheet.trainable_data import (
    append_knowledge
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
            detail=f"Internal Server Error, the core langchain doesn't work{'' if not _debug else str(e)}"
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
        response = mars_with_knowledge(
            parent_message_id=parent_message_id,
            db=db,
            input=content,
        )
        # output parsing
        response = response.strip("```json").strip("```").strip("\n")
        response = json.loads(response)
        conversation_id = FirebaseUtils.get_root_message_id(db, parent_message_id)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error on reply or parse error {'' if not _debug else str(e)}"
        )
    return MarsReplyMessageModel(
        status=MessageStatus.SUCCESS,
        type=MessageType.ASSISTANT_REPLY if response["reward_triggering"] == False else MessageType.REQUEST_REWARD,
        content=response["output"],
        from_user_id=sender_id,
        from_username=f"{sender_name}#{sender_discriminator}",
        from_conversation_id=conversation_id,
        parent_message_id=parent_message_id,
        timestamp=now(),
    ).dict()

@v1_router.post("/evaluate_conversation", response_model=SoulstoneRewardModel)
async def evaluate_conversation(
    conversation_id: str = Query(..., 
                    description="conversation ID",
                    example="10000000000000"),
    db = Depends(get_db),
):
    try:
        #FIXME(jakepyo): replace Mars Discord ID to not hard-coded one
        MARS_DISCORD_ID = "1022765839067398155"
        conversation_history = FirebaseUtils.get_conversation_history(db, conversation_id)
        participants = FirebaseUtils.get_participants(db, conversation_id)
        recipient_id = participants[0] if participants[0] != MARS_DISCORD_ID else participants[1]
        response = mars_evaluation(
            input=conversation_history,
        )
        # output parsing
        response = response.replace("\n", "").strip("```json").strip("```")
        response = json.loads(response)

        multiplier_ref = db.collection("v2_multiplier").document(recipient_id).get()
        if multiplier_ref.exists:
            multiplier = multiplier_ref.to_dict()["multiplier"]
        else:
            multiplier = 0

        reward_amount = float(multiplier) * response["score"]
        if reward_amount > 0:
            # append the summary of conversation to gsheet trainable_data
            append_knowledge(
                conversation_id=conversation_id,
                knowledge_type="conversation",
                content=response["summary"],
                created_at=now(),
                user_id=recipient_id,
                reward=reward_amount,
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error, the core langchain doesn't work{'' if not _debug else str(e)}"
        )
    return SoulstoneRewardModel(
        status=SoulstoneRewardStatus.ACCEPTED if response['score'] > 0 else SoulstoneRewardStatus.REJECTED,
        recipient_id=recipient_id,
        conversation_id=conversation_id,
        multiplier=multiplier,
        amount=reward_amount,
        summarized_knowledge=response['summary'],
        reason=response['reason'],
        timestamp=now(),
    ).dict()