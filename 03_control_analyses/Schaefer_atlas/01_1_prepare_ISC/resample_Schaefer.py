#!/usr/bin/env python3
from pathlib import Path
import csv
import shutil
import numpy as np
import nibabel as nib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nilearn import datasets, plotting
from nilearn.image import load_img, resample_to_img


# ------------------------------------------------------------------
# settings
# ------------------------------------------------------------------
N_ROIS = 300
YEO_NETWORKS = 17
RESOLUTION_MM = 2

# ------------------------------------------------------------------
# paths
# ------------------------------------------------------------------
projpath = Path("/project/3011157.03/Simon/proj_2022_CABB_movie/MRI")

brainnetome_atlas = (
    projpath
    / "Brainnetome_atlas"
    / "BN_Atlas_210_cortical_2mm.nii.gz"
)

out_dir = projpath / "Schaefer_atlas"
out_dir.mkdir(parents=True, exist_ok=True)

basename = f"Schaefer2018_{N_ROIS}Parcels_{YEO_NETWORKS}Networks_order_FSLMNI152_{RESOLUTION_MM}mm"

schaefer_orig_out = out_dir / f"{basename}.nii.gz"
schaefer_resampled_out = out_dir / f"{basename}_space-BNAtlas.nii.gz"
labels_out = out_dir / f"{basename}_labels.tsv"

qc_plot_out = out_dir / f"QC_{basename}_resampling.png"
qc_report_out = out_dir / f"QC_{basename}_resampling.txt"


# ------------------------------------------------------------------
# helper functions
# ------------------------------------------------------------------
def extract_yeo_network(label: str) -> str:
    """
    Extract Schaefer/Yeo network name.

    Example:
    17Networks_LH_DefaultA_PFCd_1 -> DefaultA
    17Networks_RH_SomMotB_Aud_1   -> SomMotB
    """
    if label.lower() == "background":
        return "Background"

    parts = label.split("_")

    if len(parts) >= 3 and parts[1] in {"LH", "RH"}:
        return parts[2]

    return "NA"


def resample_nearest_compatible(source_img, target_img):
    """
    Wrapper for compatibility across Nilearn versions.
    """
    try:
        return resample_to_img(
            source_img,
            target_img,
            interpolation="nearest",
            force_resample=True,
            copy_header=True,
        )
    except TypeError:
        try:
            return resample_to_img(
                source_img,
                target_img,
                interpolation="nearest",
                force_resample=True,
            )
        except TypeError:
            return resample_to_img(
                source_img,
                target_img,
                interpolation="nearest",
            )


# ------------------------------------------------------------------
# fetch Schaefer atlas: 300 parcels, 2 mm MNI, 17 Yeo networks
# ------------------------------------------------------------------
schaefer = datasets.fetch_atlas_schaefer_2018(
    n_rois=N_ROIS,
    yeo_networks=YEO_NETWORKS,
    resolution_mm=RESOLUTION_MM,
    data_dir=str(out_dir),
)


# ------------------------------------------------------------------
# save original atlas
# ------------------------------------------------------------------
shutil.copyfile(schaefer.maps, schaefer_orig_out)


# ------------------------------------------------------------------
# save labels
# ------------------------------------------------------------------
labels = [
    label.decode("utf-8") if isinstance(label, bytes) else str(label)
    for label in schaefer.labels
]

# Nilearn versions differ in whether "Background" is included.
if labels and labels[0].lower() == "background":
    parcel_labels = labels[1:]
else:
    parcel_labels = labels

if len(parcel_labels) != N_ROIS:
    print(f"WARNING: Expected {N_ROIS} parcel labels, found {len(parcel_labels)}")

with labels_out.open("w", newline="") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["zero_based", "one_based", "label", "Yeo_17_network"])

    for zero_based, label in enumerate(parcel_labels):
        one_based = zero_based + 1
        yeo_network = extract_yeo_network(label)

        writer.writerow([
            zero_based,
            one_based,
            label,
            yeo_network,
        ])


# ------------------------------------------------------------------
# resample Schaefer atlas to Brainnetome 2 mm atlas grid
# ------------------------------------------------------------------
schaefer_img = load_img(schaefer_orig_out)
brainnetome_img = load_img(brainnetome_atlas)

