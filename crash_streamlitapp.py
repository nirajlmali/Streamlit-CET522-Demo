import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
df_crashes = pd.read_csv("clean_data/crashes.csv")
df_3mile = pd.read_csv("clean_data/3milesegments.csv")

# Data code descriptions
df_sev = pd.read_csv("clean_data/SEVERITY.csv")

# join
df_crashes = df_crashes.merge(df_sev, left_on="SEVERITY", right_on="ID", how="left")

# Split crashes into urban
df_crashes_urban = df_crashes[df_crashes["urban"] == 1]
df_crashes_rural = df_crashes[df_crashes["urban"] == 0]

agg_sev_urban = df_crashes_urban.groupby(['SEVERITY', 'Severity']).size().reset_index(name='count')
agg_sev_rural = df_crashes_rural.groupby(['SEVERITY', 'Severity']).size().reset_index(name='count')

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Crash Data Explorer",
    page_icon="💥",
    layout="wide",
)

names = agg_sev_urban["Severity"]

plt.figure(figsize=(14, 6))

plt.subplot(211) # one row, three columns, plot on first row first column (?)
plt.barh(names, agg_sev_urban["count"])
plt.subplot(212) # one row, three columns, plot on second (?) and etc.
plt.barh(names, agg_sev_rural["count"])