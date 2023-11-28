#NOTE(jakepyo): refer to https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo
from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatOpenAI

gpt3_5 = OpenAI(
    temperature=0.3,
    max_tokens=5000,
    model_name='gpt-3.5-turbo-16k',
    streaming=False,
)

gpt3_5_chat = ChatOpenAI(
    temperature=0.3,
    max_tokens=4096,
    model_name='gpt-3.5-turbo-1106',
    streaming=True,
)