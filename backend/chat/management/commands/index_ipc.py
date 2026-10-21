
from django.core.management.base import BaseCommand, CommandError

from chat.services.rag_service import index_ipc_pdf


class Command(BaseCommand):
    help = "Extract IPC PDF text and index it in ChromaDB"

    def handle(self, *args, **options):
        self.stdout.write("Starting IPC PDF indexing...")

        try:
            result = index_ipc_pdf()
        except Exception as exc:
            raise CommandError(
                f"IPC indexing failed: {exc}"
            ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "IPC indexing completed successfully!\n"
                f"Pages processed: {result['pages_processed']}\n"
                f"Chunks indexed: {result['chunks_indexed']}"
            )
        )
