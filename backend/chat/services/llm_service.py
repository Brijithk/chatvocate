
import os

from dotenv import load_dotenv
from openai import OpenAI

# Load the .env file from the project root.
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is missing. Add it to the project root .env file."
    )

client = OpenAI(api_key=api_key)


def generate_answer(question, context_chunks):
    context = "\n\n".join(
        f"Source: {item['source']}, page {item['page']}\n{item['text']}"
        for item in context_chunks
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "You are CHATVOCATE, a legal information assistant. "
            "Answer using the supplied legal context. "
            "Do not invent legal provisions or citations. "
            "If the context is insufficient, say so clearly. "
            "Explain that your response is informational, not legal advice."
        ),
        input=(
            f"User question:\n{question}\n\n"
            f"Retrieved legal context:\n{context}"
        ),
    )

    return response.output_text
