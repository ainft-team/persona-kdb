from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatOpenAI

gpt3_5 = OpenAI(
    temperature=0,
    max_tokens=5000,
    model_name='gpt-3.5-turbo-16k',
    streaming=False,
)

gpt3_5_chat = ChatOpenAI(
    temperature=0,
    max_tokens=5000,
    model_name='gpt-3.5-turbo-16k',
    streaming=True,
)