import logging
from uuid import uuid4

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    VectorParams,
    Distance,
    SparseVectorParams,
    SparseIndexParams,
    Modifier,
)

from app.core.config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparce"
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 200

client = QdrantClient(host=settings.QDRANT_HOST_OFFLINE, port=settings.QDRANT_PORT)

def create_qdrant_collection():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

    logger.info("Creating data collection")

    if client.collection_exists(settings.QDRANT_COLLECTION_NAME):
        client.delete_collection(settings.QDRANT_COLLECTION_NAME)

    client.create_collection(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        vectors_config={VECTOR_NAME: VectorParams(size=1536, distance=Distance.COSINE)},
        sparse_vectors_config={
            SPARSE_VECTOR_NAME: SparseVectorParams(
                modifier=Modifier.IDF, index=SparseIndexParams(on_disk=False)
            )
        },
    )

    logger.info("Creating vector store")
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

    logger.info("Loading and splitting lesson data")
    docs = UnstructuredMarkdownLoader("./data_pipeline/data/lessons_clean.md").load()
    splits = text_splitter.split_documents(docs)

    logger.info("Upserting data points")
    uuids = [str(uuid4()) for _ in range(len(splits))]
    vector_store.add_documents(splits, uuids=uuids)

if __name__ == "__main__":
    if not client.collection_exists(settings.QDRANT_COLLECTION_NAME):
        logging.warning(f"Collection {settings.QDRANT_COLLECTION_NAME} does not exist. Creating...")
        create_qdrant_collection()