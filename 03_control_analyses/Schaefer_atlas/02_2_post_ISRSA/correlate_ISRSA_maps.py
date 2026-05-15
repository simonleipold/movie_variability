#!/usr/bin/env python3
"""
Compute pairwise correlations between movie-specific IS-RSA statistic maps.

Uses Schaefer 2018 300-parcel IS-RSA output files.
"""

from pathlib import Path
import pandas as pd
import re
from itertools import combinations


# ------------------------------------------------------------------
# Input/output directories
# ------------------------------------------------------------------
in_dir = Path(
    "/project/3011157.03/Simon/proj_2022_CABB_movie/"
    "Scripts/MovVar_ImagNeuro_Revision01/CABB_Schaefer/r_output_isrsa"
)

out_dir = in_dir / "correlations"
out_dir.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------
# Output files
# ------------------------------------------------------------------
corr_file = out_dir / "pairwise_statistic_correlations.csv"
summary_file = out_dir / "pairwise_statistic_correlations_summary.csv"


# ------------------------------------------------------------------
# Collect all matching CSV files
# ------------------------------------------------------------------
csv_files = list(in_dir.glob("ISRSA_features_post_movie*.csv"))

if not csv_files:
    raise FileNotFoundError(f"No matching CSV files found in {in_dir}")


# ------------------------------------------------------------------
# Helper: extract movie number
# ------------------------------------------------------------------
def extract_movie_number(path):
    m = re.search(r"movie(\d+)", path.stem)
    return int(m.group(1)) if m else float("inf")


csv_files = sorted(csv_files, key=extract_movie_number)


# ------------------------------------------------------------------
# Read movie-specific IS-RSA statistic maps
# ------------------------------------------------------------------
movie_data = {}

for f in csv_files:
    movie_num = extract_movie_number(f)
    movie_name = f"movie{movie_num}"

    df = pd.read_csv(f)

    if "statistic" not in df.columns:
        raise ValueError(f"'statistic' column not found in {f.name}")
    if "Parcel" not in df.columns:
        raise ValueError(f"'Parcel' column not found in {f.name}")

    df = df[["Parcel", "statistic"]].copy()
    df["Parcel"] = df["Parcel"].astype(int)
    df = df.sort_values("Parcel").reset_index(drop=True)

    if len(df) != 300:
        print(f"WARNING: Expected 300 parcels, found {len(df)} in {f.name}")

    movie_data[movie_name] = df


# ------------------------------------------------------------------
# Compute all pairwise Pearson correlations
# ------------------------------------------------------------------
results = []

for movie_x, movie_y in combinations(movie_data.keys(), 2):
    df_x = movie_data[movie_x].rename(columns={"statistic": "stat_x"})
    df_y = movie_data[movie_y].rename(columns={"statistic": "stat_y"})

    merged = pd.merge(df_x, df_y, on="Parcel", how="inner")

    if len(merged) != 300:
        print(
            f"WARNING: Expected 300 shared parcels for {movie_x} vs {movie_y}, "
            f"found {len(merged)}"
        )

    corr = merged["stat_x"].corr(merged["stat_y"], method="pearson")

    results.append({
        "Movie_x": movie_x,
        "Movie_y": movie_y,
        "Corr": corr
    })


# ------------------------------------------------------------------
# Save pairwise correlations
# ------------------------------------------------------------------
results_df = pd.DataFrame(results)
results_df.to_csv(corr_file, index=False)


# ------------------------------------------------------------------
# Save summary
# ------------------------------------------------------------------
summary_df = pd.DataFrame([{
    "Mean_Corr": results_df["Corr"].mean(),
    "SD_Corr": results_df["Corr"].std(),
    "Min_Corr": results_df["Corr"].min(),
    "Max_Corr": results_df["Corr"].max(),
    "N_Comparisons": len(results_df)
}])

summary_df.to_csv(summary_file, index=False)


# ------------------------------------------------------------------
# Print summary
# ------------------------------------------------------------------
print(f"Saved pairwise correlations to: {corr_file}")
print(f"Saved summary to: {summary_file}")
print(
    f"Mean correlation: {summary_df.loc[0, 'Mean_Corr']:.4f} "
    f"+/- {summary_df.loc[0, 'SD_Corr']:.4f}"
)