from typing import Union, Tuple, Optional
import piexif
import subprocess
import json


def get_gps(file_path: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    lower = file_path.lower()
    if lower.endswith((".jpg", ".jpeg")):
        return extract_gps_data_jpg(file_path)
    elif lower.endswith(".mp4"):
        return extract_gps_data_mp4(file_path)
    elif lower.endswith(".png"):
        return extract_gps_data_png(file_path)
    else:
        return (None, None, None)


def extract_gps_data_jpg(
    image_path: str
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    try:
        exif_data = piexif.load(image_path)
        gps = exif_data.get('GPS')
        if not gps:
            return (None, None, None)

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
        return (None, None, None)


def extract_gps_data_png(
    file_path: str
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    # PNGs rarely have EXIF GPS; try similar approach or fallback to None
    # You could extend with specialized PNG metadata parsing if needed
    return (None, None, None)


def extract_gps_data_mp4(
    file_path: str
) ->  Tuple[Optional[float], Optional[float], Optional[float]]:
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
    return (None, None, None)
