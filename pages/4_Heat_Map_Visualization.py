import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
import geodatasets
import contextily as ctx

@st.cache_data
def load_data(path, geo=False):
    if(geo):
        return gpd.read_file(path)
    return pd.read_csv(path)

@st.cache_data
def prep_crash_data(df_crashes):
    df_crashes = df_crashes.merge(df_sev, left_on="SEVERITY", right_on="ID", how="left")
    df_crashes = df_crashes.merge(df_rc, left_on="FUNC_CLS", right_on="ID", how="left")
    df_crashes["urban"] = df_crashes["urban"].astype('category')
    return df_crashes

@st.cache_data
def prep_agg_data(df, cols, indexName):
    return df.groupby(cols).size().reset_index(name=indexName)

@st.cache_data
def prep_mean_data(df, cols, col, indexName):
    return df.groupby(cols)[col].mean().reset_index(name=indexName)

# Geo data set
# roads = load_data("clean_data/WSDOT_-_State_Route_Linear_Referencing_System_(LRS)_Current.shp", geo=True)
# roads = roads.rename(columns={"StateRoute" : "RTE_NBR"})
# roads.columns

# Load data
df_crashes = load_data("clean_data/crashes.csv")
df_3mile = load_data("clean_data/3milesegments.csv")

# Data code descriptions
df_sev = load_data("clean_data/SEVERITY.csv")
df_rc = load_data("clean_data/ROAD_CLASS.csv")

# Prep crash data
df_crashes = prep_crash_data(df_crashes)

# Split crashes into urban
df_crashes_urban = df_crashes[df_crashes["urban"] == 1]
df_crashes_rural = df_crashes[df_crashes["urban"] == 0]

# means
means_crash_rates = prep_mean_data(df_3mile, ["RTE_NBR"], "CRASHRATE", "mean")
means_crash_rates
# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Crash Data Explorer",
    page_icon="💥",
    layout="wide",
)
st.title("🔥 Heat Map Visualization")
st.caption("Visualization of crash data on geographical map.")

# ----------------------------
# Additional Methods
# ----------------------------
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge, unary_union

def force_single_linestring(g):
    """
    Convert any geometry into a single LineString.
    Handles LineString, MultiLineString, and GeometryCollection.
    """
    # Case 1: already a LineString
    if isinstance(g, LineString):
        return g
    
    # Case 2: MultiLineString → stitch pieces together
    if isinstance(g, MultiLineString):
        parts = list(g.geoms)  # <-- FIX: use .geoms, not list(g)
        parts_sorted = sorted(parts, key=lambda ls: ls.coords[0])
        
        coords = []
        for part in parts_sorted:
            coords.extend(part.coords)
        
        return LineString(coords)
    
    # Case 3: GeometryCollection or other weird cases
    try:
        merged = linemerge(unary_union(g))
        if isinstance(merged, LineString):
            return merged
        if isinstance(merged, MultiLineString):
            return force_single_linestring(merged)
    except:
        pass
    
    return None


# ----------------------------
# Page config
# ----------------------------
# 1. Load centerline
import geopandas as gpd

# ArcGIS FeatureServer endpoint (common format for WSDOT datasets)

gdf = gpd.read_file("clean_data/WSDOT_-_State_Route_(1%3A500K)_Current.shp")

gdf
print(gdf.columns)

route_rates = (
    gdf.groupby(route_col)[crash_col]
    .mean()
    .reset_index()
)

gdf = gdf.merge(route_rates, on=route_col, suffixes=("", "_route_mean"))