from typing import List
from download_shapefiles import download_natural_earth_populated_places
import os

def setup_and_fetch_variables() -> dict:
    if not os.path.exists("assets/ne_10m_populated_places.shp"):
        download_natural_earth_populated_places()
    os.makedirs("output", exist_ok=True)
    folder_paths = os.environ.get("FOLDER_PATH")
    folder_paths = folder_paths.split(",") if folder_paths else []

    env_variables = {
        "folder_paths": folder_paths
    }
    return env_variables
    