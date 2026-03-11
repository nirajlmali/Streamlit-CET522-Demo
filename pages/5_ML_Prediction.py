
import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Crash Data Explorer",
    page_icon="💥",
    layout="wide",
)
st.title("Machine Learning ")

st.sidebar.success("Select a demo above.")

st.markdown(
"""
Machine learning exploration using sklearn library.

### Method: Random Forest Classifier
"Random Forest is an ensemble machine learning algorithm that builds multiple decision trees 
and combines their predictions to improve accuracy and reduce overfitting. In 
Scikit‑learn, the Random Forest Classifier is widely used for classification tasks 
because it handles large datasets and handles nonlinear relationships well."

More info: https://www.geeksforgeeks.org/random-forest-classifier-using-scikit-learn/

### Limitations
In order to include all crashes, we omitted joining it with the vehicles table, due to
certain crashes not having an associate record in that table, leaving out some crashes.
This may be an issue with data cleaning or with the dataset itself. Having the 
attributes of the vehicles and drivers may help this mode be more robust.
"""
)

# ----------------------------
# Methods
# ----------------------------

@st.cache_data
def load_data(path):
    return pd.read_csv(path)

df_crashes = load_data("clean_data/crashes.csv")
df_veh = load_data("clean_data/vehicles.csv")
df_roads = load_data("clean_data/roads.csv")
# df = df_veh.merge(df_crashes, on="CASENO", how="left")
df = df_crashes.merge(df_roads, on=["RTE_NBR", "BEGMP", "ENDMP"])

df
def ml_process(features, target):

    status.write("Starting ML process...")
    progress.progress(5)
    st.subheader("Feature Columns:")
    st.write(features)
    X = df[features]
    y = df[target]

    # First split: 70% train, 30% temp
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )

    # Second split: 15% validation, 15% test
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
    )

    categorical_master = [
        "ACCTYPE1", "LIGHT", "RDSURF", "DRV_AGE",
        "CONTRIB1", "VEHTYPE", "NO_LANES"
    ]

    numeric_master = ["NUMVEHS", "BEGMP", "ENDMP", "AADT"]

    categorical_cols = [c for c in categorical_master if c in features]
    numeric_cols = [c for c in numeric_master if c in features]


    status.write("Preprocessing Data...")
    progress.progress(20)
    preprocess = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", "passthrough", numeric_cols)
        ]
    )

    model = RandomForestClassifier(
        n_estimators=600,
        max_depth=20,
        random_state=42,
        class_weight="balanced"
    )


    status.write("Creating Pipeline...")
    progress.progress(40)
    clf = Pipeline(steps=[
        ("preprocess", preprocess),
        ("model", model)
    ])


    status.write("Fitting model...")
    progress.progress(60)
    clf.fit(X_train, y_train)


    status.write("Reporting Results...")
    progress.progress(80)
    y_val_pred = clf.predict(X_val)
    st.subheader("VALIDATION RESULTS")
    st.text(classification_report(y_val, y_val_pred))

    y_test_pred = clf.predict(X_test)
    st.subheader("TEST RESULTS")
    st.text(classification_report(y_test, y_test_pred))

    # Extract one-hot encoded feature names
    ohe = clf.named_steps["preprocess"].named_transformers_["cat"]
    ohe_features = ohe.get_feature_names_out(categorical_cols)

    # Combine with numeric features
    all_features = np.concatenate([ohe_features, numeric_cols])

    # Extract importances
    importances = clf.named_steps["model"].feature_importances_

    feature_importance_df = pd.DataFrame({
        "feature": all_features,
        "importance": importances
    }).sort_values("importance", ascending=False)

    st.subheader("FEATURE IMPORTANCE")
    st.write(feature_importance_df.head(20))

    status.write("Complete!")
    progress.progress(100)


all_features = [
        "ACCTYPE1", "LIGHT", "NUMVEHS", "RDSURF", 
        # "DRV_AGE", "CONTRIB1", "VEHTYPE", 
        "BEGMP", "ENDMP", "AADT", "NO_LANES"
    ]
# --- Widgets always visible ---
features = st.multiselect(
    label="Select Features to use in ML",
    options=all_features,
    key="fts"
)

target = st.selectbox(
    label="Select target",
    options=["urban","SEVERITY"]
)

run_ml = st.button("Run ML Program")
run_ml_all_features = st.button("Run ML Program w/All Features")

# --- Run ML only when button is clicked ---
progress = st.progress(0)
status = st.empty()


if run_ml:
    ml_process(features, target)

if run_ml_all_features:
    ml_process(all_features, target)

