from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

def extract_dominant_colors(image_path: str, k=3, resize=200):
    """
    Extract k dominant RGB colors from image_path using k-means clustering.
    Resizes image to max dimension 'resize' to speed up processing.
    Returns list of (R, G, B) tuples.
    """
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.thumbnail((resize, resize))
            arr = np.array(img).reshape(-1, 3)
        
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(arr)
        colors = kmeans.cluster_centers_.astype(int)
        return [tuple(color) for color in colors]
    except Exception as e:
        print(f"[COLOR] Failed to extract colors from {image_path}: {e}")
        return [(0, 0, 0)] * k  # fallback black colors
