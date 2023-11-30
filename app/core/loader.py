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

from app.core.log import logger


def load_file_from_bytes(file_bytes, loader_class: BaseLoader, file_suffix: str):
    with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name
        loader: BaseLoader = loader_class(temp_file_path)
        loaded_data = loader.load()
        return loaded_data


def determine_loader_and_load(file_name, file_bytes):
    ext = os.path.splitext(file_name)[1].lower()
    if ext == ".pdf":
        return load_file_from_bytes(file_bytes, PDFPlumberLoader, ext)
    elif ext in [".html", ".htm"]:
        return load_file_from_bytes(file_bytes, UnstructuredHTMLLoader, ext)
    elif ext == ".rtf":
        return load_file_from_bytes(file_bytes, UnstructuredRTFLoader, ext)
    elif ext in [".txt", ".text"]:
        return load_file_from_bytes(file_bytes, TextLoader, ext)
    elif ext in [".doc", ".docx"]:
        return load_file_from_bytes(file_bytes, UnstructuredWordDocumentLoader, ext)
    else:
        logger.debug(f"Unsupported file type: {file_name}")
        return []


def load_files(files_dict: dict[str, bytes]) -> list:
    documents = []
    for file_name, file_bytes in files_dict.items():
        logger.debug(f"Loading file[{file_name}]...")
        documents.extend(determine_loader_and_load(file_name, file_bytes))
    return documents

    # logger.debug("Loading GitHub repo...")
    # documents = GitLoader(
    #     branch="illiana",
    #     # repo_path="/Users/James/Workspace/Ingestion/music-cat",
    #     repo_path="/Users/James/Workspace/Poc/ee-toolset",
    #     file_filter=lambda file_path: file_path.endswith(".py"),
    # ).load()
