import os
import exifread
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import subprocess
import json

import pandas as pd
from datetime import datetime, date, timezone
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns


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
            # Standard format: '2022-03-28T14:20:30.000000Z'
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


def plot_counts(df):
    # Drop rows with invalid datetime
    df = df.copy(deep=True).dropna(subset=['datetime'])

    # Preprocessing
    df['date'] = df['datetime'].dt.date
    df['hour'] = df['datetime'].dt.hour

    # Set Seaborn style and palette
    sns.set_style("whitegrid", {'axes.grid': False})
    colors = sns.color_palette("Set2", 2)

    # === 📆 Plot by DATE ===
    daily_counts = df.groupby(['date', 'type']).size().unstack(fill_value=0)
    daily_counts = daily_counts[daily_counts.index >= date(2025, 1, 1)]

    plt.figure(figsize=(12, 6))
    ax = plt.gca()

    daily_counts.plot(ax=ax, linewidth=2.2, marker='o', color=colors)

    ax.set_title("Photos and Videos Over Time", fontsize=16, weight='normal')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.legend(["Photos", "Videos"], fontsize=11)
    ax.grid(False)

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    plt.tight_layout()
    plt.show()

    # === ⏰ Plot by HOUR of Day ===
    hourly_counts = df.groupby(['hour', 'type']).size().unstack(fill_value=0)
    plt.figure(figsize=(10, 5))
    ax2 = plt.gca()

    hourly_counts.plot(ax=ax2, linewidth=2.2, marker='o', color=colors)

    ax2.set_title("Photos and Videos by Hour of Day", fontsize=16, weight='normal')
    ax2.set_xlabel("Hour of Day", fontsize=12)
    ax2.set_ylabel("Count", fontsize=12)
    ax2.set_xticks(range(0, 24))
    ax2.legend(["Photos", "Videos"], fontsize=11)
    ax2.grid(False)

    plt.tight_layout()
    plt.show()
