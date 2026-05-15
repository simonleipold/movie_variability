#!/usr/bin/env python3
import os
import pandas as pd
import math

# ------------------------------------------------------------------
# Create participant-wise movie timing files for Emofilm
# based on events.tsv files
# Onset and Offset are saved as TR indices
# ------------------------------------------------------------------

# base BIDS directory
base_path = "/project/3011157.03/ds004892"

# task list
tasks_path = "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/tasks_emofilm.tsv"

# output directory
out_dir = "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/TimingsEmofilmMovies"
os.makedirs(out_dir, exist_ok=True)

# repetition time
TR = 1.3

# ------------------------------------------------------------------
# Load task list
# ------------------------------------------------------------------
tasks_df = pd.read_csv(tasks_path, sep="\t")

# remove accidental duplicates if any
tasks_df = tasks_df.drop_duplicates(subset=["subject", "session", "task"])

# ------------------------------------------------------------------
# Create timing file for each participant
# ------------------------------------------------------------------
for subj in tasks_df["subject"].unique():

    subj_df = tasks_df[tasks_df["subject"] == subj].copy()
    subj_df = subj_df.sort_values(["session", "task"])

    rows = []
    movie_nr = 1

    for _, row in subj_df.iterrows():
        ses = row["session"]
        movie = row["task"]

        event_file = os.path.join(
            base_path,
            subj,
            ses,
            "func",
            f"{subj}_{ses}_task-scan_acq-{movie}_events.tsv"
        )

        if not os.path.exists(event_file):
            print(f"Missing events file: {event_file}")
            continue

        df = pd.read_csv(event_file, sep="\t")

        film_df = df[df["trial_type"] == "film"].copy()

        if len(film_df) == 0:
            print(f"No film row found in: {event_file}")
            continue

        if len(film_df) > 1:
            print(f"Warning: multiple film rows found in {event_file}; using first one.")

        onset_sec = float(film_df.iloc[0]["onset"])
        duration_sec = float(film_df.iloc[0]["duration"])
        offset_sec = onset_sec + duration_sec

        # convert seconds to TR indices
        onset_tr = int(round(onset_sec / TR))
        offset_tr = int(round(offset_sec / TR))

        rows.append({
            "MovieNr": movie_nr,
            "Session": ses,
            "Movie": movie,
            "Onset": onset_tr,
            "Offset": offset_tr
        })

        movie_nr += 1

    out_file = os.path.join(out_dir, f"{subj}_movie_timing.csv")
    out_df = pd.DataFrame(rows, columns=["MovieNr", "Session", "Movie", "Onset", "Offset"])
    out_df.to_csv(out_file, index=False)

    print(f"Saved: {out_file}")