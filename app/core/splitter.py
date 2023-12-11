from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.log import logger

AVE_TOKEN_LENGTH = 5


def get_document_chunks(
    documents: list[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    context_window: int = 16385,
) -> list[Document]:
    # Estimate max characters per chunk considering the token limit
    max_characters = context_window * AVE_TOKEN_LENGTH

    logger.debug("Estimated max characters per chunk", max_characters=max_characters)

    # Set chunk size and overlap
    chunk_size = int(max_characters * 0.10)  # % of max character limit
    chunk_overlap = int(chunk_size * 0.10)  # % of chunk size for overlap

    logger.debug(
        "Splitting documents...",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    splits = text_splitter.split_documents(documents)
    logger.debug("Split documents successfully", count=len(splits))
    return splits
