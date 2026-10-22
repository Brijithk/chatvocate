
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from chat.services.rag_service import retrieve_context
from chat.services.llm_service import generate_answer


@api_view(["GET"])
def health_check(request):
    return Response({
        "status": "success",
        "message": "CHATVOCATE API is running!",
    })


@api_view(["POST"])
def chat_view(request):
    question = request.data.get("question", "")

    if not isinstance(question, str) or not question.strip():
        return Response(
            {"error": "Please provide a question."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    question = question.strip()

    try:
        context_chunks = retrieve_context(question, top_k=4)
        answer = generate_answer(question, context_chunks)

        sources = [
            {
                "source": item["source"],
                "page": item["page"],
                "text": item["text"],
            }
            for item in context_chunks
        ]

        return Response({
            "question": question,
            "answer": answer,
            "sources": sources,
        })

    except Exception:
        return Response(
            {"error": "Unable to generate an answer right now."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