schaefer_resampled = resample_nearest_compatible(
    schaefer_img,
    brainnetome_img,
)

# Keep atlas labels as integers after nearest-neighbor resampling.
resampled_data = np.rint(schaefer_resampled.get_fdata()).astype(np.int16)

schaefer_resampled_int = nib.Nifti1Image(
    resampled_data,
    affine=brainnetome_img.affine,
    header=brainnetome_img.header.copy(),
)
schaefer_resampled_int.header.set_data_dtype(np.int16)
schaefer_resampled_int.to_filename(schaefer_resampled_out)


# ------------------------------------------------------------------
# QC checks
# ------------------------------------------------------------------
expected_ids = set(range(1, len(parcel_labels) + 1))
resampled_ids = set(int(x) for x in np.unique(resampled_data) if x != 0)

missing_ids = sorted(expected_ids - resampled_ids)
unexpected_ids = sorted(resampled_ids - expected_ids)

with qc_report_out.open("w") as f:
    f.write("Schaefer atlas resampling QC\n")
    f.write("============================\n\n")

    f.write(f"Original Schaefer atlas: {schaefer_orig_out}\n")
    f.write(f"Resampled Schaefer atlas: {schaefer_resampled_out}\n")
    f.write(f"Reference Brainnetome atlas: {brainnetome_atlas}\n\n")

    f.write("Shape check\n")
    f.write("-----------\n")
    f.write(f"Original Schaefer shape:  {schaefer_img.shape}\n")
    f.write(f"Brainnetome shape:       {brainnetome_img.shape}\n")
    f.write(f"Resampled shape:         {schaefer_resampled_int.shape}\n\n")

    f.write("Affine check\n")
    f.write("------------\n")
    f.write("Brainnetome affine:\n")
    f.write(f"{brainnetome_img.affine}\n\n")
    f.write("Resampled affine:\n")
    f.write(f"{schaefer_resampled_int.affine}\n\n")

    f.write("Parcel ID check\n")
    f.write("---------------\n")
    f.write(f"Expected number of parcel IDs: {len(expected_ids)}\n")
    f.write(f"Found number of parcel IDs:    {len(resampled_ids)}\n")
    f.write(f"Missing parcel IDs:            {missing_ids}\n")
    f.write(f"Unexpected parcel IDs:         {unexpected_ids}\n")


# ------------------------------------------------------------------
# QC plot: original vs resampled atlas
# ------------------------------------------------------------------
try:
    bg_img = datasets.load_mni152_template(resolution=2)
except TypeError:
    bg_img = datasets.load_mni152_template()

fig = plt.figure(figsize=(16, 7))

plotting.plot_roi(
    schaefer_img,
    bg_img=bg_img,
    display_mode="z",
    cut_coords=[-32, -16, 0, 16, 32, 48],
    title="Original Schaefer atlas",
    figure=fig,
    axes=(0.02, 0.08, 0.46, 0.84),
    draw_cross=False,
    annotate=True,
)

plotting.plot_roi(
    schaefer_resampled_int,
    bg_img=bg_img,
    display_mode="z",
    cut_coords=[-32, -16, 0, 16, 32, 48],
    title="Resampled to Brainnetome grid",
    figure=fig,
    axes=(0.52, 0.08, 0.46, 0.84),
    draw_cross=False,
    annotate=True,
)

fig.savefig(qc_plot_out, dpi=300, bbox_inches="tight")
plt.close(fig)


# ------------------------------------------------------------------
# print summary
# ------------------------------------------------------------------
print(f"Saved original Schaefer atlas:   {schaefer_orig_out}")
print(f"Saved resampled Schaefer atlas: {schaefer_resampled_out}")
print(f"Saved Schaefer labels:          {labels_out}")
print(f"Saved QC plot:                  {qc_plot_out}")
print(f"Saved QC report:                {qc_report_out}")

if missing_ids:
    print(f"WARNING: Missing parcel IDs after resampling: {missing_ids}")
else:
    print("QC passed: all expected Schaefer parcel IDs are present after resampling.")