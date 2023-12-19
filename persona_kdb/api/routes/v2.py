from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse # for SSE(Server Sent Events)
from fastapi.security import OAuth2PasswordRequestForm
from apscheduler.schedulers.background import BackgroundScheduler

from api import auth, security
from api.db import get_db
from api.schema import UserBase, UserInSession, UserInPassword, UserInHashedPassword, TokenData, Token
from api.schema import ConversationStatus, MessageStatus
from api.models import UserInRegisteredModel, ConversationModel
from api.core import chatbot, collect
from api.utils import now

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

v2_router = APIRouter()

@v2_router.post("/signin/", response_model=UserInRegisteredModel)
async def signin(
    user_in: UserInPassword,
    db: any = Depends(get_db)
):
    users_ref = db.collection('users')  
    # Check if username already exists
    users_with_username = users_ref.where('username', '==', user_in.username).stream()
    if any(users_with_username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Check if email already exists
    users_with_email = users_ref.where('email', '==', user_in.email).stream()
    if any(users_with_email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # If not, hash the password and add the new user
    hashed_password = security.get_password_hash(user_in.password)
    user_dict = user_in.dict(exclude={"password"})
    user_dict["hashed_password"] = hashed_password
    
    # Add to Firestore
    timestamp, new_user_ref = users_ref.add(user_dict)
    timestamp = timestamp.timestamp() # get timestamp

    ts_update_ref = users_ref.document(new_user_ref.id)
    user_dict["id"] = new_user_ref.id
    user_dict["timestamp"] = timestamp
    ts_update_ref.set(user_dict, merge=True)

    return user_dict


@v2_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)
):
    user = auth.get_user(username=form_data.username)
    if not user or not security.pwd_context.verify(
        form_data.password, user['hashed_password']
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data=user, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@v2_router.post("/chat")
async def chat_by_guest(
    query: str,
    session: str = Depends(auth.get_or_create_user_session),
    db = Depends(get_db),
):
    anon_users_ref = db.collection('users')
    anon_user_doc = anon_users_ref.document(session).get()
    #TODO
    # import pdb; pdb.set_trace()
    conversations_ref = db.collection('conversations')
    conversation_doc_ref = conversations_ref.document(anon_user_doc.get('session_id'))

    if not conversation_doc_ref.get().exists:
        ts = now()
        current_index = 0
        conversation_doc_ref.set({
            "user": anon_user_doc.get('username'),
            "session_id": session,
            "start_time": ts,
            "end_time": ts,
            "index": current_index,
            "status": ConversationStatus.IN_PROGRESS,
            "messages": {}
        })
    else:
        current_index = conversation_doc_ref.get().get('index')
    
    try:
        response = chatbot(input=query)
        conversation_doc_ref.update({
            f"messages.user_{current_index}": {
                "content": query,
                "status": MessageStatus.COMPLETED,
                "timestamp": now(),
            },
            f"messages.bot_{current_index}": {
                "content": response,
                "status": MessageStatus.COMPLETED,
                "timestamp": now(),
            },
            "index": current_index + 1,
            "status": ConversationStatus.COMPLETED,
        })
    except Exception as e:
        conversation_doc_ref.update({
            f"messages.user_{current_index}": {
                "content": query,
                "status": MessageStatus.COMPLETED,
                "timestamp": now(),
            },
            f"messages.bot_{current_index}": {
                "content": str(e),
                "status": MessageStatus.ERROR,
                "timestamp": now(),
            },
            "index": current_index + 1,
            "status": ConversationStatus.COMPLETED,
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error, the core langchain doesn't work"
        )

    return {"response": response, "status": "success"}

@v2_router.post("/chat_by_user")
async def chat_by_user(
    query: str,
    current_user: UserInHashedPassword = Depends(auth.get_current_user),
    db = Depends(get_db),
):
    users_ref = db.collection('users')
    user_doc = users_ref.document(current_user.id).get()
    if not user_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    conversations_ref = db.collection('conversations')
    conversation_doc_ref = conversations_ref.document(current_user.id)

    if not conversation_doc_ref.get().exists:
        ts = now()
        current_index = 0
        conversation_doc_ref.set({
            "user": current_user.username,
            "start_time": ts,
            "end_time": ts,
            "index": current_index,
            "status": ConversationStatus.IN_PROGRESS,
            "messages": {}
        })
    else:
        current_index = conversation_doc_ref.get().get('index')
    
    try:
        response = chatbot(input=query)
        conversation_doc_ref.update({
            f"messages.user_{current_index}": {
                "content": query,
                "status": MessageStatus.COMPLETED,
                "timestamp": now(),
            },
            f"messages.bot_{current_index}": {
                "content": response,
                "status": MessageStatus.COMPLETED,
                "timestamp": now(),
            },
            "index": current_index + 1,
            "status": ConversationStatus.COMPLETED,
        })
    except Exception as e:
        conversation_doc_ref.update({
            f"messages.user_{current_index}": {
                "content": query,
                "status": MessageStatus.COMPLETED,
                "timestamp": now(),
            },
            f"messages.bot_{current_index}": {
                "content": str(e),
                "status": MessageStatus.ERROR,
                "timestamp": now(),
            },
            "index": current_index + 1,
            "status": ConversationStatus.COMPLETED,
        })
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error, the core langchain doesn't work"
        )
    
    return {"response": response, "status": "success"}

# NOTE(jakepyo): for SSE
@v2_router.post("/chat_stream_by_user")
async def chat_stream_by_user(
    query: str,
    current_user: UserInHashedPassword = Depends(auth.get_current_user),
    db = Depends(get_db),
):
    #FIXME(jakepyo): code duplication with /chat
    async def event_stream():
        users_ref = db.collection('users')
        user_doc = users_ref.document(current_user.id).get()
        if not user_doc.exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        conversations_ref = db.collection('conversations')
        conversation_doc_ref = conversations_ref.document(current_user.id)

        if not conversation_doc_ref.get().exists:
            ts = now()
            current_index = 0
            conversation_doc_ref.set({
                "user": current_user.username,
                "start_time": ts,
                "end_time": ts,
                "index": current_index,
                "status": ConversationStatus.IN_PROGRESS,
                "messages": {}
            })
        else:
            current_index = conversation_doc_ref.get().get('index')
        
        try:
            response = chatbot(input=query)
            yield f"response: {response}\n"
            conversation_doc_ref.update({
                f"messages.user_{current_index}": {
                    "content": query,
                    "status": MessageStatus.COMPLETED,
                    "timestamp": now(),
                },
                f"messages.bot_{current_index}": {
                    "content": response,
                    "status": MessageStatus.COMPLETED,
                    "timestamp": now(),
                },
                "index": current_index + 1,
                "status": ConversationStatus.COMPLETED,
            })
        except Exception as e:
            conversation_doc_ref.update({
                f"messages.user_{current_index}": {
                    "content": query,
                    "status": MessageStatus.COMPLETED,
                    "timestamp": now(),
                },
                f"messages.bot_{current_index}": {
                    "content": str(e),
                    "status": MessageStatus.ERROR,
                    "timestamp": now(),
                },
                "index": current_index + 1,
                "status": ConversationStatus.COMPLETED,
            })
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error, the core langchain doesn't work"
            )
        
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@v2_router.get("/chat_history", response_model=ConversationModel)
async def chat_history(
    session_id: str = Depends(auth.get_or_create_user_session),
    db = Depends(get_db),
):
    conversation_doc = db.collection('conversations').document(session_id)
    conversation_list = conversation_doc.get()
    if conversation_list.exists:
        return conversation_list.to_dict()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

