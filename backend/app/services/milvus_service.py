import logging

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)

_model: SentenceTransformer | None = None
_collection: Collection | None = None

EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output dimension


def init_milvus() -> None:
    global _model, _collection

    logger.info("Loading embedding model: %s", settings.embedding_model)
    _model = SentenceTransformer(settings.embedding_model)

    logger.info(
        "Connecting to Milvus at %s:%s", settings.milvus_host, settings.milvus_port
    )
    connections.connect(
        alias="default", host=settings.milvus_host, port=settings.milvus_port
    )

    _ensure_collection()
    logger.info("Milvus service initialized")


def _ensure_collection() -> None:
    global _collection

    collection_name = settings.milvus_collection

    if utility.has_collection(collection_name):
        _collection = Collection(collection_name)
        _collection.load()
        logger.info("Collection '%s' loaded (%d entities)", collection_name, _collection.num_entities)
        return

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="chunk", dtype=DataType.VARCHAR, max_length=8192),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="opening_name", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(
            name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM
        ),
    ]
    schema = CollectionSchema(fields=fields, description="Chess openings from Wikichess")
    _collection = Collection(name=collection_name, schema=schema)

    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128},
    }
    _collection.create_index(field_name="embedding", index_params=index_params)
    _collection.load()
    logger.info("Collection '%s' created and loaded", collection_name)


def get_embedding(text: str) -> list[float]:
    if _model is None:
        raise RuntimeError("Embedding model not initialized")
    return _model.encode(text, normalize_embeddings=True).tolist()


def insert_documents(
    titles: list[str],
    chunks: list[str],
    sources: list[str],
    opening_names: list[str],
) -> int:
    if _collection is None:
        raise RuntimeError("Milvus collection not initialized")

    embeddings = [get_embedding(chunk) for chunk in chunks]

    data = [titles, chunks, sources, opening_names, embeddings]
    result = _collection.insert(data)
    _collection.flush()
    logger.info("Inserted %d documents", len(chunks))
    return result.insert_count


def search(query: str, top_k: int = 5) -> list[dict]:
    if _collection is None or _model is None:
        raise RuntimeError("Milvus service not initialized")

    query_embedding = get_embedding(query)

    search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}

    results = _collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["title", "chunk", "source", "opening_name"],
    )

    hits = []
    for hit in results[0]:
        hits.append(
            {
                "title": hit.entity.get("title"),
                "chunk": hit.entity.get("chunk"),
                "source": hit.entity.get("source"),
                "opening_name": hit.entity.get("opening_name"),
                "score": round(hit.score, 4),
            }
        )
    return hits


def close_milvus() -> None:
    global _collection, _model
    if _collection is not None:
        _collection.release()
        _collection = None
    _model = None
    connections.disconnect("default")
    logger.info("Milvus service closed")
