import requests
import pandas as pd
import folium
from folium.plugins import HeatMap
import time
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from datetime import datetime

# configure the api key (we have used TOMTOM api key)
load_dotenv()
API_KEY = os.getenv("key")   # make sure .env has key=YOUR_TOMTOM_API_KEY

BBOX = [12.85, 77.45, 13.10, 77.75]  # Bengaluru bounding box
GRID_STEP = 0.05  # ~5 km spacing
OUTPUT_HTML = "bengaluru_traffic.html"
LOG_FILE = "traffic_log.csv"

# all functions

def get_traffic_flow(lat, lon):
    """Fetch traffic flow data from TomTom for given coordinates"""
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    params = {"point": f"{lat},{lon}", "key": API_KEY}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()["flowSegmentData"]
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "lat": lat,
            "lon": lon,
            "currentSpeed": data["currentSpeed"],
            "freeFlowSpeed": data["freeFlowSpeed"],
            "congestionIndex": round(
                (data["freeFlowSpeed"] - data["currentSpeed"]) / max(data["freeFlowSpeed"], 1),
                2,
            ),
        }
    else:
        return None

def generate_grid(bbox, step):
    """Generate lat/lon grid inside bounding box"""
    lat_min, lon_min, lat_max, lon_max = bbox
    lat_points, lon_points = [], []
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

def log_data(df):
    """Append data to CSV log"""
    if not os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, index=False)
    else:
        df.to_csv(LOG_FILE, mode="a", header=False, index=False)
    print(f"📁 Data logged to {LOG_FILE}")

def build_heatmap(df, filename=OUTPUT_HTML):
    """Build folium heatmap from traffic data"""
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=11)
    heat_data = [
        [row["lat"], row["lon"], row["congestionIndex"] * 5]  # scaled for visibility
        for _, row in df.iterrows()
    ]
    HeatMap(heat_data, radius=15, max_zoom=13).add_to(m)
    m.save(filename)
    print(f"✅ Heatmap saved to {filename}")

def build_bar_graph(df):
    """Build bar graph of top congested points"""
    top_hotspots = df.sort_values("congestionIndex", ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    plt.bar(
        [f"({round(lat,2)}, {round(lon,2)})" for lat, lon in zip(top_hotspots["lat"], top_hotspots["lon"])],
        top_hotspots["congestionIndex"],
        color="red",
    )
    plt.title("Top 10 Congestion Hotspots (Bengaluru)")
    plt.xlabel("Location (lat, lon)")
    plt.ylabel("Congestion Index (0=Free, 1=Severe)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def build_time_trend(location=None):
    """Build line chart of congestion over time"""
    df_log = pd.read_csv(LOG_FILE)
    if df_log.empty:
        print("⚠️ No log data found yet.")
        return

    if location:
        # Filter for specific lat/lon
        lat, lon = location
        df_loc = df_log[(df_log["lat"] == lat) & (df_log["lon"] == lon)]
        plt.plot(df_loc["timestamp"], df_loc["congestionIndex"], marker="o", label=f"{lat},{lon}")
        plt.title(f"Congestion Trend at ({lat},{lon})")
    else:
        # Average congestion across city
        df_avg = df_log.groupby("timestamp")["congestionIndex"].mean().reset_index()
        plt.plot(df_avg["timestamp"], df_avg["congestionIndex"], marker="o", label="City Avg")
        plt.title("Average Citywide Congestion Trend")

    plt.xlabel("Time")
    plt.ylabel("Congestion Index")
    plt.xticks(rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.show()

# run the code
if __name__ == "__main__":
    df = collect_traffic_data()
    print("Sample data:\n", df.head())

    if not df.empty:
        log_data(df)           # log data with timestamp
        build_heatmap(df)      # HTML heatmap
        build_bar_graph(df)    # Bar graph
        build_time_trend()     # Time trend (avg across city)
        print("🎯 Mission success: Heatmap + Graph + Time Trend ready")
    else:
        print("⚠️ No data collected. Check API key or TomTom limits.")

    
    
    