@v2_router.on_event('startup')
def collect_nfts():
    scheduler = BackgroundScheduler()
    scheduler.add_job(collect, 'cron', hour=0, minute=0, timezone='Asia/Seoul')
    scheduler.start()





# @v1_router.post("/reply", response_model=MarsReplyMessageModel)
# async def reply(
#     content: str = Query(..., 
#                     description="user's input query to the Mars",
#                     example="Hi Elon, how are you?"),
#     sender_id: str = Query(..., description="discord user ID", example="10000000000000"),
#     sender_name: str = Query(..., description="discord user name", example="Elon Musk"),
#     sender_discriminator: str = Query(..., description="discord user discriminator", example="0001"),
#     message_id: str = Query(..., description="discord message ID", example="10000000000000"),
#     parent_message_id: str = Query(None, description="discord parent message ID", example="10000000000000"),
#     db = Depends(get_db),
# ):
#     sender_type = UserType.USER
#     NEW_CONVERSATION = True if parent_message_id == None else False
#     """
#     # 1. initialization & validation of user's message
#     users_ref = db.collection('v2_users')
#     user_doc = users_ref.document(sender_id)
#     cur_user_doc = user_doc.get()

#     if not cur_user_doc.exists:
#         user_doc.set(User(
#             id=sender_id,
#             name=sender_name,
#             discriminator=sender_discriminator,
#             level=UserLevel.GUEST,
#             role=sender_type,
#             message_count_with_mars=1,
#             conversation_count_with_mars=1,
#             soulstone_reward=0,
#             soulstone_reward_txs={},
#         ).model_dump())
#     else:
#         if NEW_CONVERSATION:
#             user_doc.update({
#                 "message_count_with_mars": cur_user_doc.get('message_count_with_mars') + 1,
#                 "conversation_count_with_mars": cur_user_doc.get('conversation_count_with_mars') + 1,
#             })
#         else:
#             user_doc.update({
#                 "message_count_with_mars": cur_user_doc.get('message_count_with_mars') + 1,
#             })
    
