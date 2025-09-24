from fastapi import APIRouter, Request
from app.services.log_service import save_log, get_last_messages
from app.utils.llm import get_chat_model
from app.schemas import AgentQuery, AgentResponse, AgentAnswer, ErrorResponse
from app.utils.logging.logger import get_logger


logger = get_logger("AI Agent")

router = APIRouter(tags=["Agent"])

@router.post(
    "/ask",
    summary="Ask Jorge’s AI Agent",
    response_model=AgentResponse,
    responses={
        200: {"description": "Successful answer", "model": AgentResponse},
        503: {"description": "Vector store not available", "model": ErrorResponse},
        500: {"description": "Unexpected error", "model": ErrorResponse},
    }
)


def ask_document(query: AgentQuery, request: Request):
    """
    Ask a question to Jorge's AI Agent.

    - Searches across ALL loaded vector collections (cv, faq, etc.).
    - If the answer isn't found in any, responds politely.
    """
    client_ip = request.headers.get("x-forwarded-for", request.client.host)
    session_id = query.session_id
    lang = (query.language or "en").lower()
    if lang not in ["en", "es", "fr"]:
        logger.warning(f"Unsupported language '{lang}', defaulting to English.")
        lang = "en"

    vector_stores = request.app.state.vector_stores
    best_docs = []
    collections = [f"cv_{lang}_embeddings", f"faq_{lang}_embeddings"]

    question = query.question.strip()

    best_source = None
    best_score = 0

    for collection_name in collections:
        vector_store = vector_stores.get(collection_name)
        if vector_store:
            results = vector_store.similarity_search_with_score(question, k=4)
            if results:
                avg_score = sum(score for _, score in results) / len(results)
                if best_docs == [] or avg_score < best_score:
                    best_docs = [doc for doc, _ in results]
                    best_score = avg_score
                    best_source = collection_name

    if not best_docs and lang != "en":
        logger.warning(f"No results found for language '{lang}'. Falling back to English collections.")
        for collection_name in ["cv_en_embeddings", "faq_en_embeddings"]:
            vector_store = vector_stores.get(collection_name)
            if vector_store:
                results = vector_store.similarity_search_with_score(question, k=4)
                if results:
                    avg_score = sum(score for _, score in results) / len(results)
                    if best_docs == [] or avg_score < best_score:
                        best_docs = [doc for doc, _ in results]
                        best_score = avg_score
                        best_source = collection_name

    if not best_docs:
        fallback = "I couldn’t find that information in Jorge’s profile. Please ask about his background, education, experience, or skills."
        save_log(session_id=session_id, question=question, answer=fallback, client_ip=client_ip)
        return AgentResponse(data=AgentAnswer(question=question, answer=fallback))

    context = "\n\n---\n\n".join(
        f"[source: {best_source}]\n{doc.page_content}" for doc in best_docs
    )

    chat_model = get_chat_model()
    chat_history = [
        {
            "role": "system",
            "content": (
                f"You are a helpful assistant. You must always answer strictly in {lang.upper()}.\n\n"
                "You are a helpful assistant that answers questions using ONLY the following context blocks.\n\n"
                "Each block starts with [source: cv] or [source: faq]. Use the information in these blocks to answer the user question.\n\n"
                "Do NOT use any prior knowledge, facts, or general information. Your answer MUST be based strictly on the provided context blocks.\n\n"
                "If the answer is not found explicitly in the context, respond exactly with:\n"
                "\"I couldn’t find that information in Jorge’s profile. Please ask about his background, education, experience, or skills.\"\n\n"
                "Give priority to blocks marked as [source: faq] if the question is about preferences, opinions, or personal logistics (e.g., salary, availability, goals, etc.).\n\n"
                f"You must always answer in {lang.upper()}.\n\n"   
                f"{context}"
            )
        }
    ]

    previous_logs = get_last_messages(session_id)
    for log in previous_logs:
        chat_history.append({"role": "user", "content": log.question})
        chat_history.append({"role": "assistant", "content": log.answer})

    chat_history.append({"role": "user", "content": question})
    answer = chat_model.invoke(chat_history)

    save_log(session_id=session_id, question=question, answer=answer.content, client_ip=client_ip)
    return AgentResponse(
        data=AgentAnswer(question=question, answer=answer.content)
    )