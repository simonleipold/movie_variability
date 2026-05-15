#!/usr/bin/env python3

import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
base_dir = Path("/project/3011157.03/Simon/proj_2022_CABB_movie/MRI")

subjectlist_file = base_dir / "subjectlist_hcp7T.csv"
behavior_file = base_dir / "HCP_YA_subjects_2026_04_17_10_00_29.csv"
output_file = base_dir / "subjectlist_hcp7T_personality.csv"

# ------------------------------------------------------------------
# Load data
# ------------------------------------------------------------------
subjectlist = pd.read_csv(subjectlist_file)
behavior = pd.read_csv(behavior_file)

# Make sure IDs have the same type
subjectlist["PID"] = subjectlist["PID"].astype(str)
behavior["Subject"] = behavior["Subject"].astype(str)

# ------------------------------------------------------------------
# Keep only behavioral rows for subjects in the subject list
# ------------------------------------------------------------------
behavior_subset = behavior[behavior["Subject"].isin(subjectlist["PID"])].copy()

# keep the same order as in the subject list
behavior_subset = subjectlist.merge(
    behavior_subset,
    left_on="PID",
    right_on="Subject",
    how="left"
)

# drop duplicated ID column from subjectlist
behavior_subset = behavior_subset.drop(columns=["Subject"])

# ------------------------------------------------------------------
# Save
# ------------------------------------------------------------------
behavior_subset.to_csv(output_file, index=False)
