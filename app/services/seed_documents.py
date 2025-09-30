import os
import re
from typing import List
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from app.config.settings import settings
from app.utils.logging.logger import get_logger


logger = get_logger("SeedDocuments")

embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)

CONNECTION_URI = f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD.get_secret_value()}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"


def parse_sections_from_text(raw_text: str) -> List[Document]:
    """
    Parse the text into sections based on headers and return Langchain Documents.
    """
    lines = raw_text.splitlines()
    sections = []
    current_title = None
    buffer = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        is_section = (
            not stripped.startswith(("-", "*"))
            and not line.startswith(" ")
            and len(stripped.split()) <= 10
        )
        if is_section:
            if current_title and buffer:
                sections.append({
                    "title": current_title,
                    "content": "\n".join(buffer).strip()
                })
                buffer = []
            current_title = stripped
        else:
            buffer.append(stripped)
    if current_title and buffer:
        sections.append({
            "title": current_title,
            "content": "\n".join(buffer).strip()
        })
    documents = [
        Document(page_content=f"{s['title']}\n{s['content']}")
        for s in sections
    ]
    return documents


def seed_all_documents_in_data_folder():
    """
    Look for all `cv_??.txt` and `faq_??.txt` files in /data and seed them as separate collections.
    """
    folder = "data"
    pattern = re.compile(r"^(cv|faq)_[a-z]{2}\.txt$", re.IGNORECASE)
    files = [f for f in os.listdir(folder) if pattern.match(f)]
    if not files:
        logger.warning("No valid CV or FAQ files found in /data.")
        return
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    for filename in files:
        path = os.path.join(folder, filename)
        collection_name = filename.replace(".txt", "_embeddings")
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            if not raw_text.strip():
                logger.warning("Skipping empty file: %s", filename)
                continue
            docs = parse_sections_from_text(raw_text)
            chunks = splitter.split_documents(docs)
            logger.info("Seeding %s chunks into collection '%s'...", len(chunks), collection_name)
            PGVector.from_documents(
                chunks,
                embedding=embeddings,
                collection_name=collection_name,
                connection=CONNECTION_URI,
            )
        except Exception as e:
            logger.error("Failed to seed %s: %s", filename, e)
