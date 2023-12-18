import os
import tempfile

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
