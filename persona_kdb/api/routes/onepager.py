import json, os
from web3 import Web3
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse # for SSE(Server Sent Events)
# from apscheduler.schedulers.background import BackgroundScheduler
from typing import List, Optional, Union, Dict
import random
from collections import Counter
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

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
from api.models import (
    MockSingleModel,
    MarsReplyMessageModel, 
    SoulstoneRewardModel
)
from api.utils import now, encode_query

from components.core.chatbot import (
    mars_with_knowledge_web,
    mars_evaluation,
)
from components.kdb.firebase import FirebaseUtils
from components.kdb.gsheet.trainable_data import (
    append_knowledge
)

onepager_router = APIRouter(prefix='/onepager')
_debug=True
infura_api_key = os.getenv("INFURA_API_KEY")
w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{infura_api_key}"))

@onepager_router.post("/mock_reply", response_model=MarsReplyMessageModel)
async def mock_reply(
    content: str = Query(...,
                    description="user's input query to the Mars",
                    example="Hi Elon, how are you?"),
    evm_address: str = Query(..., description="user's ethereum address", example="0x8809537C69B9958B5F5c5aDf46A47E99754890A8"),
    prev_messages: Optional[List] = Query([], 
                                description="the list of previous messages", 
                                example=[
                                    "User: Hi Elon, how are you?", 
                                    "Assistant: I'm fine, thank you. How can I help you today?"]
                                ),
    db = Depends(get_db),
):
    try:
        response = mars_with_knowledge_web(
            prev_messages=prev_messages,
            db=db,
            input=content,
        )
        # output parsing
        response = response.strip("```json").strip("```").strip("\n")
        response = json.loads(response)

    except Exception as e:
        # raise HTTPException(
        #     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     detail=f"Internal Server Error - {'' if not _debug else str(e)}"
        # )
        return MarsReplyMessageModel(
            status=MessageStatus.ERROR,
            type=MessageType.ASSISTANT_REPLY,
            content="Mars doesn't work properly, refresh and try again",
            from_user_id=evm_address,
            from_username="mock_user",
            from_conversation_id="mock_conversation",
            parent_message_id="mock_parent_message_id",
            timestamp=now(),
        ).model_dump()

    return MarsReplyMessageModel(
        status=MessageStatus.SUCCESS,
        type=MessageType.ASSISTANT_REPLY if response["reward_triggering"] == False else MessageType.REQUEST_REWARD,
        content=response["output"],
        from_user_id=evm_address,
        from_username="mock_user",
        from_conversation_id="mock_conversation",
        parent_message_id="mock_parent_message_id",
        timestamp=now(),
    ).model_dump()

@onepager_router.post("/evaluate_conversation", response_model=SoulstoneRewardModel)
async def evaluate_conversation(
    evm_address: str = Query(..., description="user's ethereum address", example="0x8809537C69B9958B5F5c5aDf46A47E99754890A8"),
    messages: Optional[List] = Query([], 
                                description="the list of previous messages", 
                                example=[
                                    "User: Hi Elon, how are you?", 
                                    "Assistant: I'm fine, thank you. How can I help you today?"]
                                ),
    db = Depends(get_db),
):
    try:        
        response = mars_evaluation(
            input=messages,
        )
        # output parsing
        response = response.replace("\n", "").strip("```json").strip("```")
        response = json.loads(response)

        soullink_balance = (await get_soullink(evm_address=evm_address))['value']
        multiplier = (await get_multiplier(soullink_balance=soullink_balance))['value']

        reward_amount = float(multiplier) * response["score"]
        if reward_amount > 0:
            # append the summary of conversation to gsheet trainable_data
            append_knowledge(
                conversation_id="web_mock",
                knowledge_type="conversation",
                content=response["summary"],
                created_at=now(),
                user_id=evm_address,
                reward=reward_amount,
            )
            FirebaseUtils.give_soulstone(db, evm_address, reward_amount)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error, the core langchain doesn't work{'' if not _debug else str(e)}"
        )
    return SoulstoneRewardModel(
        status=SoulstoneRewardStatus.ACCEPTED if response['score'] > 0 else SoulstoneRewardStatus.REJECTED,
        recipient_id=evm_address,
        conversation_id="web_mock",
        multiplier=multiplier,
        amount=reward_amount,
        summarized_knowledge=response['summary'],
        reason=response['reason'],
        timestamp=now(),
    ).model_dump()

@onepager_router.get("/soulstone", response_model=MockSingleModel)
async def get_soulstone(
    evm_address: str = Query(..., description="EVM address", example="0x8809537C69B9958B5F5c5aDf46A47E99754890A8"),
    db = Depends(get_db),
): 
    try:
        soulstone = FirebaseUtils.get_soulstone(db, evm_address)
        print(soulstone)
        if soulstone:
            return MockSingleModel(
                value=soulstone,
            ).model_dump()
        else:
            return MockSingleModel(
                value=0,
            ).model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error, the core langchain doesn't work {'' if not _debug else str(e)}"
        )

@onepager_router.get("/soullink", response_model=MockSingleModel)
async def get_soullink(
    evm_address: str = Query(..., description="EVM address", example="0x8809537C69B9958B5F5c5aDf46A47E99754890A8"),
    db = Depends(get_db),
):
    # The contract address of the NFT and the account address
    nft_contract_address = '0xd6dbfb58c956949E3016151163ed6fD4301C4CE7'

    # ABI of the contract (simplified)
    abi = [{
        "constant": True,
        "inputs": [
            {
            "name": "_owner",
            "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
            "name": "",
            "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }]  # Add the ABI of the contract here

    # Create a contract object
    contract = w3.eth.contract(address=nft_contract_address, abi=abi)
    
    wallet = w3.to_checksum_address(evm_address)
    balance = contract.functions.balanceOf(wallet).call()

    return MockSingleModel(
        value=balance,
    ).model_dump()

@onepager_router.get("/multiplier", response_model=MockSingleModel)
async def get_multiplier(
    soullink_balance: int = Query(..., description="SoulLink balance", example=1),
): 
    try:
        if soullink_balance == 0:
            multiplier = 0
        else:
            multiplier = 1 + 0.1 * (soullink_balance - 1)
        return MockSingleModel(
            value=multiplier,
        ).model_dump()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error, the core langchain doesn't work {'' if not _debug else str(e)}"
        )