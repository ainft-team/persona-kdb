from langchain.chains import LLMChain, RetrievalQA, StuffDocumentsChain
from langchain.chains.router import LLMRouterChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.vectorstores.base import VectorStoreRetriever

def imperator_of_mars_chains(**kwargs):
    input_key = kwargs.get("input_key", "input")
    output_key = kwargs.get("output_key", "output")

    

evaluation_chains = ""

