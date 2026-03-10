import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
import geodatasets
import contextily as ctx
import altair as alt

@st.cache_data
def load_data(path, geo=False):
    if(geo):
        return gpd.read_file(path)
    return pd.read_csv(path)

@st.cache_data
def prep_crash_data(df):
    df = df.merge(df_sev, left_on="SEVERITY", right_on="ID", how="left")
    df = df.merge(df_rc, left_on="FUNC_CLS", right_on="ID", how="left")
    df["urban"] = df["urban"].astype('category')
    df["label"] = np.where(df["urban"] == 1, "Urban", "Rural")
    return df

@st.cache_data
def prep_agg_data(df, cols, indexName, roadclass=False):
    if roadclass:
        df["DISPLAY"] = np.where(
            df["ROAD_CLASS_DESC_FULL"].isin([" Urban-Interstate", " Urban-Principal-Arterial (Freeways & Expressways)"]),
            "Urban-Interstate & Principal-Arterial",
            df["ROAD_CLASS_DESC_FULL"]
        )
    new_df = df.groupby(cols).size().reset_index(name=indexName)
    return new_df

# Load data
df_crashes = load_data("clean_data/crashes.csv")
df_3mile = load_data("clean_data/3milesegments.csv")
df_roads = load_data("clean_data/roads.csv")
df_vehicles = load_data("clean_data/vehicles.csv")

# Data code descriptions
df_sev = load_data("clean_data/SEVERITY.csv")
df_rc = load_data("clean_data/ROAD_CLASS.csv")

# Merge
df_crashes_roads = df_crashes.merge(df_roads, on=["RTE_NBR", "BEGMP", "ENDMP"], how="left")

# Prep crash data
df_crashes_roads = prep_crash_data(df_crashes_roads)

# Split crashes into urban
df_crashes_urban = df_crashes_roads[df_crashes_roads["urban"] == 1]
df_crashes_rural = df_crashes_roads[df_crashes_roads["urban"] == 0]

agg_sev_urban = prep_agg_data(df_crashes_urban, ['SEVERITY', 'Severity'], 'count')
agg_sev_rural = prep_agg_data(df_crashes_rural, ['SEVERITY', 'Severity'], 'count')
agg_road_class = prep_agg_data(df_crashes_roads, ['DISPLAY'], 'count', roadclass=True)
agg_urban_rural = prep_agg_data(df_crashes_roads, ['label'], 'count')

# Add proportions
agg_road_class["proportion"] = (
    agg_road_class["count"] / agg_road_class["count"].sum()
)
agg_sev_urban["proportion"] = (
    agg_sev_urban["count"] / agg_sev_urban["count"].sum()
)
agg_sev_rural["proportion"] = (
    agg_sev_rural["count"] / agg_sev_rural["count"].sum()
)
agg_urban_rural["proportion"] = (
    agg_urban_rural["count"] / agg_urban_rural["count"].sum()
)


# Rename columns
agg_urban_rural = agg_urban_rural.rename(
    columns={
        "label" : "Urban/Rural",
        "count" : "Total # of Crashes"
    }
)
# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Crash Data Explorer",
    page_icon="💥",
    layout="wide",
)
st.title("Most Dangerous Routes")

# ----------------------------
# Get Top 5
# ---------------------------
df_top5 = df_3mile.nlargest(5, "CRASHRATE")[["RTE_NBR", 'BIN_START', 'BIN_END', "CRASH_COUNT", "CRASHRATE"]]
df_top5