# Movie Variability

This repository contains Python and R code accompanying a manuscript on variability between movies in inter-subject correlation (ISC) values and its consequences.

The code is organized into the main ISC and IS-RSA analyses, control analyses, and replication analyses using the HCP 7T movie-watching and Emofilm datasets.

## Main Folders

| Folder | Description |
| --- | --- |
| [`01_ISC`](01_ISC/) | Main ISC workflow: mask creation, time-series extraction, ISC matrices, movie comparisons, and ANOVA visualization. |
| [`02_IS-RSA`](02_IS-RSA/) | Main IS-RSA workflow: neural, behavioral, and control matrices; model fitting; visualization; formatting; map correlations; and feature-score diagnostics. |
| [`03_control_analyses`](03_control_analyses/) | Control analyses for equal movie length, Schaefer atlas parcellation, head motion, tSNR, multivariate classification, model covariates, random movie effects, and resampling. |
| [`04_HCP_movie-watching`](04_HCP_movie-watching/) | ISC/ANOVA and IS-RSA workflows for the HCP 7T movie-watching dataset. |
| [`05_Emofilm`](05_Emofilm/) | ISC/ANOVA and IS-RSA workflows for the Emofilm dataset. |

## Detailed Workflows

Detailed script orders are documented in the analysis-specific READMEs:

- [`01_ISC/README.md`](01_ISC/README.md)
- [`02_IS-RSA/README.md`](02_IS-RSA/README.md)
- [`03_control_analyses/equal_length/README.md`](03_control_analyses/equal_length/README.md)
- [`03_control_analyses/Schaefer_atlas/README.md`](03_control_analyses/Schaefer_atlas/README.md)
- [`03_control_analyses/headmotion/README.md`](03_control_analyses/headmotion/README.md)
- [`03_control_analyses/tSNR/README.md`](03_control_analyses/tSNR/README.md)
- [`04_HCP_movie-watching/README.md`](04_HCP_movie-watching/README.md)
- [`05_Emofilm/README.md`](05_Emofilm/README.md)
