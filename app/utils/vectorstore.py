import urllib.parse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, OperationalError
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from app.utils.logging.logger import get_logger
from app.config.settings import settings

# Initialize logger
logger = get_logger("AI Agent")

encoded_pass = urllib.parse.quote_plus(settings.POSTGRES_PASSWORD.get_secret_value())
CONNECTION_URI = f"postgresql+psycopg://{settings.POSTGRES_USER}:{encoded_pass}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Embeddings
embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
collection_name = "cv_embeddings"

def seed_documents():
    """Load data.txt, split, and seed documents into Postgres."""
    with open("data/data.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    docs = splitter.split_documents([Document(page_content=raw_text)])

    return PGVector.from_documents(
        docs,
        embeddings,
        collection_name=collection_name,
        connection=CONNECTION_URI,
    )


def get_vector_store() -> PGVector | None:
    """Return vector_store if DB is reachable, otherwise None."""
    try:
        engine = create_engine(CONNECTION_URI, future=True)
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT COUNT(*) FROM langchain_pg_embedding e "
                    "JOIN langchain_pg_collection c ON e.collection_id = c.uuid "
                    "WHERE c.name = :name"
                ),
                {"name": collection_name},
            ).scalar()

        if result == 0:
            logger.warning("Collection '%s' empty. Seeding...", collection_name)
            return seed_documents()

        logger.info("Collection '%s' loaded successfully with %s documents.", collection_name, result)
        return PGVector(
            embeddings,
            collection_name=collection_name,
            connection=CONNECTION_URI,
        )

    except (ProgrammingError, OperationalError) as e:
        logger.error("Database error while initializing vector store: %s", e)
        return None