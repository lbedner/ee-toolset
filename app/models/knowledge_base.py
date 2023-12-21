import json
import os
import shutil

from pydantic import BaseModel, RootModel, StrictBool, StrictInt, StrictStr

from app.core.config import settings
from app.core.log import logger
from app.core.vectorstore import delete_vectorstore


class KnowledgeBaseDocument(BaseModel):
    Type: StrictStr
    Filepath: StrictStr
    Size: StrictInt
    Loaded: StrictBool


class KnowledgeBase(RootModel):
    """
    Represents a knowledge base containing documents organized by knowledge base names.

    Attributes:
        root (dict): A dictionary representing the root of the knowledge base, where the keys are knowledge base names
                     and the values are dictionaries containing document names as keys and KnowledgeBaseDocument objects as values.
    """  # noqa

    root: dict[str, dict[str, KnowledgeBaseDocument]]

    @classmethod
    def load(cls, file_path: str = settings.KNOWLEDGE_BASE_FILEPATH) -> "KnowledgeBase":
        """
        Load a knowledge base from a file.

        Args:
            file_path (str): The file path of the knowledge base file. Defaults to the value specified in the settings.

        Returns:
            KnowledgeBase: The loaded knowledge base object.
        """  # noqa
        with open(file_path, "r") as f:
            data = json.load(f)
            return cls.model_validate(data)

    def dump(self, file_path: str = settings.KNOWLEDGE_BASE_FILEPATH) -> None:
        """
        Dump the knowledge base to a file.

        Args:
            file_path (str): The file path to dump the knowledge base. Defaults to the value specified in the settings.
        """  # noqa
        with open(file_path, "w") as f:
            json.dump(self.model_dump(), f, indent=4)

    def add(
        self,
        knowledge_base_name: str,
        document_name: str,
        document: KnowledgeBaseDocument,
    ):
        """
        Add a document to the knowledge base.

        Args:
            knowledge_base_name (str): The name of the knowledge base.
            document_name (str): The name of the document.
            document (KnowledgeBaseDocument): The document to add.
        """
        if knowledge_base_name not in self.root:
            self.root[knowledge_base_name] = {}
        self.root[knowledge_base_name][document_name] = document
        self.dump()

    def update(
        self,
        knowledge_base_name: str,
        document_name: str,
        document: KnowledgeBaseDocument,
    ):
        """
        Update a document in the knowledge base.

        Args:
            knowledge_base_name (str): The name of the knowledge base.
            document_name (str): The name of the document.
            document (KnowledgeBaseDocument): The updated document.

        Raises:
            KeyError: If no document is found with the specified document name.
        """
        if document_name in self.root[knowledge_base_name]:
            self.root[knowledge_base_name][document_name] = document
            self.dump()
        else:
            raise KeyError(f"No attribute found with key: {document_name}")

    def remove(self, knowledge_base_name: str, document_name: str):
        """
        Remove a document from the knowledge base.

        Args:
            knowledge_base_name (str): The name of the knowledge base.
            document_name (str): The name of the document.
        """
        if knowledge_base_name in self.root:
            self.root[knowledge_base_name].pop(document_name)
            self.dump()


