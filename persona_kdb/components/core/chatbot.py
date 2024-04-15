import json
from os import getenv
from operator import itemgetter
from google.cloud.firestore_v1.client import Client

from langchain.chains import LLMChain, RetrievalQA, StuffDocumentsChain
from langchain.chains.router import LLMRouterChain
from langchain.memory import ConversationKGMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.prompts import PromptTemplate
from langchain.schema import (
    StrOutputParser,
    Document
)
from langchain.schema.runnable import RunnablePassthrough, RunnableMap, RunnableLambda

from components.kdb.gsheet.persona import (
    get_persona_info, 
    get_variable_keys, 
    get_persona_template, 
    get_questionaire_template,
    get_evaluation_template,
)
from components.kdb.firebase import FirebaseUtils
from components.core.vectordb import vdb_index, vdb_retriever, format_docs
from components.core.llms import gpt3_5, gpt3_5_chat

def mars_openai_assistant_chain_factory(**kwargs):
    #TODO 
    from langchain.agents.openai_assistant import OpenAIAssistantRunnable
    raise NotImplementedError

#####
# Chain Factory
#####

def mars_evaluation_chain_factory(**kwargs):
    sheet_id = kwargs.get("sheet_id")
    output_key = kwargs.get("output_key", "output")
    input_vars= get_variable_keys(sheet_id, 'F7:F7')

    mars_template = PromptTemplate(
        template=get_evaluation_template(sheet_id),
        input_variables=input_vars,
    )
    chain = (
        {
            "conversation": RunnablePassthrough(),
        }
        | mars_template
        | gpt3_5_chat
        | StrOutputParser()
    )
    return chain

def mars_questionaire_chain_factory(**kwargs):
    sheet_id = kwargs.get("sheet_id")
    output_key = kwargs.get("output_key", "output")
    input_vars= get_variable_keys(sheet_id, 'D7:D7')

    prompt = PromptTemplate(
        template=get_questionaire_template(sheet_id),
        input_variables=input_vars,
    )
    retriever = vdb_retriever(
        "similarity", 
        vdb_index(), 
        k=1000
    )
    chain = (
        {
            "context": retriever | format_docs,
            "dummy_input": RunnablePassthrough(),
        }
        | prompt
        | gpt3_5_chat
        | StrOutputParser()
    )
    return chain

def mars_with_knowledge_chain_factory(**kwargs):
    sheet_id = kwargs.get("sheet_id")
    output_key = kwargs.get("output_key", "output")
    firebase_client: Client = kwargs.get("db")
    parent_message_id = kwargs.get("parent_message_id")
    conversation_id = FirebaseUtils.get_root_message_id(firebase_client, parent_message_id)

    prompt = PromptTemplate(
        template=get_persona_template(sheet_id),
        input_variables=get_variable_keys(sheet_id, 'B7:B7'),
    )
    retriever = vdb_retriever(
        "similarity", 
        vdb_index(), 
        k=5 # k should be 2 or less
    )
    conversation_history = RunnableLambda(
        lambda _: FirebaseUtils.get_conversation_history(
            firebase_client, 
            conversation_id,
        )[:-1]
    )

    rag_chain = (
        {
            "context": retriever | format_docs,
            "conversation_history": conversation_history,
            "question": RunnablePassthrough(),
        }
        | prompt
        | gpt3_5_chat
        | StrOutputParser()
    )

    return rag_chain

def mars_chain_factory(**kwargs):
    sheet_id = kwargs.get("sheet_id")
    output_key = kwargs.get("output_key", "output")

    input_vars= get_variable_keys(sheet_id)

    mars_template = PromptTemplate(
        template=get_persona_template(sheet_id),
        input_variables=input_vars,
    )
    # import pdb; pdb.set_trace()
    chain = LLMChain(
        llm=gpt3_5,
        prompt=mars_template,
        output_key=output_key,
        tags=["imperator_of_mars"],
        verbose=True,
    )
    return chain

def mars_with_knowledge_web_chain_factory(**kwargs):
    sheet_id = kwargs.get("sheet_id")
    output_key = kwargs.get("output_key", "output")
    firebase_client: Client = kwargs.get("db")
    prev_messages = kwargs.get("prev_messages")

    prompt = PromptTemplate(
        template=get_persona_template(sheet_id),
        input_variables=get_variable_keys(sheet_id, 'B7:B7'),
    )
    retriever = vdb_retriever(
        "similarity", 
        vdb_index(), 
        k=5 # k should be 2 or less
    )
    conversation_history = RunnableLambda(
        lambda _: prev_messages
    )
    # import pdb; pdb.set_trace()

    rag_chain = (
        {
            "context": retriever | format_docs,
            "conversation_history": conversation_history,
            "question": RunnablePassthrough(),
        }
        | prompt
        | gpt3_5_chat
        | StrOutputParser()
    )

    return rag_chain

#####
# Chain with each prompt
#####

def mars_evaluation(input):
    """
        Mars Extract & Summarize Knowledge Chain
    """
    #NOTE: input is the conversation history

    sheet_id = getenv("GOOGLE_SPREADSHEET_ID")

    output = mars_evaluation_chain_factory(
        sheet_id=sheet_id, 
        output_key="output",
    ).invoke(input)
    return output

def mars_questionaire():
    sheet_id = getenv("GOOGLE_SPREADSHEET_ID")

    output = mars_questionaire_chain_factory(
        sheet_id=sheet_id, 
        output_key="output",
    ).invoke("")

    return output

def mars_with_knowledge(
    parent_message_id,
    db,
    input="Hello, Elon?",
):
    sheet_id = getenv("GOOGLE_SPREADSHEET_ID")

    output = mars_with_knowledge_chain_factory(
        sheet_id=sheet_id, 
        output_key="output",
        parent_message_id=parent_message_id,
        db=db,
    ).invoke(input)

    return output

def mars(input="Hello, Elon?"):
    sheet_id = getenv("GOOGLE_SPREADSHEET_ID")
    input_values = get_persona_info(sheet_id)
    input_values["input"] = input

    output = mars_chain_factory(
        sheet_id=sheet_id, 
        output_key="output",
    ).run(input_values)

    #TODO: add logs to vectordb
    # import pdb; pdb.set_trace()
    # trainable = True
    # if trainable:
    #     memory.save_context({"input": input}, {"output": output})
    
    return output

def mars_with_knowledge_web(
    prev_messages,
    db,
    input="Hello, Elon?",
):
    """
        chains for soulfiction-allinone(web version).
        Input prev messages directly, not related with discord interface.
    """
    sheet_id = getenv("GOOGLE_SPREADSHEET_ID")
    # parsed_prev_messages = []
    # for prev_message in prev_messages:
    #     parsed_message = f"{prev_message['name']}: {prev_message['text']}"
    #     parsed_prev_messages.append(parsed_message)

    output = mars_with_knowledge_web_chain_factory(
        sheet_id=sheet_id, 
        output_key="output",
        prev_messages=prev_messages,
        db=db,
    ).invoke(input)

    return output

