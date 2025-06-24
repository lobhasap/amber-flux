from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List
import os
import cv2
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

app = FastAPI()

# Placeholder: Directory to save extracted frames
OUTPUT_DIR = 'frames_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Qdrant setup
QDRANT_COLLECTION = 'frame_vectors'
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

print(qdrant.get_collections())

# Create collection if not exists
try:
    qdrant.get_collection(QDRANT_COLLECTION)
except Exception:
    qdrant.recreate_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=qdrant_models.VectorParams(size=512, distance="Cosine")
    )

def compute_feature_vector(image):
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist.astype(np.float32)

@app.post('/upload_video/')
def upload_video(file: UploadFile = File(...), interval: int = Form(1)):
    """
    Endpoint to upload a video and extract frames at the specified interval (in seconds).
    """
    video_path = os.path.join(OUTPUT_DIR, file.filename)
    with open(video_path, 'wb') as f:
        f.write(file.file.read())
    
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)
    count = 0
    saved_count = 0
    points = []
    payloads = []
    while True:
        success, image = vidcap.read()
        if not success:
            break
        if count % frame_interval == 0:
            frame_filename = f"frame_{saved_count}.jpg"
            frame_path = os.path.join(OUTPUT_DIR, frame_filename)
            cv2.imwrite(frame_path, image)
            vector = compute_feature_vector(image)
            points.append(vector.tolist())
            payloads.append({"frame_path": frame_path})
            saved_count += 1
        count += 1
    vidcap.release()
    # Store in Qdrant
    if points:
        qdrant.upsert(
            collection_name=QDRANT_COLLECTION,
            points=[
                qdrant_models.PointStruct(
                    id=i,
                    vector=vec,
                    payload=payloads[i]
                ) for i, vec in enumerate(points)
            ]
        )
    return {"frames_extracted": saved_count}

@app.post('/retrieve_similar_frames/')
def retrieve_similar_frames(query_vector: List[float]):
    search_result = qdrant.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=5
    )
    results = []
    for hit in search_result:
        results.append({
            "frame_path": hit.payload.get("frame_path"),
            "vector": hit.vector,
            "score": hit.score
        })
    return {"results": results}

# TODO: Add logic for feature vector computation and Qdrant integration 

print(frame_features[0]["vector"]) 