import os 
import pandas as pd

from get_datetime import (
    extract_datetime_from_jpg, 
    extract_datetime_from_mp4, 
    extract_datetime_from_png_or_fallback
)
from datetime import timezone


def get_media_metadata(file_paths):
    records = []

    for path in file_paths:
        lower = path.lower()
        dt = None
        media_type = None

        if lower.endswith((".jpg", ".jpeg")):
            dt = extract_datetime_from_jpg(path)
            if not dt:
                print(f"[JPG] Falling back to mod time for {path}")
                dt = extract_datetime_from_png_or_fallback(path)
            media_type = "photo"

        elif lower.endswith(".mp4"):
            dt = extract_datetime_from_mp4(path)
            media_type = "video"

        elif lower.endswith(".png"):
            dt = extract_datetime_from_png_or_fallback(path)
            media_type = "photo"

        if dt:
            if dt.tzinfo:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            records.append({
                "datetime": dt,
                "type": media_type,
                "filename": os.path.basename(path)
            })
        else:
            print(f"[SKIP] No datetime found for {path}")

    return pd.DataFrame(records)

