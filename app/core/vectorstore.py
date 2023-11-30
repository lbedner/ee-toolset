from os import path

from langchain.schema import Document
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.vectorstores.chroma import Chroma

from app.core.config import settings
from app.core.log import logger


def get_vectorstore_retriever(
    documents: list[Document],
    embeddings: Embeddings,
    collection_name: str = "illiana",
    max_documents: int = 5,
    persist_directory_root: str = settings.VECTORSTORE_CHROMADB_DIR,
) -> VectorStoreRetriever:
    persist_directory = path.join(persist_directory_root, collection_name)
    if persist_directory and path.exists(persist_directory):
        logger.debug("Loading existing ChromaDB from disk...")
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_directory,
        )
    else:
        logger.debug("Creating new ChromaDB instance...")
        vectorstore = Chroma.from_documents(
            collection_name=collection_name,
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_directory,
        )
        if persist_directory:
            logger.debug("Persisting ChromaDB to disk...")
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
