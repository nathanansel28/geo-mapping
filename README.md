# 🌍 Geo-Mapping

## Overview

**Geo-Mapping** is a Python-based project that extracts GPS metadata from JPEG images and visualizes their locations on interactive maps using [Folium](https://python-visualization.github.io/folium/). The project supports two main functionalities:

1. **Simple Photo Mapping** – Places each GPS-tagged photo as a red dot on a map, limited to European coordinates.
2. **City Bubble Mapping** – Clusters photos by proximity to European cities and draws bubble markers indicating photo density.

Useful for photographers, travelers, or anyone interested in visualizing the geographical spread of their image collections.

---

## Features

* Extracts GPS coordinates (latitude, longitude, altitude) from image EXIF data
* Filters out non-European photos
* Identifies nearest major cities within 50km
* Creates:

  * **Photo dot map** (`europe_image_map.html`)
  * **City bubble map** (`city_bubbles_map.html`)
* Outputs are saved as interactive HTML maps

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/geo-mapping.git
cd geo-mapping
```

### 2. Install Dependencies

Make sure you have Python 3.8+ installed. Then run:

```bash
pip install -r requirements.txt
```


### 3. Download City Shapefile

Ensure you have the shapefile `ne_10m_populated_places.shp` from [Natural Earth](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/) placed in the `assets/` directory:

```
geo-mapping/
├── assets/
│   └── ne_10m_populated_places.shp
```

Make sure all related files (.dbf, .shx, etc.) are also in the same folder.

---

## How to Use

### 1. Generate a Basic Photo Map

```python
from map import map_photos

map_photos(["/path/to/your/image_folder"])
```

Output: `europe_image_map.html`

### 2. Generate a City Bubble Map

```python
from map import map_photos_with_bubbles

map_photos_with_bubbles(["/path/to/your/image_folder"])
```

Output: `city_bubbles_map.html`

> ✅ You can pass multiple folders as a list of paths.

---


## License

This project is open source and free to use under the [MIT License](LICENSE).
