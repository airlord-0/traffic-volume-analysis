import requests
import pandas as pd
import folium
from folium.plugins import HeatMap
import time
import os

# ============= CONFIG =============
API_KEY = os.get("api_key")  # TomTom API key

# Bengaluru bounding box (lat_min, lon_min, lat_max, lon_max)
BBOX = [12.85, 77.45, 13.10, 77.75]
GRID_STEP = 0.02  # ~2 km spacing for grid

# ==================================


def get_traffic_flow(lat, lon):
    """Fetch traffic flow data from TomTom for given coordinates"""
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    params = {"point": f"{lat},{lon}", "key": API_KEY}

    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()["flowSegmentData"]
        return {
            "lat": lat,
            "lon": lon,
            "currentSpeed": data["currentSpeed"],
            "freeFlowSpeed": data["freeFlowSpeed"],
            "congestionIndex": round(
                (data["freeFlowSpeed"] - data["currentSpeed"])
                / data["freeFlowSpeed"],
                2,
            ),
        }
    else:
        return None


def generate_grid(bbox, step):
    """Generate lat/lon grid inside bounding box"""
    lat_min, lon_min, lat_max, lon_max = bbox
    lat_points = []
    lon_points = []
    lat = lat_min
    while lat <= lat_max:
        lon = lon_min
        while lon <= lon_max:
            lat_points.append(lat)
            lon_points.append(lon)
            lon += step
        lat += step
    return list(zip(lat_points, lon_points))


def collect_traffic_data():
    """Collect traffic data for grid"""
    points = generate_grid(BBOX, GRID_STEP)
    records = []
    for lat, lon in points:
        data = get_traffic_flow(lat, lon)
        if data:
            records.append(data)
        time.sleep(0.2)  # avoid rate limit
    return pd.DataFrame(records)


def build_heatmap(df, filename="bengaluru_traffic.html"):
    """Build folium heatmap from traffic data"""
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=11)

    # Weight by congestion index (0=free, 1=bad congestion)
    heat_data = [
        [row["lat"], row["lon"], row["congestionIndex"]] for _, row in df.iterrows()
    ]
    HeatMap(heat_data, radius=15, max_zoom=13).add_to(m)

    m.save(filename)
    print(f"✅ Heatmap saved to {filename}")


# ============= RUN =============
if __name__ == "__main__":
    df = collect_traffic_data()
    print(df.head())  # preview
    build_heatmap(df)

    
    
    



