from os import path

from langchain.schema import Document
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.vectorstores.chroma import Chroma

from app.core.config import settings
from app.core.log import logger


def format_knowledge_base_name(knowledge_base_name: str) -> str:
    return knowledge_base_name.replace(" ", "_")


def vectorstore_path_exists(knowledge_base_name: str) -> bool:
    persist_directory = path.join(
        settings.VECTORSTORE_CHROMADB_DIR,
        format_knowledge_base_name(knowledge_base_name),
    )
    logger.debug(
        "vectorstore.chroma.path_exists",
        persist_directory=persist_directory,
        knowledge_base_name=knowledge_base_name,
    )
    return path.exists(persist_directory)


def get_vectorstore_retriever(
    documents: list[Document],
    embeddings: Embeddings,
    knowledge_base_name: str = "illiana",
    max_documents: int = 5,
    persist_directory_root: str = settings.VECTORSTORE_CHROMADB_DIR,
) -> VectorStoreRetriever:
    # ChromaDB does not support spaces in the knowledge base name
    knowledge_base_name = format_knowledge_base_name(knowledge_base_name)
    persist_directory = path.join(persist_directory_root, knowledge_base_name)
    if persist_directory and path.exists(persist_directory):
        logger.debug(
            "vectorstore.chroma.load",
            persist_directory=persist_directory,
            knowledge_base_name=knowledge_base_name,
        )
        vectorstore = Chroma(
            collection_name=knowledge_base_name,
            embedding_function=embeddings,
            persist_directory=persist_directory,
        )
    else:
        logger.debug(
            "vectorstore.chroma.create",
            persist_directory=persist_directory,
            knowledge_base_name=knowledge_base_name,
            embeddings=embeddings,
        )
        vectorstore = Chroma.from_documents(
            collection_name=knowledge_base_name,
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_directory,
        )
        if persist_directory:
            logger.debug("vectorstore.chroma.persist")
            vectorstore.persist()

    return vectorstore.as_retriever(search_kwargs={"k": max_documents})


# Search for similar documents
# logger.debug("Searching for similar documents...")
# vector_docs = vectorstore.similarity_search_with_score(
#    query=user_input, k=NUM_RETRIEVED_DOCUMENTS
# )
# ic(vector_docs)
# filtered_docs = [doc for doc in vector_docs if doc[1] > SIMILARITY_THRESHOLD]
# ic(filtered_docs)
