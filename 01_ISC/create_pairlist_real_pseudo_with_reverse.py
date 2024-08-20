# Create a list of all possible pairs of participants,
# and indicate if the pair is real or pseudo based on the real pair list.
import pandas as pd
from itertools import combinations, permutations

# Load the CSV file containing real pairs
real_pairs_df = pd.read_csv("/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/real_pair_list.csv")

# Extract participants from the PairID column and generate all possible pairs
participants = set()
real_pairs_df['PairID'].apply(lambda x: participants.update(x.split('_')))
all_possible_pairs = list(permutations(sorted(participants), 2))  # Use permutations to get reverse pairs as well

# Create a dataframe for all pairs
all_pairs_df = pd.DataFrame(all_possible_pairs, columns=['Subject1', 'Subject2'])

# Define a function to determine pair type
def determine_pair_type(row, real_pairs, reverse_pairs):
    pair = f"{row['Subject1']}_{row['Subject2']}"
    reverse_pair = f"{row['Subject2']}_{row['Subject1']}"
    if pair in real_pairs or reverse_pair in real_pairs:
        return 'Real'
    return 'Pseudo'

# Add a column to indicate if the pair is real or pseudo
all_pairs_df['Pair_Type'] = all_pairs_df.apply(
    determine_pair_type, 
    args=(set(real_pairs_df['PairID']), set(real_pairs_df['PairID'])), 
    axis=1
)

# Sort the dataframe: first by 'Pair_Type' to place 'Real' first, then by 'Subject1' and 'Subject2'
all_pairs_df = all_pairs_df.sort_values(by=['Pair_Type', 'Subject1', 'Subject2'], ascending=[False, True, True])

# Save the sorted dataframe to a CSV file
all_pairs_df.to_csv('/project/3011157.03/Simon/proj_2022_CABB_movie/MRI/all_pair_list_with_reverse.csv', index=False)

