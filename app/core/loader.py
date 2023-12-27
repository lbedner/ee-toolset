import os
import tempfile

from langchain.document_loaders import (
    PDFPlumberLoader,
    TextLoader,
    UnstructuredHTMLLoader,
    UnstructuredRTFLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.document_loaders.base import BaseLoader
from langchain.schema import Document

from app.core.log import logger


def load_file_from_bytes(
    file_bytes, loader_class: BaseLoader, file_suffix: str, filename: str
) -> list[Document]:
    with tempfile.NamedTemporaryFile(
        suffix=file_suffix, delete=False, prefix=filename
    ) as temp_file:
        temp_file.write(file_bytes)
        loader: BaseLoader = loader_class(temp_file.name)
        loaded_data = loader.load()

        # Since we're loading from a temp file,
        # we want to make sure we have the original filename
        loaded_data[0].metadata["source"] = filename
        loaded_data[0].metadata["size"] = len(file_bytes)
        return loaded_data


def determine_loader_and_load(file_name, file_bytes):
    ext = os.path.splitext(file_name)[1].lower()
    if ext == ".pdf":
        return load_file_from_bytes(file_bytes, PDFPlumberLoader, ext, file_name)
    elif ext in [".html", ".htm"]:
        return load_file_from_bytes(file_bytes, UnstructuredHTMLLoader, ext, file_name)
    elif ext == ".rtf":
        return load_file_from_bytes(file_bytes, UnstructuredRTFLoader, ext, file_name)
    elif ext in [".txt", ".text"]:
        return load_file_from_bytes(file_bytes, TextLoader, ext, file_name)
    elif ext in [".doc", ".docx"]:
        return load_file_from_bytes(
            file_bytes, UnstructuredWordDocumentLoader, ext, file_name
        )
    else:
        logger.error(f"Unsupported file type: {file_name}")
        return []


def load_documents(document_data: dict[str, bytes]) -> list[Document]:
    documents: list[Document] = []
    for file_name, file_bytes in document_data.items():
        logger.debug("loader.load_documents", file_name=file_name)
        documents.extend(determine_loader_and_load(file_name, file_bytes))
    return documents
