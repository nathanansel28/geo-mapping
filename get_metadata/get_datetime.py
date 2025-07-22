from typing import Optional, Tuple
import os
import exifread
import subprocess
import json

import pandas as pd
from datetime import datetime, date, timezone
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns


def get_datetime(filepath) -> Tuple[Optional[datetime], str]:
    """Returns the datetime and media type of a given file."""
    dt = None
    filepath_lower = filepath.lower() 
    if filepath_lower.endswith((".jpg", ".jpeg")):
        dt = extract_datetime_from_jpg(filepath)
        if not dt:
            print(f"[JPG] Falling back to mod time for {filepath}")
            dt = extract_datetime_from_png_or_fallback(filepath)
        media_type = "photo"

    elif filepath_lower.endswith(".mp4"):
        dt = extract_datetime_from_mp4(filepath)
        media_type = "video"

    elif filepath_lower.endswith(".png"):
        dt = extract_datetime_from_png_or_fallback(filepath)
        media_type = "photo"
    else:
        raise ValueError(f"Unsupported file type for: {filepath}")

    if dt:
        if dt.tzinfo:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        else:
            print(f"[WARNING] No datetime found for {filepath}")

    return dt, media_type


def extract_datetime_from_jpg(file_path) -> Optional[datetime]:
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
            date_tag = (
                tags.get("EXIF DateTimeOriginal") or
                tags.get("Image DateTime") or
                tags.get("EXIF DateTimeDigitized")
            )
            if date_tag:
                return datetime.strptime(str(date_tag), "%Y:%m:%d %H:%M:%S")
            else:
                print(f"[JPG] No EXIF date found for {file_path}")
    except Exception as e:
        print(f"[JPG] Error reading {file_path}: {e}")
    return None


def extract_datetime_from_mp4(file_path) -> Optional[datetime]:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_entries", "format_tags=creation_time",
                "-i", file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        data = json.loads(result.stdout)
        creation_time = data.get("format", {}).get("tags", {}).get("creation_time")

        if creation_time:
            # Standard format: '2022-03-28T14:20:30.000000Z'
            return datetime.fromisoformat(creation_time.replace("Z", "+00:00"))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def extract_datetime_from_png_or_fallback(file_path) -> Optional[datetime]:
    try:
        timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        print(f"[PNG] Failed to get mod time for {file_path}: {e}")
        return None
