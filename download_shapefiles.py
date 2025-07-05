import requests
import zipfile
import io
import os

def download_natural_earth_populated_places(output_dir="assets"):
    url = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_populated_places.zip"
    
    os.makedirs(output_dir, exist_ok=True)

    print("Downloading shapefile...")
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"Failed to download: {r.status_code}")

    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(output_dir)

    print(f"Extracted to: {output_dir}")
    return os.path.join(output_dir, "ne_10m_populated_places.shp")
