from fastapi import APIRouter, Request
from app.services.log_service import save_log
from app.utils.llm import get_chat_model
from app.schemas import AgentQuery, AgentResponse, AgentAnswer, ErrorResponse


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

    - The agent searches **only** within the ingested dataset (data.txt).
    - If the requested information is not found, it responds politely
      that the answer is not available.
    """
    vector_store = request.app.state.vector_store
    if vector_store is None:
        return ErrorResponse(
            error={"code": 503, "message": "Vector store not available"}
        )

    retriever = vector_store.as_retriever()
    relevant_docs = retriever.invoke(query.question)

    # If no relevant docs → polite fallback
    if not relevant_docs:
        answer_text = (
            "I couldn’t find that information in Jorge’s profile. "
            "Please ask about his background, education, experience, or skills."
        )
        save_log(query.question, answer_text)
        return AgentResponse(
            data=AgentAnswer(question=query.question, answer=answer_text)
        )

    # Build context from retrieved docs
    context = " ".join([d.page_content for d in relevant_docs])

    # Get reusable chat model
    chat_model = get_chat_model()

    # Generate answer constrained to context
    answer = chat_model.invoke(
        f"Answer the question using ONLY the following context:\n\n{context}\n\n"
        f"If the answer is not explicitly in the context, respond with:\n"
        f"\"I couldn’t find that information in Jorge’s profile. "
        f"Please ask about his background, education, experience, or skills.\""
        f"\n\nQuestion: {query.question}"
    )

    save_log(query.question, answer.content)
    return AgentResponse(
        data=AgentAnswer(question=query.question, answer=answer.content)
    )