#     messages_ref = db.collection('v2_messages')
#     message_doc = messages_ref.document(message_id)
#     message_type = f"{sender_type}_first" \
#                         if parent_message_id == None \
#                         else f"{sender_type}_reply"
    
#     if message_doc.get().exists:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Message already exists")
#     else:
#         message = Message(
#             id=message_id,
#             type=message_type,
#             content=content,
#             status=MessageStatus.SUCCESS,
#             created_at=now(),
#             sender_id=sender_id,
#             parent_message_id=parent_message_id,
#         ).model_dump()
#         message_doc.set(message)
    
#     conversation_ref = db.collection('v2_conversations')
#     conversation_doc = conversation_ref.document(message_id) \
#                             if message_type.endswith("first") \
#                             else conversation_ref.document(parent_message_id)
#     cur_conversation_doc = conversation_doc.get()
#     #TODO(jakepyo): PUBLIC_BY_ASSISTANT is not considered yet
#     conversation_type = ConversationType.START_BY_USER \
#                             if sender_type.endswith("user") \
#                             else ConversationType.USER_MENTION_BY_ASSISTANT
#     if not cur_conversation_doc.exists:
#         conversation_doc.set(Conversation(
#             id=parent_message_id if not NEW_CONVERSATION else message_id,
#             type=conversation_type,
#             status=ConversationStatus.IN_PROGRESS,
#             message_count=1,
#             created_at=now(),
#             updated_at=now(),
#             starter_user=sender_id,
#             participants={sender_id: 1},
#             messages={
#                 "0": message,
#             },
#         ).model_dump())
#     else:
#         conversation_type = cur_conversation_doc.get('type')
#         conversation_doc.update({
#             "status": ConversationStatus.IN_PROGRESS,
#             "updated_at": now(),
#             "participants": {
#                 **cur_conversation_doc.get('participants'),
#                 sender_id: cur_conversation_doc.get('participants')[sender_id] + 1
#             },
#             "messages": {
#                 **cur_conversation_doc.get('messages'),
#                 f"{cur_conversation_doc.get('message_count')}": message,
#             },
#         })
#     """
#     # 2. Generate the response from the Mars
#     try:
#         answer = mars(input=content)
#         response = answer.result
#         """
#         if NEW_CONVERSATION:
#             user_doc.update({
#                 "message_count_with_mars": cur_user_doc.get('message_count_with_mars') + 2,
#             })
#             message_doc.set(Message(
#                 id=f"{message_id}_1",
#                 type=MessageType.BOT_FIRST,
#                 content=response,
#                 status=MessageStatus.SUCCESS,
#                 created_at=now(),
#                 sender_id=sender_id,
#                 parent_message_id=message_id,
#             ).model_dump())

