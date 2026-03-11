import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
import geodatasets
import contextily as ctx
from shapely import wkt
from streamlit_folium import st_folium


# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Crash Data Explorer",
    page_icon="💥",
    layout="wide",
)
st.title("🔥 Heat Map Visualization (Top 50)")
st.caption("Visualization of crash data on geographical map. Includes top 50 segments with highest crash rates.")


# ----------------------------
# Interactive Map
# ----------------------------

# Read only first column
df = pd.read_csv(
    "coordinatedata/coordinates.csv",
    usecols=[0],
    header=0,
    names=["WKT"]
)

# Parse WKT
df["geometry"] = df["WKT"].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

# Create map centered on mean location
m = folium.Map(
    location=[gdf.geometry.y.mean(), gdf.geometry.x.mean()],
    zoom_start=7,
    tiles="OpenStreetMap"
)

# Add points
for _, row in gdf.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5,
        color="red",
        fill=True,
        fill_opacity=0.8
    ).add_to(m)

# Display in Streamlit
st_folium(m, width=800, height=600)
