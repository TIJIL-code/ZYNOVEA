import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
COLLECTION_NAME = "zynovea_clinic_memory"

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
client = QdrantClient(url=QDRANT_URL)

def ensure_collection(recreate: bool = False):
    if client.collection_exists(COLLECTION_NAME) and recreate:
        client.delete_collection(COLLECTION_NAME)
    
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

def seed_dummy_data(recreate: bool = True):
    ensure_collection(recreate=recreate)
    
    records = [
        {"id": 1, "patient_id": "GLOBAL", "text": "ZYNOVEA Clinic hours: Mon-Fri 8am-6pm. Location: 100 Health Way."},
        {"id": 2, "patient_id": "GLOBAL", "text": "Dr. Smith specializes in Cardiology and is available Mon/Wed/Fri."},
        {"id": 3, "patient_id": "GLOBAL", "text": "Dr. Adams specializes in Pediatrics and General Practice, available Tue/Thu."},
        {"id": 4, "patient_id": "patient_1001", "text": "Patient 1001: John Doe. Scheduled for Blood Pressure check on Friday at 10 AM."},
    ]
    
    points = []
    for r in records:
        emb = model.encode(r["text"]).tolist()
        points.append(PointStruct(id=r["id"], vector=emb, payload=r))
        
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Seeded {len(records)} records into Qdrant collection '{COLLECTION_NAME}'")

def search_memory(query: str, patient_id: str = "patient_1001", top_k: int = 2) -> str:
    if not client.collection_exists(COLLECTION_NAME):
        return ""
    
    query_vector = model.encode(query).tolist()
    
    # Updated method for qdrant-client >= 1.8.0
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    )
    
    retrieved = [hit.payload["text"] for hit in results.points if hit.payload]
    return "\n".join(retrieved)
if __name__ == "__main__":
    seed_dummy_data(recreate=True)