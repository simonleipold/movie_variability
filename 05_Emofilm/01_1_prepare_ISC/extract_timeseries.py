#!/usr/bin/env python3
import os
import pandas as pd
import matplotlib.pyplot as plt

from nltools.data import Brain_Data
from nltools.mask import expand_mask
from nilearn import plotting as nplot

import warnings
warnings.filterwarnings("ignore")  # suppress warnings

# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------

# main project directory
projpath = '/project/3011157.03/Simon/proj_2022_CABB_movie/MRI'
print('The main project directory is located here: %s' % projpath)

# Emofilm dataset
prep_dir = '/project/3011157.03/ds004892/derivatives/preprocessing'

# subject list
subjlist = pd.read_csv(
    os.path.join(projpath, 'subjectlist_emofilm_personality.csv'),
    dtype=object
)

# task list
tasks_df = pd.read_csv(
    os.path.join(projpath, 'tasks_emofilm.tsv'),
    sep='\t',
    dtype=object
)

# directory with participant-wise timing files created earlier
timing_dir = os.path.join(projpath, 'TimingsEmofilmMovies')

# group mask
mask_path = os.path.join(projpath, 'groupmask_movies_emofilm.nii.gz')

# ------------------------------------------------------------------
# Fixed alphabetical mapping from movie name to movie1 ... movie14
# ------------------------------------------------------------------

movie_map = {
    'AfterTheRain': 'movie1',
    'BetweenViewings': 'movie2',
    'BigBuckBunny': 'movie3',
    'Chatter': 'movie4',
    'FirstBite': 'movie5',
    'LessonLearned': 'movie6',
    'Payload': 'movie7',
    'Sintel': 'movie8',
    'Spaceman': 'movie9',
    'Superhero': 'movie10',
    'TearsOfSteel': 'movie11',
    'TheSecretNumber': 'movie12',
    'ToClaireFromSonny': 'movie13',
    'YouAgain': 'movie14'
}

# ------------------------------------------------------------------
# Load atlas
# ------------------------------------------------------------------

mask_name = 'Brainnetome'
brainnetome_path = os.path.join(
    projpath, 'Brainnetome_atlas', 'BN_Atlas_210_cortical_2mm.nii.gz'
)

mask = Brain_Data(brainnetome_path, mask=mask_path)
mask_x = expand_mask(mask)

# ------------------------------------------------------------------
# Output directory
# ------------------------------------------------------------------

dir_out = os.path.join(projpath, 'Emofilm_ROI_timeseries')
if not os.path.exists(dir_out):
    os.makedirs(dir_out)
    print('Dir %s created ' % dir_out)

# optional atlas plot
plot_atlas = True
if plot_atlas:
    nplot.plot_roi(
        mask.to_nifti(),
        title='%s Parcellation' % mask_name
    )
    plt.savefig(os.path.join(dir_out, 'CorticalParcels_%s.png' % mask_name))
    plt.close()

# ------------------------------------------------------------------
# Extract average activation from atlas and save to csv
# using participant-specific timing files to slice the BOLD data
# ------------------------------------------------------------------

extract_csv = True

if extract_csv:
    for subj in subjlist['PID']:
        print(f'Processing {subj}')

        # load participant-specific timing file
        timing_file = os.path.join(timing_dir, f'{subj}_movie_timing.csv')
        if not os.path.exists(timing_file):
            print(f'Missing timing file: {timing_file}')
            continue

        timing_df = pd.read_csv(timing_file, dtype={'Session': str, 'Movie': str})

        # all subject-specific task rows
        subj_tasks = tasks_df[tasks_df['subject'] == subj].copy()

        for _, row in subj_tasks.iterrows():
            ses = row['session']
            task = row['task']

            if task not in movie_map:
                print(f'Skipping unknown task: {task}')
                continue

            scan = movie_map[task]

            # find timing row for this subject/session/movie
            timing_row = timing_df[
                (timing_df['Session'] == ses) &
                (timing_df['Movie'] == task)
            ]

            if len(timing_row) == 0:
                print(f'No timing information for {subj}, {ses}, {task}')
                continue

            onset = int(timing_row.iloc[0]['Onset'])
            offset = int(timing_row.iloc[0]['Offset'])

            bold_file = os.path.join(
                prep_dir,
                subj,
                ses,
                'func',
                f'{subj}_{ses}_task-{task}_space-MNI_desc-ppres_bold.nii.gz'
            )

            if not os.path.exists(bold_file):
                print(f'Missing file: {bold_file}')
                continue

            print(f'Loading {bold_file}')
            data = Brain_Data(bold_file, mask=mask_path)

            # slice movie segment using TR-based indices
            data_movie = data[onset:offset]

            # extract average ROI timeseries
            roi = data_movie.extract_roi(mask)

            out_file = os.path.join(
                dir_out,
                f'{subj}_{scan}_Average_ROI.csv'
            )

            pd.DataFrame(roi.T).to_csv(out_file, index=False)
            print(f'Saved {out_file}')