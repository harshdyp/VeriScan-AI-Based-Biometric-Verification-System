import torch
from PIL import Image
import numpy as np
from numpy.linalg import norm
import logging

# Initialize models lazily to avoid import-time errors
mtcnn = None
resnet = None
device = None

def _initialize_models():
    """Initialize ML models on first use"""
    global mtcnn, resnet, device
    
    if mtcnn is None:
        try:
            from facenet_pytorch import MTCNN, InceptionResnetV1
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {device}")

            # More robust defaults for general photos
            mtcnn = MTCNN(
                keep_all=False,
                device=device,
                image_size=160,
                margin=20,
                post_process=True,
                thresholds=[0.6, 0.7, 0.7],
            )
            resnet = InceptionResnetV1(pretrained="vggface2").eval().to(device)
            print("Face recognition models loaded successfully")
        except Exception as e:
            print(f"Error loading face recognition models: {e}")
            raise


def get_embedding(image_path: str):
    """Get face embedding from image"""
    try:
        _initialize_models()
        
        img = Image.open(image_path).convert("RGB")
        face = mtcnn(img)
        if face is None:
            print(f"No face detected in {image_path}")
            return None
        face = face.unsqueeze(0).to(device)
        embedding = resnet(face)
        return embedding.detach().cpu().numpy().flatten()
    except Exception as e:
        print(f"Error getting embedding from {image_path}: {e}")
        return None


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    try:
        denominator = norm(a) * norm(b)
        if denominator == 0:
            return 0.0
        return float(np.dot(a, b) / denominator)
    except Exception as e:
        print(f"Error calculating cosine similarity: {e}")
        return 0.0


def compare_faces(img1_path: str, img2_path: str) -> float:
    """Compare two face images and return similarity probability"""
    try:
        print(f"Comparing faces: {img1_path} vs {img2_path}")
        
        emb1 = get_embedding(img1_path)
        emb2 = get_embedding(img2_path)
        
        if emb1 is None or emb2 is None:
            print("Could not extract embeddings from one or both images")
            return 0.0
            
        similarity = cosine_similarity(emb1, emb2)
        prob = (similarity + 1) / 2
        print(f"Similarity: {similarity:.3f}, Probability: {prob:.3f}")
        return prob
        
    except Exception as e:
        print(f"Error comparing faces: {e}")
        return 0.0


