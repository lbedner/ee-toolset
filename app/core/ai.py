from langchain.callbacks import get_openai_callback
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.base import Chain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
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
from app.core.loader import load_files
from app.core.log import ic, logger
from app.core.splitter import get_text_splits
from app.core.vectorstore import get_vectorstore_retriever

CHAT_HISTORY = "chat_history"

prompt = ChatPromptTemplate(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        MessagesPlaceholder(variable_name=CHAT_HISTORY),
        HumanMessagePromptTemplate.from_template("{user_input}"),
    ]
)

# Initialize conversation history memory
memory = ConversationBufferMemory(
    memory_key=CHAT_HISTORY,
    return_messages=True,
    input_key="question",
    output_key="answer",
)
loader = WebBaseLoader("https://lilianweng.github.io/posts/2023-06-23-agent/")


def process_sources(sources):
    print("\n\nSources:")
    for source in sources:
        print(
            source.metadata["source"]
            # source
        )  # Adjust based on actual structure of the source


def chat_with_llm(
    user_input: str,
    context_window: int = 16385,
    model: str = "gpt-3.5-turbo-1106",
    temperature: float = 0.0,
    files_dict: dict[str, bytes] = {},
) -> dict:
    logger.debug(
        "llm.chat",
        user_input=user_input,
        model=model,
        temperature=temperature,
        context_window=context_window,
    )
    documents = load_files(files_dict)

    llm = ChatOpenAI(
        api_key=settings.OPENAI_API_KEY, temperature=temperature, model=model
    )
    if documents:
        splits: list[Document] = get_text_splits(documents=documents)
        retriever = get_vectorstore_retriever(
            documents=splits,
            embeddings=OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY),
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
