#!/usr/bin/env python
"""
Format significant Schaefer IS-RSA results.

This script reads the IS-RSA output CSVs, joins Schaefer parcel labels,
filters for FWE-significant parcels, and saves formatted result tables.
"""

import os
import pandas as pd


# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
proj_path = "/project/3011157.03/Simon/proj_2022_CABB_movie"

main_out_dir = os.path.join(
    proj_path,
    "Scripts",
    "MovVar_ImagNeuro_Revision01",
    "CABB_Schaefer",
)

r_path = os.path.join(main_out_dir, "r_output_isrsa")

out_dir = os.path.join(r_path, "formatted")
if not os.path.exists(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print("Directory %s created" % out_dir)


# ------------------------------------------------------------------
# Schaefer labels
# ------------------------------------------------------------------
labels_csv = os.path.join(
    proj_path,
    "MRI",
    "Schaefer_atlas",
    "Schaefer2018_300Parcels_17Networks_order_FSLMNI152_2mm_labels.tsv",
)

labels_df = pd.read_csv(labels_csv, sep="\t")

labels_df = labels_df[
    [
        "one_based",
        "label",
        "Yeo_17_network",
    ]
]


# ------------------------------------------------------------------
# files to format
# ------------------------------------------------------------------
task_flist = [
    "ISRSA_features_post_",
]

movie_list = [
    "movie1",
    "movie2",
    "movie3",
    "movie4",
    "movie5",
    "movie6",
    "movie7",
    "movie8",
]


# ------------------------------------------------------------------
# format significant results
# ------------------------------------------------------------------
for task in task_flist:
    for movie in movie_list:
        
        print(task)
        print(movie)
        
        input_file = os.path.join(r_path, task + movie + ".csv")
        
        if not os.path.exists(input_file):
            print("File not found: %s" % input_file)
            continue
        
        tmp_df = pd.read_csv(input_file)
        
        # Remove existing label columns if they are already present
        # to avoid duplicated columns after merging.
        tmp_df = tmp_df.drop(
            columns=[
                "label",
                "Yeo_17_network",
            ],
            errors="ignore",
        )
        
        tmp_df["Parcel"] = tmp_df["Parcel"].astype(int)
        
        merged_df = pd.merge(
            tmp_df,
            labels_df,
            left_on="Parcel",
            right_on="one_based",
            how="left",
        )
        
        columns_order = [
            "Parcel",
            "label",
            "Yeo_17_network",
            "estimate",
            "statistic",
            "pval",
            "pvalFDR",
            "pvalFWE",
        ]
        
        merged_df = merged_df[columns_order]
        
        filtered_df = merged_df[merged_df["pvalFWE"] < 0.05]
        
        output_file = os.path.join(out_dir, task + movie + ".csv")
        filtered_df.to_csv(output_file, index=False)

print("\nFinished formatting significant Schaefer IS-RSA results.")