#             conversation_doc.update({
#                 "status": ConversationStatus.PREPARED,
#                 "message_count": cur_conversation_doc.get('message_count') + 2,
#                 "updated_at": now(),
#                 "participants": {sender_id: cur_conversation_doc.get('message_count') + 1},
#             })
#         """
#     except Exception as e:
#         """
#         conversation_doc.update({
#             "status": ConversationStatus.PREPARED,
#         })
#         """
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Internal Server Error, the core langchain doesn't work{'' if _debug else str(e)}"
#         )

#     # 3. Response to the discord bot
    
#     content = content.strip()
#     encoded_query = encode_query(content) # urlencode

#     users_ref = db.collection('users')
#     user_doc = anon_users_ref.document(discord_id).get()
    
#     threads_ref = db.collection('threads')
#     thread_doc_ref = threads_ref.document(anon_user_doc.get('discord_id'))

#     if not thread_doc_ref.get().exists:
#         ts = now()
#         cur_msg_count = 0
#         conversation_doc_ref.set(DiscordThread(
#             user_id=discord_id,
#             discord_id=discord_id,
#             created_at=ts,
#             updated_at=ts,
#             message_count=cur_msg_count,
#             status=ConversationStatus.IN_PROGRESS,
#             messages={}
#         ).dict())
#     else:
#         conversation_doc_ref.update({'status': ConversationStatus.IN_PROGRESS})
#         cur_msg_count = conversation_doc_ref.get().get('message_count')

#     conversation_doc_ref.update({
#         f"messages.{cur_msg_count}": Message(
#             type=UserType.HUMAN,
#             content=content,
#             status=MessageStatus.COMPLETED,
#             created_at=now()
#         ).dict(),
#         "message_count": cur_msg_count + 1,  
#         "updated_at": now(),
#     })

#     try:        
#         answer = mars(input=content)
#         response = answer.result
#         ref.child(f'{encoded_query}').set(output.cache_data)

#         conversation_doc_ref.update({
#             f"messages.{cur_msg_count + 1}": Message(
#                 type=UserType.BOT,
#                 content=response,
#                 status=MessageStatus.COMPLETED,
#                 created_at=now()
#             ).dict(),
#             "message_count": cur_msg_count + 2,
#             "updated_at": now(),
#             "status": ConversationStatus.PREPARED,
#         })
#     except Exception as e:
#         timestamp = now()
#         conversation_doc_ref.update({
#             f"messages.{cur_msg_count + 1}": Message(
#                 type=UserType.BOT,
#                 content=str(e),
#                 status=MessageStatus.ERROR,
#                 created_at=timestamp,
#             ).dict(),
#             "message_count": cur_msg_count + 2,
#             "updated_at": timestamp,
#             "status": ConversationStatus.PREPARED,
#         })
#         error_queries_doc_ref = db.collection('error_queries').document(timestamp)
#         error_queries_doc_ref.set({
#             "query": query,
#             "error": str(e),
#             "discord_id": discord_id,
#         })
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Internal Server Error, the core langchain doesn't work{'' if _debug else str(e)}"
#         )

#     return MarsReplyMessageModel(
#         status=MarsMessageStatus.SUCCESS,
#         discord_id=discord_id,
#         thread_id=thread_id,
#         amount=amount,
#         timestamp=now(),
#     ).dict()


# @v1_router.post("/giveReward", responseModel=SoulstoneRewardModel)
# async def give_reward(
#     discord_id: str = Query(..., description="discord ID", example="10000000000000"),
#     thread_id: str = Query(..., description="thread ID", example="10000000000000"),
#     amount: int = Query(..., description="amount of reward", example=1),
#     db = Depends(get_db),
# ):
#     #TODO
#     return SoulstoneRewardModel(
#         status=SoulstoneRewardStatus.SUCCESS,
#         discord_id=discord_id,
#         thread_id=thread_id,
#         amount=amount,
#         timestamp=now(),
#     ).dict()




# @v1_router.on_event('startup')
# def collect_nfts():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(collect, 'cron', hour=0, minute=0, timezone='Asia/Seoul')
#     scheduler.start()