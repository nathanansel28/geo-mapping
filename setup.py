import os
from download_shapefiles import download_natural_earth_populated_places

def setup():
    download_natural_earth_populated_places()
    os.makedirs("output")
    