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


def prep_crash_data(df_crashes):
    df_crashes = df_crashes.merge(df_sev, left_on="SEVERITY", right_on="ID", how="left")
    df_crashes = df_crashes.merge(df_rc, left_on="FUNC_CLS", right_on="ID", how="left")
    df_crashes["urban"] = df_crashes["urban"].astype('category')
    return df_crashes

@st.cache_data
def prep_agg_data(df, cols, indexName):
    return df.groupby(cols).size().reset_index(name=indexName)

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
df_crash_sev_urban = df_3mile[df_3mile["URBAN"] == 1]

agg_sev_urban = prep_agg_data(df_crashes_urban, ['SEVERITY', 'Severity'], 'count')
agg_road_class = prep_agg_data(df_crashes_urban, ['FUNC_CLS', 'ROAD_CLASS_DESC'], 'count')

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Crash Data Explorer",
    page_icon="💥",
    layout="wide",
)
st.title("🏢 Urban Crash data")
st.caption("Detailed data on crashes in urban areas.")

# ----------------------------
# General Stats
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

total_crashes = len(df_crashes_urban)
avg_crash_rate = float(df_crash_sev_urban["CRASHRATE"].mean())
peak_row = df_3mile.loc[df_crash_sev_urban["CRASHRATE"].idxmax()]
highest_crash_road_class = agg_road_class.loc[agg_road_class["count"].idxmax()]

col1.metric("Total Urban Crashes", f"{total_crashes:,}")  # https://docs.streamlit.io/develop/api-reference/data/st.metric
col2.metric("Avg Urban Crash Rate in 3 Mile Segment", f"{avg_crash_rate:.2f}")
col3.metric(
    "Highest Crash Rate in 3 Mile Segment",
    f"{int(peak_row['CRASHRATE']):,}"
)
col4.metric(highest_crash_road_class["ROAD_CLASS_DESC"],
            f"{int(highest_crash_road_class["count"])}",
            help="Road type w/highest # of crashes"            
)
# ----------------------------
# Data Summary
# ----------------------------
st.subheader("# of Crashes by Road Class")
st.bar_chart(
    data=agg_road_class,
    x="ROAD_CLASS_DESC",
    y="count",
    horizontal=True,
    x_label="# of Crashes",
    y_label="Road Class"
)

st.subheader("# of Crashes by Crash Severity")
st.bar_chart(
    data=agg_sev_urban,
    x="Severity",
    y="count",
    horizontal=True,
    y_label="Severity Class",
    x_label="# of Crashes"
)

st.subheader("# of Crashes by Crash Severity (Excluding minor severities)")
st.bar_chart(
    data=agg_sev_urban.loc[~agg_sev_urban["SEVERITY"].isin([0,1])],
    x="Severity",
    y="count",
    horizontal=True,
    y_label="Severity Class",
    x_label="# of Crashes"
)
st.table(
    agg_sev_urban,
    border=True
    )


