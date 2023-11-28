from os import getenv
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'))

from langchain import hub
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader, GoogleDriveLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import StrOutputParser, Document
from langchain.schema.runnable import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma, _import_pinecone
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
import pinecone

pinecone.init(
    api_key=getenv("PINECONE_API_KEY"),
    environment=getenv("PINECONE_ENV", "northamerica-northeast1-gcp"),
)
index = pinecone.Index(getenv("PINECONE_INDEX", "search-and-discovery"))
Pinecone = _import_pinecone()(
    index=index,
    embedding=OpenAIEmbeddings(openai_api_key=getenv("OPENAI_API_KEY")),
    text_key="text",
    namespace=getenv("PINECONE_NAMESPACE", "kdb_soulfiction"),
    distance_strategy="DOT_PRODUCT",
)

from components.core.llms import gpt3_5, gpt3_5_chat

def _loader(texts):
    docs = [Document(page_content=text[0]) for text in texts]
    return docs
def _splitter(docs, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(docs)

def _store(splits, embedding=OpenAIEmbeddings()):
    try:
        _ = Pinecone.add_documents(
            documents=splits,
        )
        return True
    except Exception as e:
        print(e)
        return False
    
def vdb_update(docs):
    docs = _loader(docs)
    splits =_splitter(docs, 1000, 200)
    if _store(splits, embedding=OpenAIEmbeddings(openai_api_key=getenv("OPENAI_API_KEY"))):
        print("Successfully updated the vector database.")
        return True
    else:
        print("Failed to update the vector database.")
        return False

def vdb_index():
    vectorstore = Pinecone.from_existing_index(
        index_name=getenv("PINECONE_INDEX", "search-and-discovery"),
        embedding=OpenAIEmbeddings(openai_api_key=getenv("OPENAI_API_KEY")),
        namespace=getenv("PINECONE_NAMESPACE", "kdb_soulfiction"),
    )
    return vectorstore
def vdb_retriever(search_type="similarity_score_threshold", vectorstore=vdb_index(), **search_kwargs):
    return vectorstore.as_retriever(
        search_type=search_type if search_type else "similarity_score_threshold",
        search_kwargs=search_kwargs if search_kwargs else {
            "k": 2, 
            "score_threshold": 0.5,
        },
    )

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)