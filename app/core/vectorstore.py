from os import path

import chromadb
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.vectorstores.chroma import Chroma

from app.core.config import settings
from app.core.log import logger


def format_knowledge_base_name(knowledge_base_name: str) -> str:
    """
    Formats the knowledge base name by replacing spaces with underscores.

    Args:
        knowledge_base_name (str): The name of the knowledge base.

    Returns:
        str: The formatted knowledge base name.
    """
    return knowledge_base_name.replace(" ", "_")


def delete_vectorstore(knowledge_base_name: str) -> None:
    """
    Deletes the vector store directory and its metadata for a given knowledge base name.

    Args:
        knowledge_base_name (str): The name of the knowledge base.

    Raises:
        FileNotFoundError: If the vector store directory does not exist.
    """
    formatted_kb_name = format_knowledge_base_name(knowledge_base_name)
    persist_directory = path.join(settings.VECTORSTORE_CHROMADB_DIR, formatted_kb_name)

    Chroma(
        collection_name=formatted_kb_name,
        embedding_function=OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY),
        persist_directory=persist_directory,
    ).delete_collection()


def create_vectorstore(
    documents: list[Document],
    embeddings: Embeddings,
    knowledge_base_name: str,
    persist_directory_root: str = settings.VECTORSTORE_CHROMADB_DIR,
) -> Chroma:
    """
    Create a vector store using the given documents, embeddings, knowledge base name, and persist directory.

    Args:
        documents (list[Document]): The list of documents to create the vector store from.
        embeddings (Embeddings): The embeddings to use for creating the vector store.
        knowledge_base_name (str): The name of the knowledge base for the vector store.
        persist_directory_root (str, optional): The root directory for persisting the vector store. Defaults to settings.VECTORSTORE_CHROMADB_DIR.

    Returns:
        Chroma: The vector store object.
    """  # noqa
    knowledge_base_name = format_knowledge_base_name(knowledge_base_name)
    persist_directory = path.join(persist_directory_root, knowledge_base_name)
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
        vectorstore.persist()
        logger.debug(
            "vectorstore.chroma.persist.success",
            persist_directory=persist_directory,
            knowledge_base_name=knowledge_base_name,
        )
    return vectorstore


def get_vectorstore(
    knowledge_base_name: str,
    embeddings: Embeddings,
    persist_directory: str,
) -> Chroma:
    """
    Get a vector store for a given knowledge base.

    Args:
        knowledge_base_name (str): The name of the knowledge base.
        embeddings (Embeddings): The embeddings to use for vectorization.
        persist_directory (str): The directory to persist the vector store.

    Returns:
        Chroma: The vector store object.
    """
    logger.debug(
        "vectorstore.chroma.load",
        persist_directory=persist_directory,
        knowledge_base_name=knowledge_base_name,
    )
    return Chroma(
        collection_name=knowledge_base_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )


def vectorstore_exists(knowledge_base_name: str) -> bool:
    """
    Check if the vector store for a given knowledge base exists.

    Args:
        knowledge_base_name (str): The name of the knowledge base.

    Returns:
        bool: True if the vector store exists, False otherwise.
    """
    formatted_kb_name = format_knowledge_base_name(knowledge_base_name)
    persist_directory = path.join(settings.VECTORSTORE_CHROMADB_DIR, formatted_kb_name)

    vectorstore_exists = False
    try:
        chromadb.PersistentClient(path=persist_directory).get_collection(
            name=formatted_kb_name
        )
        vectorstore_exists = True
    except ValueError:
        pass

    logger.debug(
        "vectorstore.chroma.exists",
        persist_directory=persist_directory,
        knowledge_base_name=knowledge_base_name,
        vectorstore_exists=vectorstore_exists,
    )
    return vectorstore_exists


def get_vectorstore_retriever(
    documents: list[Document],
    embeddings: Embeddings,
    knowledge_base_name: str,
    max_documents: int = 10,
    persist_directory_root: str = settings.VECTORSTORE_CHROMADB_DIR,
) -> VectorStoreRetriever:
    """
    Retrieves a VectorStoreRetriever object for a given set of documents and embeddings.

    Args:
        documents (list[Document]): The list of documents to be used for creating the vector store.
        embeddings (Embeddings): The embeddings to be used for creating the vector store.
        knowledge_base_name (str, optional): The name of the knowledge base. Defaults to "illiana".
        max_documents (int, optional): The maximum number of documents to retrieve. Defaults to 5.
        persist_directory_root (str, optional): The root directory for persisting the vector store. Defaults to settings.VECTORSTORE_CHROMADB_DIR.

    Returns:
        VectorStoreRetriever: The VectorStoreRetriever object.

    """  # noqa
    # ChromaDB does not support spaces in the knowledge base name
    knowledge_base_name = format_knowledge_base_name(knowledge_base_name)
    persist_directory = path.join(persist_directory_root, knowledge_base_name)
    vectorstore: Chroma = None
    if not documents:
        vectorstore = get_vectorstore(
            knowledge_base_name=knowledge_base_name,
            embeddings=embeddings,
            persist_directory=persist_directory,
        )
    else:
        vectorstore = create_vectorstore(
            documents=documents,
            embeddings=embeddings,
            knowledge_base_name=knowledge_base_name,
            persist_directory_root=persist_directory_root,
        )

    return vectorstore.as_retriever(search_kwargs={"k": max_documents})
