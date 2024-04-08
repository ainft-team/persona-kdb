import json, os
from web3 import Web3
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
from api.models import (
    MockSingleModel
)
from api.utils import now, encode_query

from components.kdb.firebase import FirebaseUtils

onepager_router = APIRouter()
_debug=True
infura_api_key = os.getenv("INFURA_API_KEY")
w3 = Web3(Web3.HTTPProvider(f"https://mainnet.infura.io/v3/{infura_api_key}"))

@onepager_router.get("/soulstone", response_model=MockSingleModel)
async def get_soulstone(
    evm_address: str = Query(..., description="EVM address", example="0x8809537C69B9958B5F5c5aDf46A47E99754890A8"),
    db = Depends(get_db),
): 
    try:
        soulstone = FirebaseUtils.get_soulstone(db, evm_address)
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
    evm_address: str = Query(..., description="EVM address", example="0x8809537C69B9958B5F5c5aDf46A47E99754890A8"),
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