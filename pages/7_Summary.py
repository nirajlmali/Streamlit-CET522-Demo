
import streamlit as st
# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Crash Data Explorer",
    page_icon="💥",
    layout="wide",
)
st.title("Project Summary")

st.sidebar.success("Select a demo above.")

st.markdown(
"""
Our results match what would be expected for a comparison between urban and rural 
crash volumes and rates, with the major exception of State Route 99. The majority of the 
50 most dangerous segments of state highway in Washington do follow the pattern of 
occurring in rural areas. Those that do not, such as on State Route 99 and State 
Route 7, would require further investigation to determine contributing factors.
"""
)