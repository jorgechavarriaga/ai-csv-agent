import urllib.parse
from typing import Dict

from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, OperationalError
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

from app.utils.logging.logger import get_logger
from app.config.settings import settings
from app.services.seed_documents import seed_all_documents_in_data_folder

# Logger
logger = get_logger("AI Agent")

# Encode password and construct DB URI
encoded_pass = urllib.parse.quote_plus(settings.POSTGRES_PASSWORD.get_secret_value())
CONNECTION_URI = f"postgresql+psycopg://{settings.POSTGRES_USER}:{encoded_pass}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Embeddings instance (OpenAI)
embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)

# List of all vector store collections to initialize
COLLECTIONS = ["cv_en_embeddings", "faq_en_embeddings"]


def get_all_vector_stores(force: bool = False) -> Dict[str, PGVector]:
    """
    Initialize and return a dictionary of PGVector instances for all collections.
    Seeds data only if the collection is empty, unless force=True.
    """
    vector_stores = {}
    engine = create_engine(CONNECTION_URI, future=True)

    for collection_name in COLLECTIONS:
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT COUNT(*) FROM langchain_pg_embedding e
                        JOIN langchain_pg_collection c ON e.collection_id = c.uuid
                        WHERE c.name = :name
                    """),
                    {"name": collection_name},
                ).scalar()

            if force or result == 0:
                if result == 0:
                    logger.warning("Collection '%s' empty. Seeding...", collection_name)
                elif force:
                    logger.warning("Force seeding enabled for collection '%s'.", collection_name)

                seed_all_documents_in_data_folder()

                # Recheck
                with engine.connect() as conn:
                    result = conn.execute(
                        text("""
                            SELECT COUNT(*) FROM langchain_pg_embedding e
                            JOIN langchain_pg_collection c ON e.collection_id = c.uuid
                            WHERE c.name = :name
                        """),
                        {"name": collection_name},
                    ).scalar()

                if result == 0:
                    logger.error("Seeding failed: no documents inserted into '%s'.", collection_name)
                    continue

                logger.info("Collection '%s' loaded into vector store.", collection_name)
            else:
                logger.info("Collection '%s' loaded into vector store.", collection_name)

            # Init and store vector store
            vector_stores[collection_name] = PGVector(
                embeddings,
                collection_name=collection_name,
                connection=CONNECTION_URI,
            )

        except (ProgrammingError, OperationalError) as e:
            logger.error("Error while loading vector store '%s': %s", collection_name, e)

    if not vector_stores:
        logger.warning("No vector stores loaded.")

    logger.info("Vector stores initialized successfully.")
    return vector_stores
