import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

load_dotenv()

COLLECTION_NAME = "zynovea_clinic_memory"

# Initialize local embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Always use fast in-memory client if standalone server is unavailable
QDRANT_URL = os.getenv("QDRANT_URL", "").strip()

client = None
if QDRANT_URL and not QDRANT_URL.startswith("http://127.0.0.1:6333"):
    try:
        client = QdrantClient(url=QDRANT_URL, timeout=1.0, check_compatibility=False)
        client.get_collections()
    except Exception:
        client = None

if client is None:
    client = QdrantClient(":memory:")


def ensure_collection(recreate: bool = False):
    if client.collection_exists(COLLECTION_NAME) and recreate:
        client.delete_collection(COLLECTION_NAME)
    
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )


def seed_dummy_data(recreate: bool = False):
    ensure_collection(recreate=recreate)
    
    records = [
        {"id": 1, "patient_id": "GLOBAL", "text": "ZYNOVEA Clinic hours: Monday to Friday 8:00 AM to 6:00 PM. Location: 100 Health Way."},
        {"id": 2, "patient_id": "GLOBAL", "text": "Dr. Smith specializes in Cardiology and is available Monday, Wednesday, and Friday."},
        {"id": 3, "patient_id": "GLOBAL", "text": "Dr. Adams specializes in Pediatrics and General Practice, available Tuesday and Thursday."},
        {"id": 4, "patient_id": "patient_1001", "text": "Patient 1001: John Doe. Scheduled for a Blood Pressure check on Friday at 10:00 AM."},
    ]
    
    points = []
    for r in records:
        emb = model.encode(r["text"]).tolist()
        points.append(PointStruct(id=r["id"], vector=emb, payload=r))
        
    client.upsert(collection_name=COLLECTION_NAME, points=points)


# Seed initial records at startup
seed_dummy_data(recreate=True)


def search_memory(query: str, patient_id: str = "patient_1001", top_k: int = 2) -> str:
    try:
        if not client.collection_exists(COLLECTION_NAME):
            seed_dummy_data(recreate=False)
        
        query_vector = model.encode(query).tolist()
        
        try:
            results = client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                limit=top_k
            )
            retrieved = [hit.payload["text"] for hit in results.points if hit.payload and "text" in hit.payload]
        except AttributeError:
            results = client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                limit=top_k
            )
            retrieved = [hit.payload["text"] for hit in results if hit.payload and "text" in hit.payload]
            
        return "\n".join(retrieved)
    except Exception as e:
        print(f"Memory fallback active: {e}")
        return "Clinic hours: Monday to Friday 8:00 AM to 6:00 PM. Location: 100 Health Way. Appointments available Mon-Fri."


if __name__ == "__main__":
    test_query = "What time does the clinic close?"
    print(f"Result:\n{search_memory(test_query)}")