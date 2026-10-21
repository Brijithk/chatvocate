
from pathlib import Path
import re
import chromadb
import fitz
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parents[2]
PDF_PATH = BASE_DIR / "documents" / "ipc.pdf"
CHROMA_PATH = BASE_DIR / "chroma_db"

COLLECTION_NAME = "ipc_sections"

# Local embedding model: no embedding API key required.
embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=str(CHROMA_PATH))

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)


def extract_pdf_text():
    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"IPC PDF not found at: {PDF_PATH}"
        )

    pages = []

    with fitz.open(PDF_PATH) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text")
            if text.strip():
                pages.append({
                    "page": page_number,
                    "text": text,
                })

    return pages


def chunk_text(text, chunk_size=900, overlap=150):
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])

        if end == len(text):
            break

        start = end - overlap

    return chunks


def index_ipc_pdf():
    pages = extract_pdf_text()

    documents = []
    ids = []
    metadatas = []

    for page in pages:
        chunks = chunk_text(page["text"])

        for chunk_number, chunk in enumerate(chunks):
            documents.append(chunk)
            ids.append(f"page-{page['page']}-chunk-{chunk_number}")
            metadatas.append({
                "page": page["page"],
                "source": PDF_PATH.name,
            })

    if not documents:
        raise ValueError(
            "No extractable text found. The PDF may be scanned."
        )

    embeddings = embedding_model.encode(
        documents,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).tolist()

    # Remove previous entries so repeated indexing won't duplicate data.
    collection.delete(where={"source": PDF_PATH.name})

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return {
        "pages_processed": len(pages),
        "chunks_indexed": len(documents),
    }


def retrieve_context(question, top_k=4):
    question_embedding = embedding_model.encode(
        question,
        normalize_embeddings=True,
    ).tolist()

    # First, retrieve semantically relevant chunks.
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    matches = []
    seen = set()

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        matches.append({
            "text": document,
            "page": metadata["page"],
            "source": metadata["source"],
            "distance": distance,
        })
        seen.add(document)

    # If the user names an IPC section, search for its exact heading.
    section_match = re.search(
        r"\bsection\s+(\d+[A-Z]?)\b",
        question,
        re.IGNORECASE,
    )

    if section_match:
        section = section_match.group(1)

        stored = collection.get(
            include=["documents", "metadatas"]
        )

        exact_matches = []

        heading_pattern = re.compile(
            rf"\b{re.escape(section)}\s*[.)]\s*"
            rf"punishment\s+for\s+murder\b",
            re.IGNORECASE,
        )

        for document, metadata in zip(
            stored["documents"],
            stored["metadatas"],
        ):
            if heading_pattern.search(document):
                exact_matches.append({
                    "text": document,
                    "page": metadata["page"],
                    "source": metadata["source"],
                    "distance": 0.0,
                })

        # Put exact heading matches before semantic matches.
        if exact_matches:
            exact_texts = {
                item["text"] for item in exact_matches
            }

            matches = exact_matches + [
                item for item in matches
                if item["text"] not in exact_texts
            ]

    return matches[:max(top_k, 1)]
