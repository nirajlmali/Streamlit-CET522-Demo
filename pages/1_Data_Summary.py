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
st.title("📝Data Summary")
st.caption("What are the different ways we can compare crashes on urban vs rural roadways?")

# ----------------------------
# Sidebar controls
# ----------------------------
st.sidebar.header("Filters")


# ----------------------------
# General Stats
# ----------------------------
st.subheader("Crash Statistics for all WA Interstate and Arterial Road Types")
col1, col2, col3, col4 = st.columns(4)

total_crashes = len(df_crashes_roads)
avg_crash_rate = float(df_3mile["CRASHRATE"].mean())
peak_row = df_3mile.loc[df_3mile["CRASHRATE"].idxmax()]
highest_crash_road_class = agg_road_class.loc[agg_road_class["count"].idxmax()]

col1.metric("Total Crashes", f"{total_crashes:,}")  # https://docs.streamlit.io/develop/api-reference/data/st.metric
col2.metric("Avg Crash Rate in 3 mi Segment", f"{avg_crash_rate:.2f}")
col3.metric(
    "Highest Crash Rate (3 mi segment):",
    f"{int(peak_row['CRASHRATE']):,}",
    help="Route No. "f"{peak_row['RTE_NBR'].astype(int)}"
)
col4.metric("Highest Crash Total (Single State Route)",
            f"{int(highest_crash_road_class["count"])}",
            help="Type: " + highest_crash_road_class["DISPLAY"]            
)

# ----------------------------
# Data Summary
# ----------------------------
st.subheader("Urban vs Rural: Crash Statistics Comparison")
def distribution_plots(option):
    if option == "Crashes by Road Type":
        if prop_toggle:  
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
            st.bar_chart(
                data=agg_road_class,
                x="DISPLAY",
                y="count",
                horizontal=True,
                x_label="# of Crashes",
                y_label="Road Class"
            )
        st.table(
            agg_road_class[["DISPLAY", "count", "proportion"]],
            border=True
            )
    
    elif option == "Severity":
        if prop_toggle:  
            chart = (
                alt.Chart(agg_sev_urban.loc[~agg_sev_urban["SEVERITY"].isin([0,1])])
                .mark_bar()
                .encode(
                    x=alt.X("proportion:Q", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
                    y=alt.Y("Severity:N", title="Severity Class"),
                    tooltip=["Severity", "proportion"]
                )
            )
            chart2 = (
                alt.Chart(agg_sev_rural.loc[~agg_sev_rural["SEVERITY"].isin([0,1])],)
                .mark_bar()
                .encode(
                    x=alt.X("proportion:Q", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
                    y=alt.Y("Severity:N", title="Severity Class"),
                    tooltip=["Severity", "proportion"]
                )
            )

            st.caption("Urban Crash Severity (Proportions)")
            st.altair_chart(chart, use_container_width=True)
            st.caption("Rural Crash Severity (Proportions)")
            st.altair_chart(chart2, use_container_width=True)
        else:
            st.caption("Urban Crash Severity (Totals)")
            st.bar_chart(
                data=agg_sev_urban.loc[~agg_sev_urban["SEVERITY"].isin([0,1])],
                x="Severity",
                y="count",
                horizontal=True,
                y_label="Severity Class",
                x_label="# of Crashes"
            )
            st.caption("Rural Crash Severity (Totals)")
            st.bar_chart(
                data=agg_sev_rural.loc[~agg_sev_rural["SEVERITY"].isin([0,1])],
                x="Severity",
                y="count",
                horizontal=True,
                y_label="Severity Class",
                x_label="# of Crashes"
            )     
        st.caption("Urban Crash Severity")        
        st.table(
            agg_sev_urban.loc[~agg_sev_urban["SEVERITY"].isin([0,1])],
            border=True
            )
        st.caption("Rural Crash Severity")
        st.table(
            agg_sev_rural.loc[~agg_sev_urban["SEVERITY"].isin([0,1])],
            border=True
            )
    
    else:
        if prop_toggle:  
            chart = (
                alt.Chart(agg_urban_rural)
                .mark_bar()
                .encode(
                    x=alt.X(
                            "proportion:Q", 
                            axis=alt.Axis(format="%"), 
                            scale=alt.Scale(domain=[0, 1])
                    ),
                    y=alt.Y("Urban/Rural:N", title="Urban or Rural"),
                    tooltip=["Urban/Rural", "proportion"]
                )
            )
            st.caption("Urban vs Rural (Proportional Comparison)")
            st.altair_chart(chart, use_container_width=True)
        else:
            st.caption("Urban vs Rural (Total Comparison)")
            st.bar_chart(
                data=agg_urban_rural,
                x="Urban/Rural",
                y="Total # of Crashes",
                horizontal=True,
                y_label="Urban or Rural",
                x_label="# of Crashes"
            )
        st.caption("Urban vs Rural Crashes")
        st.table(
            agg_urban_rural,
            border=True
            )


# ----------------------------
# Distributions
# ----------------------------
options = ["Urban vs Rural (Totals)", 
        "Crashes by Road Type", 
        "Severity"
        ]
option = st.selectbox(
    label="View distributions by...",
    options=options
    )
prop_toggle = st.toggle("View By Proportion")
distribution_plots(option)
