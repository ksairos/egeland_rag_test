from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain_core.messages import RemoveMessage
from langgraph.runtime import Runtime
from qdrant_client import QdrantClient
from typing import Any

from app.core.config import settings

client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparce"

vector_store = QdrantVectorStore(
    client=client,
    collection_name=settings.QDRANT_COLLECTION_NAME,
    embedding=embeddings,
    sparse_embedding=sparse_embeddings,
    retrieval_mode=RetrievalMode.HYBRID,
    vector_name=VECTOR_NAME,
    sparse_vector_name=SPARSE_VECTOR_NAME,
)

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


@tool(
    response_format="content_and_artifact",
    description="Retrieve lesson Context for the answer",
)
def retrieve_docs(query: str):
    retrieved_docs = vector_store.similarity_search(query)
    serialized = "\n\n".join(f"Context: {doc.page_content}" for doc in retrieved_docs)
    return serialized, retrieved_docs


system_prompt = """
    ROLE: Ты - профессиональный агент в RAG системе в роли преподавателя корейского языка.\n
    INSTRUCTION: Основываясь на истории чата с пользователем, сформируйте краткий, четкий и точный ответ на запрос пользователя.
    Если вопрос касается корейской грамматики, ОБЯЗАТЕЛЬНО используйте retrieve_docs tool для поиска контекста, который поможет ответить на вопрос пользователя.\n
    \n
    ПРАВИЛО ИСПОЛЬЗОВАНИЯ retrieve_docs():\n
    retrieve_docs() использует технологию Hypothetical Document Embeddings. Прежде чем использовать инструмент, сгенерируйте гипотетический ответ,
    который напрямую отвечает на этот вопрос. Текст должен быть кратким и содержать только необходимую информацию. Уместите ответ в 2-3 предложениях.
    Используйте ответ, чтобы найти наиболее подходящую информацию с помощью инструмента retrieve_docs()\n
    \n
    ВАЖНО:\n
    Если документов нет или они не подходят для ответа на запрос, не старайтесь ответить на запрос пользователя самостоятельно. Скажите, что не знаете\n
    \n
    ФОРМАТИРОВАНИЕ: Всегда используйте Markdown синтаксис (**жирный**, *курсив*, `код`) вместо HTML тегов для форматирования ответов.
    """


@before_model
def trim_messages(
    state: AgentState, runtime: Runtime, num_to_keep: int = 10
) -> dict[str, Any] | None:
    messages = state["messages"]

    if len(messages) <= 10:
        return None

    first_msg = messages[0]
    while num_to_keep < len(messages) and messages[-num_to_keep].type == "tool":
        num_to_keep += 1

    recent_messages = [first_msg] + messages[-num_to_keep - 1 :]

    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *recent_messages]}
