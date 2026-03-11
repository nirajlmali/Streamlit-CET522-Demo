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
    df = df[~df["FUNC_CLS"].isin([16,17])]
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


# @st.cache_data
# def prep_agg_roadclass_data_means(df):
#     df["DISPLAY"] = np.where(
#         df["ROAD_CLASS_DESC_FULL"].isin([" Urban-Interstate", " Urban-Principal-Arterial (Freeways & Expressways)"]),
#         "Urban-Interstate & Principal-Arterial",
#         df["ROAD_CLASS_DESC_FULL"]
#     )
#     new_df = df.groupby(["FUNC_CLS", "DISPLAY"])[""].mean()
#     return new_df


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
df_crashes_rural = df_crashes_roads[df_crashes_roads["urban"] == 0]
df_crash_sev_rural = df_3mile[df_3mile["URBAN"] == 0]

agg_sev_rural = prep_agg_data(df_crashes_rural, ['SEVERITY', 'Severity'], 'count')
agg_road_class = prep_agg_data(df_crashes_roads, ['DISPLAY'], 'count', roadclass=True)

# Add proportions
agg_road_class["proportion"] = (
    agg_road_class["count"] / agg_road_class["count"].sum()
)
agg_sev_rural["proportion"] = (
    agg_sev_rural["count"] / agg_sev_rural["count"].sum()
)



# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Crash Data Explorer",
    page_icon="💥",
    layout="wide",
)
st.title("🗂️Road Classification")
st.caption("Statistical comparisons between different road classifications.")
st.markdown(
    """
    The dataset classifies roads as not just urban and rural, but also subclassifies
    those into interstate, principal arterial, and others. We chose to focus on major
    roadways shown in the table below.
    """
)
# df_rc[~df_rc["ID"].isin([6,7,9,16,17])]
agg_road_class["DISPLAY"]

# ----------------------------
# Basic Stats
# ----------------------------
# prep_agg_roadclass_data_means(df_crashes_roads)

# ----------------------------
# Data Summary
# ----------------------------
prop_toggle = st.toggle("View By Proportion")

if prop_toggle:
    st.subheader("# of Crashes by Road Class (Proportions)")
    chart = (
        alt.Chart(agg_road_class)
        .mark_bar()
        .encode(
            x=alt.X("proportion:Q", axis=alt.Axis(format="%")),
            y=alt.Y("DISPLAY:N", title="Road Class"),
            tooltip=["DISPLAY", "proportion"]
        )
    )

    st.altair_chart(chart, use_container_width=True)

else:
    st.subheader("# of Crashes by Road Class (Totals)")
    st.bar_chart(
        data=agg_road_class,
        x="DISPLAY",
        y="count",
        horizontal=True,
        x_label="# of Crashes",
        y_label="Road Class"
    )


