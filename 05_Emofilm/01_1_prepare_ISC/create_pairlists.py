#!/usr/bin/env python3
import os
import pandas as pd
from itertools import combinations

# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = "/project/3011157.03/Simon/proj_2022_CABB_movie"
subjlist_path = os.path.join(projpath, "MRI", "subjectlist_emofilm_personality.csv")

out_dir = os.path.join(projpath, "MRI")

out_file_upper = os.path.join(out_dir, "all_pair_list_emofilm.csv")
out_file_both = os.path.join(out_dir, "all_pair_list_with_reverse_emofilm.csv")

# ------------------------------------------------------------------
# load subject IDs
# ------------------------------------------------------------------
subjlist = pd.read_csv(subjlist_path, dtype=str)
subjects = subjlist["PID"].tolist()

# ------------------------------------------------------------------
# upper triangle (exclude diagonal)
# ------------------------------------------------------------------
pairs_upper = list(combinations(subjects, 2))

pd.DataFrame(pairs_upper, columns=["Subject1", "Subject2"]).to_csv(
    out_file_upper, index=False
)

# ------------------------------------------------------------------
# upper + lower triangle (exclude diagonal)
# ------------------------------------------------------------------
pairs_both = (
    [(s1, s2) for s1, s2 in pairs_upper] +
    [(s2, s1) for s1, s2 in pairs_upper]
)

pd.DataFrame(pairs_both, columns=["Subject1", "Subject2"]).to_csv(
    out_file_both, index=False
)

print(f"Saved: {out_file_upper}")
print(f"Saved: {out_file_both}")