from src.vector_store import ChromaVectorStore


def test_chroma_vector_store_add_and_query() -> None:
    store = ChromaVectorStore(
        collection_name="test-studybuddy",
        persist_directory="./db/test-chroma",
        model_name="all-MiniLM-L6-v2",
        device="cpu",
    )

    documents = [
        "Retrieval-Augmented Generation uses a vector database to augment answers.",
        "A study buddy can help a student understand concepts faster.",
    ]
    metadata = [{"source": "doc1"}, {"source": "doc2"}]
    ids = store.add_documents(documents, metadatas=metadata)

    assert len(ids) == 2

    results = store.search("What is retrieval-augmented generation?", n_results=1)
    assert results
    assert any("Retrieval-Augmented Generation" in doc for doc in results)
