from os import getenv
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
load_dotenv(find_dotenv('.env'), override=True)

from google.cloud.firestore_v1.client import Client

# put lru_cache here
class QueryPreset:
    @staticmethod
    def collection_list(client: Client) -> str:
        c = client.collections()
        return [collection.id for collection in c]
    @staticmethod
    def get_conversation(client: Client, conversation_id):
        try:
            messages = client.collection("conversations").document(conversation_id).get()
            if messages.exists:
                return messages.to_dict()
            else:
                return None
        except Exception as e:
            print(e)
            return None
    def get_query_key(self) -> str:
        return list(self.query.keys())[0]

    def get_query_value(self):
        return list(self.query.values())[0]

class FirebaseUtils:
    @staticmethod
    def get_conversation_history(client: Client, conversation_id: str):
        try:
            conversations = client.collection("v2_conversations").document(conversation_id).get()
            if conversations.exists:
                # import pdb; pdb.set_trace()
                messages_indices = sorted(conversations.to_dict()['messages'].keys())
                messages_objects = [conversations.to_dict()['messages'][message_ind] for message_ind in messages_indices]
                if messages_objects[0]['type'] == 'user_first':
                    # append 'User', 'Assistant' in turn
                    modified_contents = [
                        f"User: {object['content']}" if i % 2 == 0 else f"Assistant: {object['content']}" 
                        for i, object in enumerate(messages_objects)
                    ]
                    return modified_contents
                else:
                    # append 'Assistant', 'User' in turn
                    modified_contents = [
                        f"Assistant: {object['content']}" if i % 2 == 0 else f"User: {object['content']}" 
                        for i, object in enumerate(messages_objects)
                    ]
                    return modified_contents
            else:
                return []
        except Exception as e:
            print(e)
            return None
    @staticmethod
    def get_participants(client: Client, conversation_id: str):
        try:
            conversations = client.collection("v2_conversations").document(conversation_id).get()
            if conversations.exists:
                return [str(user_id) for user_id in conversations.to_dict()['participants'].keys()]
            else:
                return [""]
        except Exception as e:
            print(e)
            return None
    @staticmethod
    def get_root_message_id(client: Client, child_message_id: str):
        try:
            messages = client.collection("v2_messages").document(child_message_id).get()
            if messages.exists:
                return messages.to_dict()["rootMessageId"]
            else:
                return None
        except Exception as e:
            print(e)
            return None
    @staticmethod
    def create_user_mock_message(
        client: Client, 
        evm_address: str, 
        root_message_id: Optional[str], 
        content: str
    ):
        try:
            now = datetime.utcnow() + timedelta(hours=9)
            #NOTE: to clarify that the message is a mock message in /v2_messages/{message_id}
            mock_offset = 7700000000000000000
            message_id = mock_offset + now.timestamp()

            user_message = client.collection("v2_messages").document(message_id).set({
                "content": content,
                "createdAt": now,
                "messageId": message_id,
                "rootMessageId": root_message_id,
                "senderId": evm_address,
                "type": "user_reply" if root_message_id else "user_first"
            })
            import pdb; pdb.set_trace()
        except Exception as e:
            print(e)
            return None
    @staticmethod
    def get_soulstone(client: Client, evm_address: str):
        try:
            messages = client.collection("mock_soulstone").document(evm_address).get()
            if messages.exists:
                return messages.to_dict()["value"]
            else:
                return None
        except Exception as e:
            print(e)
            return None
    @staticmethod
    def give_soulstone(client: Client, evm_address: str, amount: int):
        try:
            prev_value = FirebaseUtils.get_soulstone(client, evm_address)
            updated = client.collection("mock_soulstone").document(evm_address).set({
                "value": prev_value + amount,
            })
        except Exception as e:
            print(e)
            return None
    @staticmethod
    def get_soullink(client: Client, evm_address: str):
        try:
            messages = client.collection("mock_soullink").document(evm_address).get()
            if messages.exists:
                return messages.to_dict()["value"]
            else:
                return None
        except Exception as e:
            print(e)
            return None