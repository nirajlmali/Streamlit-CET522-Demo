
import streamlit as st
# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Crash Data Explorer",
    page_icon="💥",
    layout="wide",
)
st.title("📊Dataset and Data Plan")

st.sidebar.success("Select a demo above.")

st.markdown(
"""
### Dataset
For this project, we used the HSIS dataset, a comprehensive record of crashes in Washington in 2002. 
The original dataset included three spreadsheets that included a comprehensive list of attributes for the 
accident itself, the road it occurred on, and the vehicles involved. From this dataset, we parsed out the data we needed and 
mapped it into an ER Diagram.

## Database Overview
One table was created based on values calculate from the other tables: 3milesegment. This table
grouped segments on the same routes into 3 mile bins and stores the total number of crashes and
a calculated crash rate described in Appendix A of this page. Due to overlap of some route and 
milepost combinations being in two bins at once, the team determined to have this table have no
relationships between other tables and act as its own entity. In the future, it would be ideal to 
be able to establish a relationship 3milesegment and roads tables.
"""
)

st.image("images/ERDiagram.png")

st.markdown(
"""
### Schema
The ER Diagram was then converted into a schema below. We chose to maintain CSV format for storage 
and reading of the data itself, but the structure is maintained.

| Table | Primary Key | Attributes |
|-------|-------------|------------|
| Crashes | CASENO | MILEPOST, SEVERITY, ACCTYPE1, LIGHT, NUMVEHS, RDSURF, RTE_NBR, BEGMP, ENDMP |
| Roads | RTE_NBR, BEGMP, ENDMP | AADT, NO_LANES, FUNC_CLS, urban |
| Vehicles | CASENO | VEHNO, DRV_AGE, CONTRIB1, VEHTYPE |
| Severity | ID | Severity |
| Road_Class | ID | ROAD_CLASS_DESC | ROAD_CLASS_DESC_FULL |
| 3milesegments | RTE_NBR, BIN_START, BIN_END | AADT_WT, CRASH_COUNT, CRASHRATE |

### Limitations
Creating a relationship between 3milesegment and Roads tables proved to be too complex due to
bins having some road segments overlap between bins. For this study, 3milesegment was used
independently of all other tables, so we proceeded with analysis. However, a more robust design
would need to be used in a practical application.

### Appendix A
Data cleaning:
- The original Road file included extra overlapping control segments for every road in addition to the principal segments. The extra segments were deleted.
- We created 3-mile bins for each road (MP 0-3, 3-6, etc). Overlapping roadway segments were split between two bins.
- Partial bins (less than 3 miles) at the end of routes were deleted to maintain uniform segment length.
- We calculated a weighted AADT for each bin based on the AADT of contributing segments.
- Each bin was classified as Urban or Rural based on the classifications of contributing segments.
- Crashes for each 3-mile bin were calculated from the cleaned crash dataset and merged to the new dataset using the MILEPOST and RTE_NBR variables.
- Crash rates were calculated using the following equation.

$R =(C*100,000,000)/(V*365*N*L)$

Where:
- R = Crash rate for the road segment per 100 million vehicle-miles of travel
- C = Total number of crashes in the study period
- V = Traffic volumes using Average Annual Daily Traffic (AADT) volumes
- N = Number of years of data = 1 (all data is from 2002)
- L = Length of the roadway segment in miles

This produced a cleaned dataset of 2,337 three-mile roadway segments and associated crash rates:

"""


)
