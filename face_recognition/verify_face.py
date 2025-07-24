import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import numpy as np

# Load pretrained model
device = 'cuda' if torch.cuda.is_available() else 'cpu'
mtcnn = MTCNN(keep_all=False, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def get_embedding(image_path):
    img = Image.open(image_path)
    face = mtcnn(img)
    if face is None:
        return None
    face = face.unsqueeze(0).to(device)
    embedding = resnet(face)
    return embedding.detach().cpu().numpy()

def compare_faces(img1_path, img2_path):
    emb1 = get_embedding(img1_path)
    emb2 = get_embedding(img2_path)
    if emb1 is None or emb2 is None:
        return 0
    distance = np.linalg.norm(emb1 - emb2)
    return float(distance < 1.0)  # 1 if similar, 0 otherwise 