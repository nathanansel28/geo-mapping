import requests
import zipfile
import io
import os
import geopandas as gpd

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


def download_gadm_shapefile(iso_code='SWE', level=2, output_dir='assets/gadm_data'):
    """
    Download and extract GADM shapefile for a specific country and administrative level.

    Parameters:
    - iso_code: str (e.g. 'SWE' for Sweden, 'USA' for United States)
    - level: int (0 = country, 1 = regions, 2 = cities/districts, etc.)
    - output_dir: str (directory to store downloaded data)

    Returns:
    - GeoDataFrame if GeoPandas can read the shapefile.
    """
    base_url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_{iso_code}_shp.zip"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Downloading from: {base_url}")
    r = requests.get(base_url)
    if r.status_code != 200:
        raise Exception(f"Failed to download file: HTTP {r.status_code}")

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        z.extractall(output_dir)

    shapefile_path = os.path.join(output_dir, f"gadm41_{iso_code}_{level}.shp")
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Level {level} shapefile not found in ZIP archive.")

    gdf = gpd.read_file(shapefile_path)
    print(f"Loaded shapefile with {len(gdf)} entries")
    return gdf
