from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.postgres import PostgresSaver
from qdrant_client import QdrantClient

from app.core.config import settings
from app.core.prompts import SYSTEM_PROMPT
from app.models.schemas import CustomAgentState
from app.services.agent.tools.retrieve import create_retrieve_docs_tool
from app.services.agent.tools.messages import trim_messages


# client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


def get_vector_store(client: QdrantClient) -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client,
        collection_name=settings.QDRANT_COLLECTION_NAME,
        embedding=embeddings,
        sparse_embedding=sparse_embeddings,
        retrieval_mode=RetrievalMode.HYBRID,
        vector_name=settings.VECTOR_NAME,
        sparse_vector_name=settings.SPARSE_VECTOR_NAME,
    )


def build_rag_agent(checkpointer: PostgresSaver):
    qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    vector_store = get_vector_store(qdrant_client)
    retrieve_docs = create_retrieve_docs_tool(vector_store)

    rag_agent: CompiledStateGraph = create_agent(
        model=model,
        tools=[retrieve_docs],
        state_schema=CustomAgentState,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
        middleware=[trim_messages],
    )
    return rag_agent
