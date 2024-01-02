from typing import Optional, Tuple

from langchain.callbacks import get_openai_callback
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
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
from app.core.vectorstore import (
    create_vectorstore,
    delete_vectorstore,
    get_vectorstore_retriever,
    vectorstore_exists,
)
from app.models import KnowledgeBaseDocument

CHAT_HISTORY = "chat_history"


conversation_memories: dict[str, ConversationBufferMemory] = {}
conversation_prompts: dict[str, ChatPromptTemplate] = {}


def process_sources(sources: list):
    logger.info("\n\nSources:")
    for source in sources:
        logger.info(source.metadata["source"])


def _get_memory(knowledge_base_name: str) -> ConversationBufferMemory:
    # Get or create the conversation memory for the given conversation ID
    if knowledge_base_name not in conversation_memories:
        conversation_memories[knowledge_base_name] = ConversationBufferMemory(
            memory_key=f"{CHAT_HISTORY}",
            return_messages=True,
            input_key="question",
            output_key="answer",
        )
    memory = conversation_memories[knowledge_base_name]
    return memory


def _get_prompt(knowledge_base_name: str) -> ChatPromptTemplate:
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
    return prompt


def stream_chat_with_llm(
    user_input: str,
    knowledge_base_name: str,
    context_window: int = 16385,
    model: str = "gpt-3.5-turbo-1106",
    temperature: float = 0.0,
    knowledge_base_documents: dict[str, KnowledgeBaseDocument] = {},
    use_knowledge_base: bool = False,
    streaming_callback_handler: Optional[BaseCallbackHandler] = None,
) -> Tuple[dict, bool]:
    logger.debug(
        "llm.chat",
        user_input=user_input,
        model=model,
        temperature=temperature,
        context_window=context_window,
        files=knowledge_base_documents.keys(),
        use_knowledge_base=use_knowledge_base,
        streaming_callback_handler=streaming_callback_handler,
    )

    llm = create_llm(model, temperature, streaming_callback_handler)
    memory, prompt = get_conversation_components(knowledge_base_name)
    chain, response_key, refreshed_vectorstore = configure_chain(
        llm,
        memory,
        prompt,
        use_knowledge_base,
        knowledge_base_name,
        knowledge_base_documents,
    )

    logger.debug("ai.send_request", model=model, user_input=user_input)
    llm_response = get_response(
        chain=chain,
        qa={"question": user_input}
        if use_knowledge_base
        else {"user_input": user_input, "question": user_input},
        model=model,
        user_input=user_input,
        response_key=response_key,
        return_sources=True if use_knowledge_base else False,
    )

    sources = llm_response.get("sources", [])
    process_sources(sources)
    return llm_response, refreshed_vectorstore


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
        )

    result = {"response": llm_response[response_key]}
    if return_sources and "source_documents" in llm_response:
        result["sources"] = llm_response["source_documents"]
    return result


def refresh_vectorstore(
    knowledge_base_documents: dict[str, KnowledgeBaseDocument], knowledge_base_name: str
) -> None:
    """
    Recreates the ChromaDB vector store for a given knowledge base.

    Args:
        document_data (dict[str, bytes]): A dictionary containing document data, where the keys are document filenames
            and the values are the document contents in bytes.
        knowledge_base_name (str): The name of the knowledge base.
    """  # noqa
    delete_vectorstore(knowledge_base_name)
    create_vectorstore(
        documents=get_document_chunks(load_documents(knowledge_base_documents)),
        embeddings=OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY),
        knowledge_base_name=knowledge_base_name,
    )


def create_llm(
    model, temperature: float, streaming_callback_handler: Optional[BaseCallbackHandler]
):
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        temperature=temperature,
        model=model,
        streaming=True if streaming_callback_handler else False,
        verbose=True if streaming_callback_handler else False,
        callback_manager=(
            CallbackManager([streaming_callback_handler])
            if streaming_callback_handler
            else None
        ),
    )


def get_conversation_components(knowledge_base_name: str):
    memory: ConversationBufferMemory = _get_memory(knowledge_base_name)
    prompt: ChatPromptTemplate = _get_prompt(knowledge_base_name)
    return memory, prompt


def configure_chain(
    llm,
    memory: ConversationBufferMemory,
    prompt: ChatPromptTemplate,
    use_knowledge_base: bool,
    knowledge_base_name: str,
    knowledge_base_documents: dict[str, KnowledgeBaseDocument],
):
    refreshed_vectorstore = False
    if use_knowledge_base and knowledge_base_name and knowledge_base_documents:
        chunked_documents, refreshed_vectorstore = prepare_documents(
            knowledge_base_name, knowledge_base_documents
        )
        retriever = get_vectorstore_retriever(
            documents=chunked_documents,
            embeddings=OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY),
            knowledge_base_name=knowledge_base_name,
        )
        memory.output_key = "answer"
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
        )
        response_key = "answer"
    else:
        memory.output_key = "text"
        chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
        response_key = "text"
    return chain, response_key, refreshed_vectorstore


def prepare_documents(
    knowledge_base_name: str, knowledge_base_documents: dict[str, KnowledgeBaseDocument]
) -> Tuple[list[Document], bool]:
    refreshed_vectorstore = False
    chunked_documents: list[Document] = []
    if not vectorstore_exists(knowledge_base_name):
        documents = load_documents(knowledge_base_documents)
        if documents:
            chunked_documents = get_document_chunks(documents=documents)
            refreshed_vectorstore = True
    return chunked_documents, refreshed_vectorstore
