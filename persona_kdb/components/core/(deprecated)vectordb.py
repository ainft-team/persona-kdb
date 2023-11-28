from os import getenv
import pinecone
from langchain.vectorstores import _import_pinecone
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.base import VectorStoreRetriever

from typing import Optional

Pinecone = _import_pinecone()

class PineconeInstance:
    _instance = None
    _index_name = None
    _namespace = None
    _embedding = None
    _vectorstore = None
    _retriever = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            pinecone.init(
                api_key=getenv("PINECONE_API_KEY"),
                environment=getenv("PINECONE_ENV", "northamerica-northeast1-gcp"),
            )
            #initialize all class variables from kwargs
            for key, value in kwargs.items():
                key_added_underbar = '_' + key
                setattr(cls, key_added_underbar, value)
            cls._instance = super(PineconeInstance, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_index(cls):
        if cls._index_name is None:
            cls._index_name = getenv("PINECONE_INDEX_NAME")
        return pinecone.Index(cls._index_name)
    
    @classmethod
    def get_namespace(cls):
        if cls._namespace is None:
            cls._namespace = getenv("PINECONE_NAMESPACE")
        return cls._namespace
    @classmethod
    def set_namespace(cls, namespace):
        cls._namespace = namespace
    @classmethod
    def set_embedding(cls, embed_function=OpenAIEmbeddings()):
        if cls._embedding is None:
            cls._embedding = embed_function
        return cls._embedding
    @classmethod
    def get_vectorstore(cls) -> Optional[VectorStoreRetriever]:
        if cls._vectorstore is None:
            try:
                cls._vectorstore = Pinecone.from_existing_index(
                    index_name=cls._index_name,
                    embedding=cls._embedding,
                    namespace=cls._namespace,
                )
            except Exception as e:
                print(e, "Cannot fetch vectorstore")
                pass
        return cls._vectorstore
    @classmethod
    def get_retriever(cls) -> Optional[VectorStoreRetriever]:
        if cls._retriever is None:
            cls._retriever = VectorStoreRetriever(
                vectorstore=cls.get_vectorstore(),
                search_type="similarity",
            )
        return cls._retriever
    @classmethod
    def set_retriever(cls, retriever: VectorStoreRetriever):
        cls._retriever_dict[cls._namespace] = retriever
    
    @classmethod
    def insert_document(cls, document: dict):
        try:
            cls.get_vectorstore().from_texts(
                texts=[document],
                embedding=cls._embedding,
                ids=[document["id"]],
                namespace=cls._namespace,
                index_name=cls._index_name,
            )
        except Exception as e:
            print(e, "Failed to insert document")
            pass
    
