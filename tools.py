import os
import folium
import piexif
from PIL import Image

def get_decimal_from_dms(dms, ref):
    degrees, minutes, seconds = dms
    decimal = degrees[0]/degrees[1] + \
              minutes[0]/minutes[1]/60 + \
              seconds[0]/seconds[1]/3600
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def extract_gps_data(image_path):
    try:
        img = Image.open(image_path)
        exif_data = piexif.load(img.info['exif'])

        gps_data = exif_data.get("GPS")
        if not gps_data:
            return None

        lat = get_decimal_from_dms(gps_data[piexif.GPSIFD.GPSLatitude], gps_data[piexif.GPSIFD.GPSLatitudeRef].decode())
        lon = get_decimal_from_dms(gps_data[piexif.GPSIFD.GPSLongitude], gps_data[piexif.GPSIFD.GPSLongitudeRef].decode())

        alt = None
        if piexif.GPSIFD.GPSAltitude in gps_data:
            alt_val = gps_data[piexif.GPSIFD.GPSAltitude]
            alt = alt_val[0] / alt_val[1]

        return lat, lon, alt
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return None

def map_images(folder_path, output_file='photo_map.html'):
    markers = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('jpg', 'jpeg')):
            full_path = os.path.join(folder_path, filename)
            gps = extract_gps_data(full_path)
            if gps:
                lat, lon, alt = gps
                popup = f"{filename}<br>Lat: {lat:.6f}<br>Lon: {lon:.6f}"
                if alt:
                    popup += f"<br>Altitude: {alt:.2f} m"
                markers.append((lat, lon, popup))

    if not markers:
        print("No images with valid GPS data found.")
        return

    photo_map = folium.Map(location=[markers[0][0], markers[0][1]], zoom_start=12)

    for lat, lon, popup in markers:
        folium.Marker([lat, lon], popup=popup).add_to(photo_map)

    photo_map.save(output_file)
    print(f"Map saved to {output_file}")

# Example usage
map_images("assets")
