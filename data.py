import os
import piexif
import exifread
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import subprocess
import json

import pandas as pd
from datetime import datetime, date, timezone
from typing import Union, Tuple

def extract_datetime_from_jpg(file_path):
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


def extract_datetime_from_mp4(file_path):
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
            return datetime.fromisoformat(creation_time.replace("Z", "+00:00"))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None


def extract_datetime_from_png_or_fallback(file_path):
    try:
        timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        print(f"[PNG] Failed to get mod time for {file_path}: {e}")
    return None


def extract_gps_data_jpg(image_path: str) -> Union[Tuple[float, float, float], None]:
    try:
        exif_data = piexif.load(image_path)
        gps = exif_data.get('GPS')
        if not gps:
            return None

        def convert_to_degrees(value):
            d, m, s = value
            return d[0]/d[1] + m[0]/(m[1]*60) + s[0]/(s[1]*3600)

        lat = convert_to_degrees(gps[2])
        if gps[1] == b'S':
            lat = -lat

        lon = convert_to_degrees(gps[4])
        if gps[3] == b'W':
            lon = -lon

        alt = None
        if 6 in gps:
            alt_num, alt_den = gps[6]
            alt = alt_num / alt_den if alt_den != 0 else None

        return (lat, lon, alt)

    except Exception as e:
        print(f"Failed to extract GPS from {image_path}: {e}")
        return None


def extract_gps_data_png(file_path: str) -> Union[Tuple[float, float, float], None]:
    # PNGs rarely have EXIF GPS; try similar approach or fallback to None
    # You could extend with specialized PNG metadata parsing if needed
    return None


def extract_gps_data_mp4(file_path: str) -> Union[Tuple[float, float, float], None]:
    # Extract GPS metadata from MP4 using ffprobe if available
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_entries", "format_tags=location",
                "-i", file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        data = json.loads(result.stdout)
        location = data.get("format", {}).get("tags", {}).get("location")
        if location:
            # Example location format: "+37.7749-122.4194/" (lat/lon)
            # Parsing may need adjustment depending on actual format
            loc_str = location.strip().replace('/', '')
            lat_str = ''
            lon_str = ''
            i = 0
            # Extract latitude
            if loc_str[i] in ('+', '-'):
                lat_str += loc_str[i]
                i += 1
            while i < len(loc_str) and (loc_str[i].isdigit() or loc_str[i] == '.'):
                lat_str += loc_str[i]
                i += 1
            # Extract longitude
            if i < len(loc_str) and loc_str[i] in ('+', '-'):
                lon_str += loc_str[i]
                i += 1
            while i < len(loc_str) and (loc_str[i].isdigit() or loc_str[i] == '.'):
                lon_str += loc_str[i]
                i += 1
            lat = float(lat_str)
            lon = float(lon_str)
            alt = None
            return (lat, lon, alt)
    except Exception as e:
        print(f"Failed to extract GPS from {file_path}: {e}")
    return None


def get_datetime(file_path):
    lower = file_path.lower()
    if lower.endswith((".jpg", ".jpeg")):
        dt = extract_datetime_from_jpg(file_path)
        if not dt:
            print(f"[JPG] Falling back to mod time for {file_path}")
            dt = extract_datetime_from_png_or_fallback(file_path)
        return dt
    elif lower.endswith(".mp4"):
        return extract_datetime_from_mp4(file_path)
    elif lower.endswith(".png"):
        return extract_datetime_from_png_or_fallback(file_path)
    else:
        return None


def get_gps(file_path):
    lower = file_path.lower()
    if lower.endswith((".jpg", ".jpeg")):
        return extract_gps_data_jpg(file_path)
    elif lower.endswith(".mp4"):
        return extract_gps_data_mp4(file_path)
    elif lower.endswith(".png"):
        return extract_gps_data_png(file_path)
    else:
        return None


def get_media_metadata(file_paths):
    records = []

    for path in file_paths:
        dt = get_datetime(path)
        media_type = None
        lower = path.lower()
        if lower.endswith((".jpg", ".jpeg", ".png")):
            media_type = "photo"
        elif lower.endswith(".mp4"):
            media_type = "video"

        if dt:
            if dt.tzinfo:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
            gps = get_gps(path)
            lat, lon, alt = (gps if gps else (None, None, None))
            records.append({
                "datetime": dt,
                "type": media_type,
                "filename": os.path.basename(path),
                "latitude": lat,
                "longitude": lon,
                "altitude": alt
            })
        else:
            print(f"[SKIP] No datetime found for {path}")

    return pd.DataFrame(records)
