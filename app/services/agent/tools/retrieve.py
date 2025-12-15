from langchain_core.tools import tool
from langchain_qdrant import QdrantVectorStore


def create_retrieve_docs_tool(vector_store: QdrantVectorStore):
    """
    Factory function that creates a tool with a bound vector store

    :param vector_store: Pass vector store item to the retriever tool
    :type vector_store: QdrantVectorStore
    """

    @tool(
        response_format="content_and_artifact",
        description="Retrieve lesson Context for the answer",
    )
    def retrieve_docs(query: str):
        retrieved_docs = vector_store.similarity_search(query)
        serialized = "\n\n".join(
            f"Context: {doc.page_content}" for doc in retrieved_docs
        )
        return serialized, retrieved_docs

    return retrieve_docs
