from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'), override=True)

# using langchain

# interpreter_assistant = OpenAIAssistantRunnable.create_assistant(
#     name="langchain assistant",
#     instructions="You are a personal math tutor. Write and run code to answer math questions.",
#     tools=[{"type": "code_interpreter"}],
#     model="gpt-4-1106-preview",
# )
# output = interpreter_assistant.invoke({"content": "What's 10 - 4 raised to the 2.7"})
# import pdb; pdb.set_trace()
# print(output)

# using bare openai api
# refer to https://platform.openai.com/docs/api-reference/assistants/createAssistant
from openai import OpenAI
from os import getenv

class OpenAIAssistantClient:
    _instance = None
    _debug = False
    _discord2thread = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIAssistantClient, cls).__new__(cls)
            cls._instance.client = OpenAI(api_key=getenv("OPENAI_API_KEY"))
        return cls._instance
    @classmethod
    def set_debug(cls, debug: bool):
        cls._debug = debug
    
    def create(self, name, instructions, tools, model):
        """
        returns:
            {
                "id": "asst_abc123",
                "object": "assistant",
                "created_at": 1698984975,
                "name": "Math Tutor",
                "description": null,
                "model": "gpt-4",
                "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
                "tools": [
                    {
                    "type": "code_interpreter"
                    }
                ],
                "file_ids": [],
                "metadata": {}
            }
        """
        try:
            assistant =  self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                tools=tools,
                model=model,
            )
            if self._debug: print(assistant)
            return assistant
        except Exception as e:
            print(e)
            return None
    
    def delete(self, assistant_id):
        """
        returns:
            {
                "id": "asst_abc123",
                "object": "assistant.deleted",
                "deleted": true
            }
        """
        try:
            response = self.client.beta.assistants.delete(assistant_id)
            if self._debug: print(response)
        except Exception as e:
            print(e)
            return None
    def retrieve(self, assistant_id=None):
        """
        returns:
            {
                "id": "asst_abc123",
                "object": "assistant",
                "created_at": 1698984975,
                "name": "Math Tutor",
                "description": null,
                "model": "gpt-4",
                "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
                "tools": [
                    {
                    "type": "code_interpreter"
                    }
                ],
                "file_ids": [],
                "metadata": {}
            }
        """
        try:
            if assistant_id is None:
                response = self.get_assistants(order="desc", limit="1")
                assistant = response.data[0]
            else:
                assistant = self.client.beta.assistants.retrieve(assistant_id)
            if self._debug: print(assistant)
            return assistant
        except Exception as e:
            print(e)
            return None
        
    def modify(self, assistant_id, instructions, tools, model, file_ids):
        """
        returns:
            {
                "id": "asst_abc123",
                "object": "assistant",
                "created_at": 1698984975,
                "name": "Math Tutor",
                "description": null,
                "model": "gpt-4",
                "instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
                "tools": [
                    {
                    "type": "code_interpreter"
                    }
                ],
                "file_ids": [],
                "metadata": {}
            }
        """
        assistant = self.client.beta.assistants.update(
            assistant_id, instructions, tools, model, file_ids
        )
        if self._debug: print(assistant)
        return assistant
    def get_assistants(self, order="desc", limit="20"):
        """
        returns:
            {
                "object": "list",
                "data": [
                    {
                        "id": "asst_abc123",
                        "object": "assistant",
                        "created_at": 1698982736,
                        "name": "Coding Tutor",
                        "description": null,
                        "model": "gpt-4",
                        "instructions": "You are a helpful assistant designed to make me better at coding!",
                        "tools": [],
                        "file_ids": [],
                        "metadata": {}
                    },
                    {
                        "id": "asst_abc456",
                        "object": "assistant",
                        "created_at": 1698982718,
                        "name": "My Assistant",
                        "description": null,
                        "model": "gpt-4",
                        "instructions": "You are a helpful assistant designed to make me better at coding!",
                        "tools": [],
                        "file_ids": [],
                        "metadata": {}
                    },
                    {
                        "id": "asst_abc789",
                        "object": "assistant",
                        "created_at": 1698982643,
                        "name": null,
                        "description": null,
                        "model": "gpt-4",
                        "instructions": null,
                        "tools": [],
                        "file_ids": [],
                        "metadata": {}
                    }
                ],
                "first_id": "asst_abc123",
                "last_id": "asst_abc789",
                "has_more": false
            }
        """
        assistants = self.client.beta.assistants.list(order=order, limit=limit)
        if self._debug: print(assistants)
        return assistants
    def create_thread_by_discord(self, assistant_id, discord_id):
        """
        returns:
            {
                "id": "thread_abc123",
                "object": "thread",
                "created_at": 1699012949,
                "metadata": {}
            }
        """
        try:
            thread = self.client.beta.threads.create()
            self._discord2thread[discord_id] = thread
            if self._debug: print(thread)
            return thread
        except Exception as e:
            print(e)
            return None
    def delete_thread_by_discord(self, discord_id):
        """
        returns:
            {
                "id": "thread_abc123",
                "object": "thread.deleted",
                "deleted": true
            }
        """
        try:
            thread_id = self._discord2thread.pop(discord_id)
            response = self.client.beta.threads.delete(thread_id)
            if self._debug: print(response)
        except Exception as e:
            print(e)
            return None
    def retrieve_thread_by_discord(self, discord_id):
        """
        returns:
            {
                "id": "thread_abc123",
                "object": "thread",
                "created_at": 1699012949,
                "metadata": {}
            }
        """
        try:
            thread_id = self._discord2thread[discord_id]
            thread = self.client.beta.threads.retrieve(thread_id)
            if self._debug: print(thread)
            return thread
        except Exception as e:
            print(e)
            return None
    def create_message(self, assistant_id, thread_id, content):
        """
        returns:
            {
                "id": "msg_abc123",
                "object": "message",
                "created_at": 1699012949,
                "thread": "thread_abc123",
                "content": "Hello!",
                "metadata": {}
            }
        """
        try:
            message = self.client.beta.threads.messages.create(
                thread_id,
                role="user",
                content=content,
            )
            if self._debug: print(message)
            return message
        except Exception as e:
            print(e)
            return None
    def get_messages(self, assistant_id, thread_id, order="desc", limit="20"):
        """
        returns:
            {
                "object": "list",
                "data": [
                    {
                        "id": "msg_abc123",
                        "object": "message",
                        "created_at": 1699012949,
                        "thread": "thread_abc123",
                        "content": "Hello!",
                        "metadata": {}
                    },
                    {
                        "id": "msg_abc456",
                        "object": "message",
                        "created_at": 1699012949,
                        "thread": "thread_abc123",
                        "content": "How are you?",
                        "metadata": {}
                    },
                    {
                        "id": "msg_abc789",
                        "object": "message",
                        "created_at": 1699012949,
                        "thread": "thread_abc123",
                        "content": "Good, how are you?",
                        "metadata": {}
                    }
                ],
                "first_id": "msg_abc123",
                "last_id": "msg_abc789",
                "has_more": false
            }
        """
        try:
            messages = self.client.beta.threads.messages.list(thread_id)
            if self._debug: print(messages.data)
            return messages.data
        except Exception as e:
            print(e)
            return None
    def create_run(self, assistant_id, thread_id):
        try:
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            if self._debug: print(run)
            return run
        except Exception as e:
            print(e)
            return None 
    def create_thread_and_run(self, assistant_id, thread):
        try:
            thread = {
                "messages": [
                    {"role": "user", "content": "Explain deep learning to a 5 year old."}
                ]
            } if thread is None else thread

            run = self.client.beta.threads.create_and_run(
                assistant_id=assistant_id,
                thread=thread,
            )
            if self._debug: print(run)
            return run
        except Exception as e:
            print(e)
            return None
    
client = OpenAIAssistantClient()
client.set_debug(True)

# my_assistant = client.create(
#     instructions="You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
#     name="Math Tutor",
#     tools=[{"type": "code_interpreter"}],
#     model="gpt-3.5-turbo-1106",
# )

# created_assistant_id = "asst_4dc0cezoEDuM67TzgKONhl76"
# my_assistant = client.retrieve(created_assistant_id)
my_assistant = client.retrieve()
# thread_id = client._discord2thread["0123"]
# thread = client.create_thread_by_discord(my_assistant.id, "0123")
# for i in range(5):
#     res = client.create_message(my_assistant.id, thread.id, f"Hello, World! {i}")
# msgs = client.get_messages(my_assistant.id, thread.id)
# run = client.create_thread_and_run(my_assistant.id, None)
msgs = client.get_messages(my_assistant.id, 'thread_OEIcroA4SwB6GKvOFkr6iRQq')