import logging

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, SparseVectorParams, SparseIndexParams, Modifier

from app.core.config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparce"
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 200

client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

client.create_collection(
    collection_name=settings.QDRANT_COLLECTION_NAME,
    vectors_config={VECTOR_NAME: VectorParams(size=1536, distance=Distance.COSINE)},
    sparse_vectors_config={
        SPARSE_VECTOR_NAME: SparseVectorParams(
            modifier=Modifier.IDF, index=SparseIndexParams(on_disk=False)
        )
    },
)

vector_store = QdrantVectorStore(
    client=client,
    collection_name=settings.QDRANT_COLLECTION_NAME,
    embedding=embeddings,
    sparse_embedding=sparse_embeddings,
    retrieval_mode=RetrievalMode.HYBRID,
    vector_name=VECTOR_NAME,
    sparse_vector_name=SPARSE_VECTOR_NAME,
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)

docs = UnstructuredMarkdownLoader("data/lessons_clean.md").load()
splits = text_splitter.split_documents(docs)

vector_store.add_documents(splits)