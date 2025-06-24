# FastAPI Video Frame Feature Retrieval

## Overview
This app allows you to upload a video, extracts frames at a specified interval, computes feature vectors (color histograms) for each frame, and enables retrieval of similar frames using a REST API. Feature vectors are stored and retrieved from a Qdrant vector database.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start Qdrant (Docker recommended):
   ```bash
   docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
   ```
3. Run the app:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### 1. Upload Video & Extract Frames
- **POST** `/upload_video/`
- **Form Data:**
  - `file`: Video file (e.g., MP4)
  - `interval`: Interval in seconds (default: 1)
- **Response:**
  - `{ "frames_extracted": <number> }`

### 2. Retrieve Similar Frames
- **POST** `/retrieve_similar_frames/`
- **Body (JSON):**
  - `query_vector`: List of floats (feature vector)
- **Response:**
  - `results`: List of top 5 similar frames with image paths, vectors, and similarity scores

## Output
- Extracted frames are saved in the `frames_output` directory.

## Notes
- Feature vectors are color histograms (8x8x8 bins, normalized).
- Vectors are stored and searched in Qdrant for persistent and scalable retrieval. 