import os

from app.models import KnowledgeBase, KnowledgeBaseDocument


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

    # Assert that the knowledge base has specific documents
    assert "doc1" in kb.root
    assert "doc2" in kb.root

    # Assert details of the documents
    assert kb.root["doc1"].Type == "Document"
    assert kb.root["doc1"].Filepath == "/path/to/doc1"
    assert kb.root["doc1"].Size == 1024
    assert kb.root["doc1"].Loaded is True

    assert kb.root["doc2"].Type == "Report"
    assert kb.root["doc2"].Filepath == "/path/to/doc2"
    assert kb.root["doc2"].Size == 2048
    assert kb.root["doc2"].Loaded is False


def test_knowledge_base_add():
    # Test adding a document to the knowledge base
    kb = KnowledgeBase(root={})
    doc = KnowledgeBaseDocument(
        Type="Document", Filepath="/new/doc", Size=2048, Loaded=False
    )
    kb.add("new_doc", doc)
    assert "new_doc" in kb.root
    assert kb.root["new_doc"].Filepath == "/new/doc"


def test_knowledge_base_update():
    # Initialize a knowledge base and add a document
    kb = KnowledgeBase(root={})
    doc = KnowledgeBaseDocument(
        Type="Document", Filepath="/path/to/doc", Size=1024, Loaded=True
    )
    kb.add("doc1", doc)

    # Update the document
    updated_doc = KnowledgeBaseDocument(
        Type="Document", Filepath="/new/path/doc", Size=2048, Loaded=False
    )
    kb.update("doc1", updated_doc)

    # Assert that the document was updated
    assert kb.root["doc1"].Filepath == "/new/path/doc"
    assert kb.root["doc1"].Size == 2048
    assert kb.root["doc1"].Loaded is False


def test_knowledge_base_remove():
    # Initialize a knowledge base and add a document
    kb = KnowledgeBase(root={})
    doc = KnowledgeBaseDocument(
        Type="Document", Filepath="/path/to/doc", Size=1024, Loaded=True
    )
    kb.add("doc1", doc)

    # Remove the document
    kb.remove("doc1")

    # Assert that the document was removed
    assert "doc1" not in kb.root
