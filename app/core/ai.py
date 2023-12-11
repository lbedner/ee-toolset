from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import Document
from langchain.schema.messages import SystemMessage

from app.core.config import settings
from app.core.loader import load_documents
from app.core.log import ic, logger
from app.core.splitter import get_document_chunks
from app.core.vectorstore import get_vectorstore_retriever, vectorstore_path_exists

CHAT_HISTORY = "chat_history"


conversation_memories: dict[str, ConversationBufferMemory] = {}
conversation_prompts: dict[str, ChatPromptTemplate] = {}


def process_sources(sources):
    logger.info("\n\nSources:")
    for source in sources:
        logger.info(source.metadata["source"])


def chat_with_llm(
    user_input: str,
    knowledge_base_name: str,
    context_window: int = 16385,
    model: str = "gpt-3.5-turbo-1106",
    temperature: float = 0.0,
    document_data: dict[str, bytes] = {},
) -> dict:
    logger.debug(
        "llm.chat",
        user_input=user_input,
        model=model,
        temperature=temperature,
        context_window=context_window,
        files=document_data.keys(),
    )

    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY, temperature=temperature, model=model
    )

    # Get or create the conversation memory for the given conversation ID
    if knowledge_base_name not in conversation_memories:
        conversation_memories[knowledge_base_name] = ConversationBufferMemory(
            memory_key=f"{CHAT_HISTORY}",
            return_messages=True,
            input_key="question",
            output_key="answer",
        )
    memory = conversation_memories[knowledge_base_name]

    # Get or create the conversation prompt for the given conversation ID
    if knowledge_base_name not in conversation_prompts:
        conversation_prompts[knowledge_base_name] = ChatPromptTemplate(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                MessagesPlaceholder(variable_name=f"{CHAT_HISTORY}"),
                HumanMessagePromptTemplate.from_template("{user_input}"),
            ]
        )
    prompt = conversation_prompts[knowledge_base_name]

    if knowledge_base_name and document_data:
        chunked_documents: list[Document] = []
        # Check for the existence of the vectorstore
        if not vectorstore_path_exists(knowledge_base_name):
            documents: list[Document] = load_documents(document_data)
            if documents:
                chunked_documents = get_document_chunks(documents=documents)

        retriever = get_vectorstore_retriever(
            documents=chunked_documents,
            embeddings=OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY),
            knowledge_base_name=knowledge_base_name,
        )

        # Create conversational retrieval chain
        logger.debug("Creating conversational retrieval chain...")
        memory.output_key = "answer"
        conversational_retrieval_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            verbose=False,
            return_source_documents=True,
        )

        llm_response = get_response(
            chain=conversational_retrieval_chain,
            qa={"question": user_input},
            model=model,
            user_input=user_input,
            response_key="answer",
            return_sources=True,
        )
    else:
        # Get a response from the model
        logger.debug("ai.send_request", model=model, user_input=user_input)
        memory.output_key = "text"
        conversation_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True,
            memory=memory,
        )

        llm_response = get_response(
            chain=conversation_chain,
            qa={"user_input": user_input, "question": user_input},
            model=model,
            user_input=user_input,
            response_key="text",
        )

    sources = llm_response.get("sources", [])
    process_sources(sources)  # Process the sources as needed
    return llm_response


def get_response(
    chain: Chain,
    qa: dict[str, str],
    model: str,
    user_input: str,
    response_key: str,
    return_sources: bool = False,
) -> dict:
    ic(chain, model, user_input)
    with get_openai_callback() as cb:
        logger.debug("ai.send_request", model=model)
        llm_response = chain(qa)
        logger.debug(
            "ai.get_response",
            usage=cb,
            model=model,
            # response=llm_response,
        )

    result = {"response": llm_response[response_key]}
    if return_sources and "source_documents" in llm_response:
        result["sources"] = llm_response["source_documents"]
    return result
