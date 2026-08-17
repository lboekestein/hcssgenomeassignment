# src/preprocessing.py
"""
Loads, preprocesses and saves the cleaned data
"""

from pathlib import Path

import numpy as np
import pandas as pd

# set path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed"

# -----------
# Import data
# -----------

# import raw CSV files, combine
csv_files = sorted(RAW_DATA_PATH.glob("*.csv"))

combined = []
for file in csv_files:
    df = pd.read_csv(file)
    df["direction"] = file.stem
    df["dyad"] = "_".join(sorted(file.stem.split("_")))
    combined.append(df)

combined = pd.concat(combined, ignore_index=True)

# ---------------
# Data validation
# ---------------

# combined.head()
# print(combined.shape)
# print(combined.dtypes)
# print(combined.isnull().sum().sort_values(ascending=False))

# -------------
# Preprocessing
# -------------

# fix data format
combined["event_date"] = pd.to_datetime(combined["event_date"])
combined.groupby("dyad")["event_date"].agg(["min", "max", "count"])

# check date ranges
# print(combined.groupby("dyad")["event_date"].agg(["min", "max", "count"]))

# check distribution of event types and intensity
# print(combined.groupby("event_type")["intensity"].unique())
# print(combined.groupby("quadrant")["intensity"].describe())


# map event types to PLOVER categories
plover_map = {
    "verbal_cooperation": ["CONSULT", "AGREE", "SUPPORT", "CONCEDE"],
    "material_cooperation": ["AID", "COOPERATE", "RETREAT"],
    "verbal_conflict": ["ACCUSE", "REQUEST", "THREATEN", "REJECT"],
    "material_conflict": ["ASSAULT", "SANCTION", "COERCE", "MOBILIZE", "PROTEST"],
}
event_type_to_quadrant = {
    event_type: quadrant
    for quadrant, event_types in plover_map.items()
    for event_type in event_types
}
combined["quadrant"] = combined["event_type"].map(event_type_to_quadrant)

# check value counts
# print(combined["quadrant"].value_counts())

# -----------
# Save to csv
# -----------

combined.to_csv(PROCESSED_DATA_PATH / "processed_data.csv")