import os
import tempfile

import pytest

from app.models import KnowledgeBase, KnowledgeBaseDocument, KnowledgeBaseHelper


def test_knowledge_base_document_creation():
    # Test creating a KnowledgeBaseDocument
    doc = KnowledgeBaseDocument(
        Type="Document", Filepath="/path/to/doc", Size=1024, Loaded=True
    )
    assert doc.Type == "Document"
    assert doc.Filepath == "/path/to/doc"
    assert doc.Size == 1024
    assert doc.Loaded is True


def test_knowledge_base_load():
    # Load the knowledge base from the test file
    kb = KnowledgeBase.load(
        os.path.join(
            os.path.dirname(__file__),
            "data",
            "knowledge_base.json",
        )
    )

    kb_1 = kb.root["kb1"]

    # Assert that the knowledge base has specific documents
    assert "doc1" in kb_1
    assert "doc2" in kb_1

    # Assert details of the documents
    assert kb_1["doc1"].Type == "Document"
    assert kb_1["doc1"].Filepath == "/path/to/doc1"
    assert kb_1["doc1"].Size == 1024
    assert kb_1["doc1"].Loaded is True

    assert kb_1["doc2"].Type == "Report"
    assert kb_1["doc2"].Filepath == "/path/to/doc2"
    assert kb_1["doc2"].Size == 2048
    assert kb_1["doc2"].Loaded is False

    kb_2 = kb.root["kb2"]

    # Assert that the knowledge base has specific documents
    assert "doc3" in kb_2
    assert "doc4" in kb_2

    # Assert details of the documents
    assert kb_2["doc3"].Type == "Document"
    assert kb_2["doc3"].Filepath == "/path/to/doc3"
    assert kb_2["doc3"].Size == 1024
    assert kb_2["doc3"].Loaded is True

    assert kb_2["doc4"].Type == "Report"
    assert kb_2["doc4"].Filepath == "/path/to/doc4"
    assert kb_2["doc4"].Size == 2048
    assert kb_2["doc4"].Loaded is False


def test_knowledge_base_add():
    # Test adding a document to the knowledge base
    kb = KnowledgeBase(root={})
    doc = KnowledgeBaseDocument(
        Type="Document", Filepath="/new/doc", Size=2048, Loaded=False
    )
    kb.add("kb1", "new_doc", doc)
    assert "new_doc" in kb.root["kb1"]
    assert kb.root["kb1"]["new_doc"].Filepath == "/new/doc"


def test_knowledge_base_update():
    # Initialize a knowledge base and add a document
    kb = KnowledgeBase(root={})
    doc = KnowledgeBaseDocument(
        Type="Document", Filepath="/path/to/doc", Size=1024, Loaded=True
    )
    kb.add("kb1", "doc1", doc)

    # Update the document
    updated_doc = KnowledgeBaseDocument(
        Type="Document", Filepath="/new/path/doc", Size=2048, Loaded=False
    )
    kb.update("kb1", "doc1", updated_doc)

    # Assert that the document was updated
    assert kb.root["kb1"]["doc1"].Filepath == "/new/path/doc"
    assert kb.root["kb1"]["doc1"].Size == 2048
    assert kb.root["kb1"]["doc1"].Loaded is False


def test_knowledge_base_remove():
    # Initialize a knowledge base and add a document
    kb = KnowledgeBase(root={})
    doc = KnowledgeBaseDocument(
        Type="Document", Filepath="/path/to/doc", Size=1024, Loaded=True
    )
    kb.add("kb1", "doc1", doc)

    # Remove the document
    kb.remove("kb1", "doc1")

    # Assert that the document was removed
    assert "doc1" not in kb.root["kb1"]


def test_knowledge_base_helper_add_document():
    kb = KnowledgeBase(root={})
    kb_helper = KnowledgeBaseHelper(kb)

    with tempfile.NamedTemporaryFile(delete=False) as temp_incoming_file:
        temp_incoming_file_name = temp_incoming_file.name
        temp_incoming_file.write(b"Test content")

    # Create a temporary file with content
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_outgoing_file:
        temp_outgoing_file_name = temp_outgoing_file.name

    # Add the document to the knowledge base using helper
    kb_helper.add_document(
        "kb1",
        "temp_doc",
        incoming_filename=temp_incoming_file_name,
        outgoing_filename=temp_outgoing_file_name,
    )

    # Assert that the document was added and data is loaded
    assert "temp_doc" in kb.root["kb1"]
    assert kb.root["kb1"]["temp_doc"].Filepath == temp_outgoing_file_name
    assert kb.root["kb1"]["temp_doc"].Size == len("Test content")
    assert kb.root["kb1"]["temp_doc"].Loaded is False
    assert kb_helper.document_data["kb1"]["temp_doc"] == b"Test content"

    # Clean up
    os.remove(temp_incoming_file_name)
    os.remove(temp_outgoing_file_name)