class KnowledgeBaseHelper:
    """
    Helper class for managing knowledge base operations.

    Args:
        knowledge_base (KnowledgeBase): The knowledge base object.

    Attributes:
        knowledge_base (KnowledgeBase): The knowledge base object.
        document_data (dict[str, dict[str, bytes]]): A dictionary containing the loaded document data.

    Methods:
        _load_document_data(): Loads the document data from the knowledge base.
        add_new_knowledge_base(knowledge_base_name: str): Adds a new knowledge base.
        add_document(knowledge_base_name: str, document_name: str, incoming_filename: str, outgoing_filename: str): Adds a document to the knowledge base.
        delete_document(knowledge_base_name: str, document_name: str): Deletes a document from the knowledge base.
        _delete_document_from_disk(filepath: str): Deletes a document file from disk.
    """  # noqa

    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base
        self.document_data: dict[str, dict[str, bytes]] = self._load_document_data()

    def _load_document_data(self) -> dict[str, dict[str, bytes]]:
        """
        Loads the document data from the knowledge base.

        Returns:
            dict[str, dict[str, bytes]]: A dictionary containing the loaded document data.
        """
        document_data: dict[str, dict[str, bytes]] = {}
        for knowledge_base_name, documents in self.knowledge_base.root.items():
            document_data[knowledge_base_name] = {}
            for document_name, document in documents.items():
                try:
                    with open(document.Filepath, "rb") as file:
                        document_data[knowledge_base_name][document_name] = file.read()
                except Exception as e:
                    logger.error(f"Error loading document '{document_name}': {str(e)}")
        return document_data

    def get_document_data(self, knowledge_base_name: str) -> dict[str, bytes]:
        """
        Retrieves the document data for a given knowledge base.

        Args:
            knowledge_base_name (str): The name of the knowledge base.

        Returns:
            dict[str, bytes]: The document data.
        """
        return self.document_data[knowledge_base_name]

    def add_new_knowledge_base(self, knowledge_base_name: str) -> None:
        """
        Adds a new knowledge base.

        Args:
            knowledge_base_name (str): The name of the knowledge base.

        Returns:
            None
        """
        if knowledge_base_name not in self.knowledge_base.root:
            self.knowledge_base.root[knowledge_base_name] = {}
            self.knowledge_base.dump()

    def add_document(
        self,
        knowledge_base_name: str,
        document_name: str,
        incoming_filename: str,
        outgoing_filename: str,
    ):
        """
        Adds a document to the knowledge base.

        Args:
            knowledge_base_name (str): The name of the knowledge base.
            document_name (str): The name of the document.
            incoming_filename (str): The path to the incoming file.
            outgoing_filename (str): The path to the outgoing file.

        Returns:
            None
        """
        try:
            os.makedirs(os.path.dirname(outgoing_filename), exist_ok=True)
            with open(incoming_filename, "rb") as incoming_file:
                with open(outgoing_filename, "wb") as outgoing_file:
                    file_bytes: bytes = incoming_file.read()
                    outgoing_file.write(file_bytes)
                    document = KnowledgeBaseDocument(
                        Type="Document",
                        Filepath=outgoing_filename,
                        Size=len(file_bytes),
                        Loaded=False,
                    )
                    self.knowledge_base.add(
                        knowledge_base_name, document_name, document
                    )
                    if knowledge_base_name not in self.document_data:
                        self.document_data[knowledge_base_name] = {}
                    self.document_data[knowledge_base_name][document_name] = file_bytes
                    logger.debug(
                        "knowledge.add_document.success",
                        knowledge_base_name=knowledge_base_name,
                        document_name=document_name,
                        document=document,
                    )
        except FileNotFoundError as e:
            logger.error(
                "knowledge.add_document.failure",
                file_path=outgoing_filename,
                document_name=document_name,
                exception=e,
            )
        except IOError as e:
            logger.error(
                "knowledge.add_document.failure",
                file_path=outgoing_filename,
                exception=e,
                document_name=document_name,
            )

    def delete_document(self, knowledge_base_name: str, document_name: str) -> None:
        """
        Deletes a document from the knowledge base.

        Args:
            knowledge_base_name (str): The name of the knowledge base.
            document_name (str): The name of the document.

        Returns:
            None
        """
        if document_name in self.knowledge_base.root[knowledge_base_name]:
            document = self.knowledge_base.root[knowledge_base_name][document_name]
            self._delete_document_from_disk(document.Filepath)
            self.knowledge_base.remove(knowledge_base_name, document_name)
            self.document_data[knowledge_base_name].pop(document_name, None)
        else:
            logger.warning(
                "knowledge.delete_document.no_file",
                document_name=document_name,
                knowledge_base_name=knowledge_base_name,
            )

    def get_knowledge_base(
        self, knowledge_base_name: str
    ) -> dict[str, KnowledgeBaseDocument]:
        """
        Retrieves a specific knowledge base by its name.

        Args:
            knowledge_base_name (str): The name of the knowledge base to retrieve.

        Returns:
            dict[str, KnowledgeBaseDocument]: The documents within the specified knowledge base.

        Raises:
            KeyError: If the knowledge base does not exist.
        """  # noqa
        if knowledge_base_name in self.knowledge_base.root:
            return self.knowledge_base.root[knowledge_base_name]
        else:
            raise KeyError(f"Knowledge base '{knowledge_base_name}' does not exist")

    def _delete_document_from_disk(self, filepath: str) -> None:
        """
        Deletes a document file from disk.

        Args:
            filepath (str): The path to the document file.

        Returns:
            None
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug("knowledge.delete_file.success", document=filepath)
            else:
                logger.warning("knowledge.delete_file.no_file", document=filepath)
        except (PermissionError, OSError) as e:
            logger.error("knowledge.exception", document=filepath, exception=e)

    def delete_knowledge_base(self, knowledge_base_name: str) -> None:
        """
        Deletes an entire knowledge base given its name.

        Args:
            knowledge_base_name (str): The name of the knowledge base to delete.

        Raises:
            KeyError: If the knowledge base does not exist.
        """
        if knowledge_base_name in self.knowledge_base.root:
            document_names = list(self.knowledge_base.root[knowledge_base_name].keys())
            for document_name in document_names:
                self.delete_document(knowledge_base_name, document_name)

            # Remove the knowledge base from the root
            del self.knowledge_base.root[knowledge_base_name]

            # Update the stored file
            self.knowledge_base.dump()

            # Remove the knowledge base from the document data
            self.document_data.pop(knowledge_base_name, None)

            # Determine the root directory for the documents
            document_root_directory = os.path.join(
                settings.VECTORSTORE_KNOWLEDGE_BASE_DIR,
                knowledge_base_name,
            )

            # Remove the root directory of the documents
            if os.path.exists(document_root_directory):
                shutil.rmtree(document_root_directory)

            # Remove the vector store from disk
            delete_vectorstore(knowledge_base_name)

            logger.debug(
                "knowledge_base.delete.success", knowledge_base_name=knowledge_base_name
            )
        else:
            raise KeyError(f"Knowledge base '{knowledge_base_name}' does not exist")

    def refesh(self, knowledge_base_name: str) -> None:
        """
        Refreshes the knowledge base.

        Args:
            knowledge_base_name (str): The name of the knowledge base to refresh.

        Returns:
            None
        """
        if knowledge_base_name in self.knowledge_base.root:
            documents = self.knowledge_base.root[knowledge_base_name]
            for document in documents.values():
                document.Loaded = True
        self.knowledge_base.dump()

    def get_documents(
        self, knowledge_base_name: str
    ) -> dict[str, KnowledgeBaseDocument]:
        """
        Retrieves the documents within a knowledge base.

        Args:
            knowledge_base_name (str): The name of the knowledge base.

        Returns:
            dict[str, KnowledgeBaseDocument]: The documents within the specified knowledge base.
        """  # noqa
        return self.knowledge_base.root[knowledge_base_name]
