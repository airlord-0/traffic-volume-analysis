🚦 Bengaluru Traffic Analysis

This project uses TomTom’s Traffic API to collect real-time traffic flow data for Bengaluru.
It generates both:
	•	A Heatmap (to visualize congestion intensity across the city)
	•	A Graph (to compare congestion levels across grid points)

⸻

📌 Objectives
	•	Identify congestion hotspots in Bengaluru during peak hours.
	•	Build a heatmap of city traffic flow in real time.
	•	Visualize congestion using both maps and graphs.

⸻

set up and installation
1. clone my repo- git clone https://github.com/yourusername/traffic-analysis.git
   cd traffic-analysis
2. install dependencies
   1.pandas, 2.requests, 3.folium, 4.os, 5.load.env 6.matplotlib
3.create a .env file in your project's root and inside it hide your api key as such : key="your api key"


running the script 
* python traffic_volume_analysis.py
  this will :
  This will:
	1.	Fetch live traffic data from TomTom API.
	2.	Generate a heatmap saved as bengaluru_traffic.html.
	3.	Show a matplotlib graph comparing congestion levels across grid points.

📊 Outputs
	•	Heatmap: Visualizes congestion (0 = free flow, 1 = heavy congestion).
	•	Graph: Bar chart comparing congestion indices across grid points.

  
🛠 Tech Stack
	•	Python → Data collection & processing
	•	Pandas → Data handling
	•	Folium → Interactive heatmap
	•	Matplotlib → Graph plotting
	•	dotenv → Secure API key management
