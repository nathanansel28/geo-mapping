import folium
import pandas as pd
from typing import Union
from folium import CircleMarker
from geopandas import GeoDataFrame
import geopandas as gpd
from shapely.geometry import Point
from folium import Map, CircleMarker, Marker, DivIcon
from collections import defaultdict
import numpy as np
import pandas as pd


def is_in_europe(lat, lon):
    return (35 <= lat <= 71) and (-25 <= lon <= 45)


def map_photos(
    df: pd.DataFrame, output_file: str = 'europe_image_map.html'
) -> None:
    """
    Given a DataFrame from get_media_metadata, plot photos with valid GPS in Europe.
    """
    # Filter for valid coordinates
    df_valid = df.dropna(subset=["latitude", "longitude"])
    df_valid = df_valid[df_valid.apply(lambda row: is_in_europe(row["latitude"], row["longitude"]), axis=1)]

    if df_valid.empty:
        print("No valid GPS-tagged media files in Europe.")
        return

    # Calculate center of map
    avg_lat = df_valid["latitude"].mean()
    avg_lon = df_valid["longitude"].mean()

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=4, tiles='CartoDB positron')

    for _, row in df_valid.iterrows():
        folium.CircleMarker(
            location=(row["latitude"], row["longitude"]),
            radius=5,
            color='red',
            fill=True,
            fill_opacity=0.7,
            popup=row["filename"]
        ).add_to(m)

    m.save(output_file)
    print(f"Interactive map saved to {output_file}")




# Load and filter shapefile once
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


def map_photos_with_bubbles_from_df(
    df: pd.DataFrame, output_file='city_bubbles_map.html'
) -> None:
    """Plot city bubble map using a DataFrame with lat/lon."""
    df_valid = df.dropna(subset=["latitude", "longitude"])
    df_valid = df_valid[df_valid.apply(lambda row: is_in_europe(row["latitude"], row["longitude"]), axis=1)]

    if df_valid.empty:
        print("No valid GPS-tagged media in Europe.")
        return

    city_data = defaultdict(lambda: {"count": 0, "coords": []})

    for _, row in df_valid.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        city = find_city(lat, lon)

        if city:
            city_data[city]["count"] += 1
            city_data[city]["coords"].append((lat, lon))

    if not city_data:
        print("No GPS-tagged photos matched to cities.")
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
