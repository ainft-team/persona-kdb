from langchain.chains import LLMChain, RetrievalQA, StuffDocumentsChain
from langchain.chains.router import LLMRouterChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.prompts import PromptTemplate

from kdb.persona import get_persona_info, get_variable_keys, get_persona_template

from core.llms import gpt3_5, gpt3_5_chat

def imperator_of_mars_chain_factory(**kwargs):
    sheet_id = kwargs.get("sheet_id")
    # input_key = kwargs.get("input_key", "input")
    output_key = kwargs.get("output_key", "output")

    input_vars= get_variable_keys(sheet_id)
    # input_values = get_persona_info(sheet_id)

    mars_template = PromptTemplate(
        template=get_persona_template(sheet_id),
        input_variables=input_vars,
    )
    # import pdb; pdb.set_trace()
    chain = LLMChain(
        llm=gpt3_5_chat,
        prompt=mars_template,
        output_key=output_key,
        tags=["imperator_of_mars"],
        verbose=True,
    )
    return chain

if __name__ == "__main__":
    import os
    imperator_of_mars_chains(sheet_id=os.getenv("GOOGLE_SPREADSHEET_ID"), output_key="output")

