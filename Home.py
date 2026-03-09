
import streamlit as st
# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Crash Data Explorer",
    page_icon="💥",
    layout="wide",
)
st.title("💥 Urban vs Rural Crashes")
st.caption("What are the different ways we can compare crashes on urban vs rural roadways?")

# ----------------------------
# Home apge text
# ----------------------------

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    This app uses HSIS crash data to answer different questions on crashes, with an overarching
    question of what differences can we spot between Urban and Rural crash data?
    **👈 View different pages showing different sets of data** 

    ### Group Members
    Ashley Carle, Alex Cheriel, Dante Shorana, Niraj Mali
"""
)