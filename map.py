from typing import Tuple, Union, List

from PIL import Image
from collections import defaultdict
from datetime import datetime
from folium import CircleMarker, Map, Marker, DivIcon
from shapely.geometry import Point

import os
import piexif
import folium
import geopandas as gpd
import numpy as np
import piexif


def extract_gps_data(
    image_path: str
) -> Union[Tuple[float, float, float], None]:
    """For a given image, return a tuple of the latitude, longitude, and altitude, if geodata is avaialble. Else return None."""
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


def is_in_europe(lat, lon):
    return (35 <= lat <= 71) and (-25 <= lon <= 45)


def map_photos(
    folder_paths: List[str], output_file='europe_image_map.html'
) -> None:
    """Plots each photo as a dot on the map."""
    if isinstance(folder_paths, str):
        folder_paths = [folder_paths]

    markers = []

    for folder_path in folder_paths:
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('jpg', 'jpeg')):
                full_path = os.path.join(folder_path, filename)
                gps = extract_gps_data(full_path)
                if gps:
                    lat, lon, _ = gps
                    if is_in_europe(lat, lon):
                        markers.append((lat, lon, filename))

    if not markers:
        print("No images with valid GPS data in Europe.")
        return

    avg_lat = sum(lat for lat, lon, _ in markers) / len(markers)
    avg_lon = sum(lon for lat, lon, _ in markers) / len(markers)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4, tiles='CartoDB positron')

    for lat, lon, filename in markers:
        folium.CircleMarker(
            location=(lat, lon),
            radius=5,
            color='red',
            fill=True,
            fill_opacity=0.7,
            popup=filename
        ).add_to(m)

    m.save(output_file)
    print(f"Interactive map saved to {output_file}")


city_shapes = gpd.read_file("assets/ne_10m_populated_places.shp").to_crs("EPSG:4326")
city_shapes_europe = city_shapes[
    city_shapes.geometry.apply(lambda geom: is_in_europe(geom.y, geom.x))
]


def find_city(lat, lon, max_distance_km=50):
    if not is_in_europe(lat, lon):
        return None

    photo_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs("EPSG:3035").iloc[0]
    cities_proj = city_shapes_europe.copy().to_crs("EPSG:3035")

    cities_proj["distance"] = cities_proj.geometry.distance(photo_point)
    nearest_city = cities_proj.sort_values("distance").iloc[0]

    if nearest_city["distance"] <= max_distance_km * 1000:
        return nearest_city["NAMEASCII"]

    return None


def map_photos_with_bubbles(
    folder_paths, output_file='city_bubbles_map.html'
) -> None:
    if isinstance(folder_paths, str):
        folder_paths = [folder_paths]

    city_data = defaultdict(lambda: {"count": 0, "coords": []})

    for folder in folder_paths:
        for filename in os.listdir(folder):
            if filename.lower().endswith(('jpg', 'jpeg')):
                full_path = os.path.join(folder, filename)

                gps = extract_gps_data(full_path)
                if not gps:
                    continue 

                lat, lon, _ = gps
                city = find_city(lat, lon)

                if city:
                    city_data[city]["count"] += 1
                    city_data[city]["coords"].append((lat, lon))

    if not city_data:
        print("No valid GPS-tagged photos found.")
        return

    m = Map(location=[54, 15], zoom_start=4, tiles="CartoDB positron")
    bubble_color = "#4a90e2"

    for city, data in city_data.items():
        lats, lons = zip(*data["coords"])
        center_lat = sum(lats) / len(lats)
        center_lon = sum(lons) / len(lons)
        count = data["count"]
        radius = 10 + 2 * np.log1p(count)

        CircleMarker(
            location=(center_lat, center_lon),
            radius=radius,
            color=bubble_color,
            fill=True,
            fill_color=bubble_color,
            fill_opacity=0.7,
            popup=f"{city} ({count} photo{'s' if count > 1 else ''})",
            tooltip=city
        ).add_to(m)

        Marker(
            location=(center_lat, center_lon),
            icon=DivIcon(html=f"""<div style="font-size: 10px; font-weight:bold;">{city}</div>""")
        ).add_to(m)

    m.save(output_file)
    print(f"Map saved: {output_file}")
