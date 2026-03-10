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
st.title("⚠️Road Classification")
st.caption("Statistical comparisons between different road classifications.")
st.markdown(
    """
    The dataset originally classified 
    """
)
st.table(df_rc[~df_rc["ID"].isin([6,7,9,16,17])])


# ----------------------------
# General Stats
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

total_crashes = len(df_crashes_rural)
avg_crash_rate = float(df_crash_sev_rural["CRASHRATE"].mean())
peak_row = df_3mile.loc[df_crash_sev_rural["CRASHRATE"].idxmax()]
highest_crash_road_class = agg_road_class.loc[agg_road_class["count"].idxmax()]

col1.metric("Total Urban Crashes", f"{total_crashes:,}")  # https://docs.streamlit.io/develop/api-reference/data/st.metric
col2.metric("Avg Urban Crash Rate in 3 Mile Segment", f"{avg_crash_rate:.2f}")
col3.metric(
    "Highest Crash Rate in 3 Mile Segment",
    f"{int(peak_row['CRASHRATE']):,}"
)
col4.metric(highest_crash_road_class["DISPLAY"],
            f"{int(highest_crash_road_class["count"])}",
            help="Road type w/highest # of crashes"            
)
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

    st.subheader("# of Crashes by Crash Severity")  
    chart2 = (
        alt.Chart(agg_sev_urban.loc[~agg_sev_urban["SEVERITY"].isin([0,1])])
        .mark_bar()
        .encode(
            x=alt.X("proportion:Q", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, .5])),
            y=alt.Y("Severity:N", title="Severity Class"),
            tooltip=["Severity", "proportion"]
        )
    )

    st.altair_chart(chart2, use_container_width=True)

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

    st.subheader("# of Crashes by Crash Severity (Totals)")
    st.bar_chart(
        data=agg_sev_rural.loc[~agg_sev_rural["SEVERITY"].isin([0,1])],
        x="Severity",
        y="count",
        horizontal=True,
        y_label="Severity Class",
        x_label="# of Crashes"
    )

st.table(
    agg_sev_rural,
    border=True
    )


