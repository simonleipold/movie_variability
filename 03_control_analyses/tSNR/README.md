# tSNR Control Analysis

This control analysis evaluates the relationship between ISC variability, ISC level, and parcel-wise temporal signal-to-noise ratio (tSNR).

Run the scripts in the following order.

| Step | Script | Notes |
| --- | --- | --- |
| 1 | `get_tSNR_values.py` | Extract movie- and parcel-wise tSNR values, create tSNR maps, and save group summaries. Submit to the cluster with `submit_get_tSNR_values.py`. |
| 2 | `isc_tSNR_2026_04_30.R` | Run the ISC/tSNR control analysis, including parcel-wise ISC ANOVAs and partial correlations controlling for tSNR. |
