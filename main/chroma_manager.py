from chromadb import Client
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings

client = Client(Settings())
collection = client.get_or_create_collection("chapters")
encoder = SentenceTransformer("all-MiniLM-L6-v2")

def add_version(chapter_id, stage, text, metadata):
    embedding = encoder.encode(text).tolist()
    collection.add(
        documents=[text],
        ids=[f"{chapter_id}-{stage}"],
        embeddings=[embedding],
        metadatas=[metadata]
    )

def search_chapters(query, k=5):
    results = collection.query(
        query_texts=[query],
        n_results=k
    )

    doc_ids = results["ids"][0]
    contents = results["documents"][0]
    metadatas = results["metadatas"][0]

    return list(zip(doc_ids, contents, metadatas))