def test_knowledge_base_helper_delete_document():
    kb = KnowledgeBase(root={})
    kb_helper = KnowledgeBaseHelper(kb)

    with tempfile.NamedTemporaryFile(delete=False) as temp_incoming_file:
        temp_incoming_file_name = temp_incoming_file.name
        temp_incoming_file.write(b"Test content")

    # Create a temporary file with content
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_outgoing_file:
        temp_outgoing_file_name = temp_outgoing_file.name

    # Add the document to the knowledge base using helper
    kb_helper.add_document(
        "kb1",
        "temp_doc",
        incoming_filename=temp_incoming_file_name,
        outgoing_filename=temp_outgoing_file_name,
    )

    # Ensure the document is in the knowledge base
    assert "temp_doc" in kb.root["kb1"]

    # Delete the document using helper
    kb_helper.delete_document("kb1", "temp_doc")

    # Assert that the document was removed from the knowledge base and document_data
    assert "temp_doc" not in kb.root["kb1"]
    assert "temp_doc" not in kb_helper.document_data["kb1"]

    # Ensure the file is deleted from disk
    os.remove(temp_incoming_file_name)


def test_knowledge_base_helper_get_knowledge_base():
    # Initialize a knowledge base with some documents
    kb = KnowledgeBase(
        root={
            "kb1": {
                "doc1": KnowledgeBaseDocument(
                    Type="Document", Filepath="/path/to/doc1", Size=1024, Loaded=True
                ),
                "doc2": KnowledgeBaseDocument(
                    Type="Report", Filepath="/path/to/doc2", Size=2048, Loaded=False
                ),
            }
        }
    )
    kb_helper = KnowledgeBaseHelper(kb)

    # Test retrieving an existing knowledge base
    retrieved_kb = kb_helper.get_knowledge_base("kb1")
    assert "doc1" in retrieved_kb
    assert "doc2" in retrieved_kb
    assert retrieved_kb["doc1"].Type == "Document"
    assert retrieved_kb["doc2"].Type == "Report"

    # Test retrieving a non-existent knowledge base
    with pytest.raises(KeyError):
        kb_helper.get_knowledge_base("non_existent_kb")


def test_knowledge_base_helper_delete_knowledge_base():
    # Initialize a knowledge base
    kb = KnowledgeBase(
        root={
            "kb1": {
                "doc1": KnowledgeBaseDocument(
                    Type="Document", Filepath="/path/to/doc1", Size=1024, Loaded=True
                ),
                "doc2": KnowledgeBaseDocument(
                    Type="Report", Filepath="/path/to/doc2", Size=2048, Loaded=False
                ),
            }
        }
    )
    kb_helper = KnowledgeBaseHelper(kb)

    # Delete the knowledge base
    kb_helper.delete_knowledge_base("kb1")

    # Assert that the knowledge base is removed
    assert "kb1" not in kb_helper.knowledge_base.root

    # Optionally, assert that the documents are removed from the document_data
    # This depends on whether your delete_document method
    # also removes the data from document_data
    assert "kb1" not in kb_helper.document_data


@pytest.mark.skip(reason="Skipping this until I can sort out the file paths")
def test_knowledge_base_helper_get_document_data():
    # Initialize a knowledge base
    kb = KnowledgeBase(root={})
    kb_helper = KnowledgeBaseHelper(kb)

    # Create temporary files and add them to the knowledge base
    document_data = {}
    for i in range(2):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_name = temp_file.name
            content = f"Test content {i}".encode()
            temp_file.write(content)

            # Add document to the knowledge base
            doc_name = f"doc{i}"
            kb_helper.add_document(
                "kb1",
                doc_name,
                incoming_filename=temp_file_name,
                outgoing_filename=temp_file_name,
            )
            document_data[doc_name] = content

    # Retrieve the document data using get_document_data
    retrieved_data = kb_helper.get_document_data("kb1")

    # Assert that the retrieved data matches the added data
    assert len(retrieved_data) == len(document_data)
    for doc_name, content in document_data.items():
        assert doc_name in retrieved_data
        assert retrieved_data[doc_name] == content

    # Clean up
    for temp_file_name in [
        doc.Filepath for doc in kb_helper.knowledge_base.root["kb1"].values()
    ]:
        os.remove(temp_file_name)


def test_knowledge_base_helper_get_knowledge_base_names():
    # Initialize a knowledge base with some named knowledge bases
    kb = KnowledgeBase(
        root={
            "kb1": {
                "doc1": KnowledgeBaseDocument(
                    Type="Document", Filepath="/path/to/doc1", Size=1024, Loaded=True
                )
            },
            "kb2": {
                "doc2": KnowledgeBaseDocument(
                    Type="Document", Filepath="/path/to/doc2", Size=2048, Loaded=False
                )
            },
        }
    )
    kb_helper = KnowledgeBaseHelper(kb)

    # Retrieve the knowledge base names using get_knowledge_base_names
    kb_names = kb_helper.get_knowledge_base_names()

    # Assert that the retrieved knowledge base names are correct
    assert set(kb_names) == {"kb1", "kb2"}

    # Optionally, test with an empty knowledge base
    kb_empty = KnowledgeBase(root={})
    kb_helper_empty = KnowledgeBaseHelper(kb_empty)
    kb_names_empty = kb_helper_empty.get_knowledge_base_names()
    assert kb_names_empty == []
