
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

    ### Background & Motivation
    While there has been a great deal of study into the differences in crash rates and outcomes between 
    urban and rural locations, we find that relatively little has been published that delves further into 
    the impact of roadway type within these two classes or the geographical relation between them. With the 
    high number of crashes on Washington state highways available through the HSIS dataset it is intended 
    for this to provide sufficient characterization information to be generally applicable as an expansion 
    upon existing literature, particularly as to data regarding injurious and fatal crashes.
    
    As is widely supported by existing literature, there is a strong relationship between urban road 
    conditions and VMT-adjusted crash volumes but a negative relationship with fatality crash rates. 
    (Zwerling et al 2005). This can be attributed to a variety of contributing factors such as roadway 
    speeds, design, lighting, and lane width in rural areas. (Kauffmann 2024). Therefore we would expect 
    to see the greatest number of crashes on the most travelled roadways - namely interstate highways 
    through urban areas such as I-5 through Seattle or I-90 through Bellevue. We also hypothesize that the 
    urban context has higher crash rates than the rural context but rural areas have more severe crashes 
    than urban areas.

    ### Group Members
    Ashley Carle, Alex Cheriel, Dante Shorana, Niraj Mali
"""
)