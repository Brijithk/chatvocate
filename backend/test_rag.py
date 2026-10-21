import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from chat.services.rag_service import retrieve_context

question = "What does Section 302 of the IPC say?"
results = retrieve_context(question)

for i, result in enumerate(results, start=1):
    print(f"\n--- Result {i} ---")
    print(f"Source page: {result['page']}")
    print(result["text"])