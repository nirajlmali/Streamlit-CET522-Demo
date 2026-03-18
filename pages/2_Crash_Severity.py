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
df_crashes_urban = df_crashes_roads[df_crashes_roads["urban"] == 1]
df_crashes_rural = df_crashes_roads[df_crashes_roads["urban"] == 0]

agg_sev_urban = prep_agg_data(df_crashes_urban, ['SEVERITY', 'Severity'], 'count')
agg_sev_rural = prep_agg_data(df_crashes_rural, ['SEVERITY', 'Severity'], 'count')
agg_road_class = prep_agg_data(df_crashes_roads, ['DISPLAY'], 'count', roadclass=True)
agg_urban_rural = prep_agg_data(df_crashes_roads, ['label'], 'count')

# remove minor crashes
agg_sev_urban = agg_sev_urban.loc[~agg_sev_urban["SEVERITY"].isin([0,1])]
agg_sev_rural = agg_sev_rural.loc[~agg_sev_rural["SEVERITY"].isin([0,1])]

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

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Crash Data Explorer",
    page_icon="💥",
    layout="wide",
)
st.title("‼️Crash Severity")
st.caption("Statistics on crash severity between Urban and Rural roads.")
st.markdown(
    """
    Crash severity describes the damage done to the individuals involved in the crashes, ranging
    from 'NO INJURY' to 'FATAL'. All possible severity descriptions are stated in the table 
    below. For our study, we chose to omit 'NOT STATED', 'NO INJURY', and 'POSSIBLE INJURY', focusing on crashes that
    caused considerable harm to the drivers and/or passengers.
    """
)
st.table(df_sev)

# ----------------------------
# General Stats
# ----------------------------
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

urban_fatal_crash_pct = agg_sev_urban.loc[agg_sev_urban["SEVERITY"] == 2, "proportion"].iloc[0] * 100
urban_fatal_crash_pct = round(urban_fatal_crash_pct, 2)
rural_fatal_crash_pct = agg_sev_rural.loc[agg_sev_rural["SEVERITY"] == 2, "proportion"].iloc[0] * 100
rural_fatal_crash_pct = round(rural_fatal_crash_pct, 2)

urban_major_crash_pct = agg_sev_urban.loc[agg_sev_urban["SEVERITY"].isin([2,5,6]), "proportion"].sum()
urban_major_crash_pct = round(urban_major_crash_pct*100, 2)
rural_major_crash_pct = agg_sev_rural.loc[agg_sev_rural["SEVERITY"].isin([2,5,6]), "proportion"].sum()
rural_major_crash_pct = round(rural_major_crash_pct*100, 2)

# avg_crash_rate = float(df_crash_sev_urban["CRASHRATE"].mean())
# peak_row = df_3mile.loc[df_crash_sev_urban["CRASHRATE"].idxmax()]
# highest_crash_road_class = agg_road_class.loc[agg_road_class["count"].idxmax()]
col1.metric("Urban Fatal Crash Percentage", f"{urban_fatal_crash_pct:,}" "%")  # https://docs.streamlit.io/develop/api-reference/data/st.metric
col2.metric("Rural Fatal Crash Percentage", f"{rural_fatal_crash_pct:,}" "%")  # https://docs.streamlit.io/develop/api-reference/data/st.metric

col1.metric("Urban Major Crash Percentage", f"{urban_major_crash_pct:,}" "%")  # https://docs.streamlit.io/develop/api-reference/data/st.metric
col2.metric("Rural Major Crash Percentage", f"{rural_major_crash_pct:,}" "%")  # https://docs.streamlit.io/develop/api-reference/data/st.metric

# ----------------------------
# Data Summary
# ----------------------------
prop_toggle = st.toggle("View By Proportion")

if prop_toggle:
    st.subheader("# of Crashes by Crash Severity (Proportions)")  
    st.caption("Urban Crash Severity Distribution")
    chart2 = (
        alt.Chart(agg_sev_urban.loc[~agg_sev_urban["SEVERITY"].isin([0,1,7])])
        .mark_bar()
        .encode(
            x=alt.X("proportion:Q", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, .3])),
            y=alt.Y("Severity:N", title="Severity Class"),
            tooltip=["Severity", "proportion"]
        )
    )

    st.altair_chart(chart2, use_container_width=True) 
    st.caption("Rural Crash Severity Distribution")
    chart2 = (
        alt.Chart(agg_sev_rural.loc[~agg_sev_rural["SEVERITY"].isin([0,1,7])])
        .mark_bar()
        .encode(
            x=alt.X("proportion:Q", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, .3])),
            y=alt.Y("Severity:N", title="Severity Class"),
            tooltip=["Severity", "proportion"]
        )
    )

    st.altair_chart(chart2, use_container_width=True)

else:
    st.subheader("# of Crashes by Crash Severity (Totals)")
    st.caption("Urban Crash Severity Distribution")
    st.bar_chart(
        data=agg_sev_urban.loc[~agg_sev_urban["SEVERITY"].isin([0,1,7])],
        x="Severity",
        y="count",
        horizontal=True,
        y_label="Severity Class",
        x_label="# of Crashes"
    )
    st.caption("Rural Crash Severity Distribution")
    st.bar_chart(
        data=agg_sev_rural.loc[~agg_sev_rural["SEVERITY"].isin([0,1,7])],
        x="Severity",
        y="count",
        horizontal=True,
        y_label="Severity Class",
        x_label="# of Crashes"
    )


