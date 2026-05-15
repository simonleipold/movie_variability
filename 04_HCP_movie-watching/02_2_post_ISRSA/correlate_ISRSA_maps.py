#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
import re
from itertools import combinations

# Input/output directories
in_dir = Path("/project/3011157.03/Simon/proj_2022_CABB_movie/Scripts/MovVar_ImagNeuro_Revision01/HCP_movie-watching/r_output_ISRSA")
out_dir = in_dir / "correlations"
out_dir.mkdir(parents=True, exist_ok=True)

# Output files
corr_file = out_dir / "pairwise_statistic_correlations.csv"
summary_file = out_dir / "pairwise_statistic_correlations_summary.csv"

# Collect all matching csv files
csv_files = list(in_dir.glob("ISRSA_personality_movie*.csv"))

if not csv_files:
    raise FileNotFoundError(f"No matching CSV files found in {in_dir}")

# Extract movie number for sorting/naming
def extract_movie_number(path):
    m = re.search(r"movie(\d+)", path.stem)
    return int(m.group(1)) if m else float("inf")

csv_files = sorted(csv_files, key=extract_movie_number)

# Read in data
movie_data = {}
for f in csv_files:
    movie_num = extract_movie_number(f)
    movie_name = f"movie{movie_num}"

    df = pd.read_csv(f)

    if "statistic" not in df.columns:
        raise ValueError(f"'statistic' column not found in {f.name}")
    if "Parcel" not in df.columns:
        raise ValueError(f"'Parcel' column not found in {f.name}")

    movie_data[movie_name] = df[["Parcel", "statistic"]].copy()

# Compute all pairwise Pearson correlations
results = []

for movie_x, movie_y in combinations(movie_data.keys(), 2):
    df_x = movie_data[movie_x].rename(columns={"statistic": "stat_x"})
    df_y = movie_data[movie_y].rename(columns={"statistic": "stat_y"})

    merged = pd.merge(df_x, df_y, on="Parcel", how="inner")

    corr = merged["stat_x"].corr(merged["stat_y"], method="pearson")

    results.append({
        "Movie_x": movie_x,
        "Movie_y": movie_y,
        "Corr": corr
    })

# Save pairwise correlations
results_df = pd.DataFrame(results)
results_df.to_csv(corr_file, index=False)

# Compute and save summary
mean_corr = results_df["Corr"].mean()
sd_corr = results_df["Corr"].std()

summary_df = pd.DataFrame([{
    "Mean_Corr": mean_corr,
    "SD_Corr": sd_corr
}])
summary_df.to_csv(summary_file, index=False)

# Print summary
print(f"Saved pairwise correlations to: {corr_file}")
print(f"Saved summary to: {summary_file}")
print(f"Mean correlation: {mean_corr:.4f} +/- {sd_corr:.4f}")