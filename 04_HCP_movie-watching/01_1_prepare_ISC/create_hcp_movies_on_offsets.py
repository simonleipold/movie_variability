#!/usr/bin/env python3
import os
import pandas as pd

out_dir = "/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/TimingsHPC7TMovies"
os.makedirs(out_dir, exist_ok=True)

movie_names = {
    "1.1": "Two_Men",
    "1.2": "Welcome_To_Bridgeville",
    "1.3": "Pockets",
    "1.4": "Inside_the_Human_Body",
    "1.5": "Vimeo_Repeat",
    "2.1": "Inception_1",
    "2.2": "Social_Network_1",
    "2.3": "Ocean's_Eleven_1",
    "2.4": "Vimeo_Repeat",
    "3.1": "Off_The_Shelf",
    "3.2": "1212",
    "3.3": "Mrs_Meyers_Clean_Day",
    "3.4": "Northwest_Passage",
    "3.5": "Vimeo_Repeat",
    "4.1": "Home_Alone_1",
    "4.2": "Erin_Brockovich_2",
    "4.3": "Empire_Strikes_Back_1",
    "4.4": "Vimeo_Repeat",
}

movie_timings = {
    "MOVIE1": [
        ("0",0,19.9583),("1.1",20,264.0417),("0",264.0833,284.0417),
        ("1.2",284.0833,505.7083),("0",505.75,525.7083),
        ("1.3",525.75,713.75),("0",713.7917,733.75),
        ("1.4",733.7917,797.5417),("0",797.5833,817.5417),
        ("1.5",817.5833,900.9583),("0",901,920.9583),
    ],
    "MOVIE2": [
        ("0",0,19.9583),("2.1",20,246.7083),("0",246.75,266.7083),
        ("2.2",266.75,525.3333),("0",525.375,545.3333),
        ("2.3",545.375,794.5833),("0",794.625,814.5417),
        ("2.4",814.5833,897.9583),("0",898,917.9583),
    ],
    "MOVIE3": [
        ("0",0,19.9583),("3.1",20,200.5417),("0",200.5833,220.5417),
        ("3.2",220.5833,405.0833),("0",405.125,425.0833),
        ("3.3",425.125,629.2083),("0",629.25,649.2083),
        ("3.4",649.25,791.75),("0",791.7917,811.5417),
        ("3.5",811.5833,894.9583),("0",895,914.9583),
    ],
    "MOVIE4": [
        ("0",0,19.9583),("4.1",20,252.2917),("0",252.3333,272.2917),
        ("4.2",272.3333,502.1667),("0",502.2083,522.1667),
        ("4.3",522.2083,777.375),("0",777.4167,797.5417),
        ("4.4",797.5833,880.9583),("0",881,900.9583),
    ],
}

movie_nr = 1

for movie_run, timing_rows in movie_timings.items():

    rows = []

    for block_id, onset, offset in timing_rows:

        if block_id == "0":
            continue

        movie = movie_names[block_id]

        if movie == "Vimeo_Repeat":
            continue

        rows.append({
            "MovieNr": movie_nr,
            "Movie": movie,
            "Onset": onset,
            "Offset": offset
        })

        movie_nr += 1

    df = pd.DataFrame(rows, columns=["MovieNr","Movie","Onset","Offset"])

    out_file = os.path.join(out_dir, f"hpc7T_{movie_run}_timing.csv")
    df.to_csv(out_file, index=False)

    print(f"Saved: {out_file}")