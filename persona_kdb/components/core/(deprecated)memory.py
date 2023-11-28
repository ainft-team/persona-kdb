from os import getenv

from langchain.memory import VectorStoreRetrieverMemory
from langchain.memory.kg import ConversationKGMemory
from langchain.embeddings import OpenAIEmbeddings

from components.core.vectordb import PineconeInstance

p_instance = PineconeInstance(
    index_name=getenv("PINECONE_INDEX"),
    namespace="kdb_soulfiction",
    embedding=OpenAIEmbeddings(),
)
vectorstore = p_instance.get_vectorstore()
retriever = p_instance.get_retriever()

memory = VectorStoreRetrieverMemory(
    retriever=retriever,
    memory_key="history",
    input_key=None,
    vectorstore=vectorstore,
)