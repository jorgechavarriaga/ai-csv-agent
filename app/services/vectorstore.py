import urllib.parse
from typing import Dict, List
import re, os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, OperationalError
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from app.utils.logging.logger import get_logger
from app.config.settings import settings
from app.services.seed_documents import seed_all_documents_in_data_folder


logger = get_logger("AI Agent")

encoded_pass = urllib.parse.quote_plus(settings.POSTGRES_PASSWORD.get_secret_value())
CONNECTION_URI = f"postgresql+psycopg://{settings.POSTGRES_USER}:{encoded_pass}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)


def discover_collections() -> List[str]:
    folder = "data"
    pattern = re.compile(r"^(cv|faq)_[a-z]{2}\.txt$", re.IGNORECASE)
    files = [f for f in os.listdir(folder) if pattern.match(f)]
    collections = [f.replace(".txt", "_embeddings") for f in files]
    logger.info(f"🔎 Discovered collections: {collections}")
    return collections


def get_collection_count(engine, name: str) -> int:
    try:
        with engine.connect() as conn:
            return conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM langchain_pg_embedding e
                    JOIN langchain_pg_collection c ON e.collection_id = c.uuid
                    WHERE c.name = :name
                """),
                {"name": name},
            ).scalar() or 0
    except Exception:
        return 0


def get_all_vector_stores(force: bool = False) -> Dict[str, PGVector]:
    vector_stores: Dict[str, PGVector] = {}
    engine = create_engine(CONNECTION_URI, future=True)
    collections = discover_collections()
    if not collections:
        logger.warning("No CV/FAQ collections discovered in /data.")
        return vector_stores
    need_seed = force or any(get_collection_count(engine, c) == 0 for c in collections)
    if need_seed:
        if force:
            logger.warning("Force seeding enabled. Reseeding all collections...")
        else:
            logger.warning("Some collections are empty. Seeding once...")
        seed_all_documents_in_data_folder()
    for collection_name in collections:
        try:
            vector_stores[collection_name] = PGVector(
                embeddings,
                collection_name=collection_name,
                connection=CONNECTION_URI,
            )
            logger.info("Collection '%s' loaded into vector store.", collection_name)
        except (ProgrammingError, OperationalError) as e:
            logger.error("Error while loading vector store '%s': %s", collection_name, e)
    if not vector_stores:
        logger.warning("No vector stores loaded.")
    else:
        logger.info("Vector stores initialized successfully.")
    return vector_stores
