import os 
import pandas as pd

from get_datetime import get_datetime
from get_gps import get_gps
from get_colors import get_colors
from datetime import timezone


def get_media_metadata(file_paths):
    records = []

    for path in file_paths:
        dt, media_type = get_datetime(path)
        lat, lon, alt = get_gps(path)
        dominant_colors = get_colors(path)
        

        records.append({
            "datetime": dt,
            "type": media_type,
            "filename": os.path.basename(path),
            "latitude": lat,
            "longitude": lon,
            "altitude": alt,
            "color_1": dominant_colors[0],
            "color_2": dominant_colors[1],
            "color_3": dominant_colors[2],
        })

    return pd.DataFrame(records)
