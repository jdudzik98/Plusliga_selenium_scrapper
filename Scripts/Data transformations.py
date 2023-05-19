import pandas as pd
import numpy as np

# read CSV file as a dataframe
batch1 = pd.read_csv('../Datasets/Matches_batch1.csv')
batch2 = pd.read_csv('../Datasets/Matches_batch2.csv')
batch3 = pd.read_csv('../Datasets/Matches_batch3.csv')
batch4 = pd.read_csv('../Datasets/Matches_batch4.csv')
batch5 = pd.read_csv('../Datasets/Matches_batch5.csv')
batch6 = pd.read_csv('../Datasets/Matches_batch6.csv')

# concatenate the dataframes
matches = pd.concat([batch1, batch2, batch3, batch4, batch5, batch6], ignore_index=True)

teams = pd.read_csv('../Scripts/teams.csv')
teams = teams.drop_duplicates(subset='MatchID', keep='first')

# drop the columns Team1_href and Team2_href
matches = matches.drop(columns=['Team1_href', 'Team2_href'])

# Merge the teams dataframe with the matches dataframe by :
matches = pd.merge(matches, teams, left_on=['MatchID'], right_on=['MatchID'], how='left', validate="m:1")

# Drop the duplicates from the matches dataframe:
matches = matches.drop_duplicates(inplace=True)

table = pd.read_csv('../Datasets/Table_standings.csv')

# Duplicate the 'Round' column:
matches['Round_original'] = matches['Round']
matches['Round'] = matches['Round'] - 1

table_host = table.rename(columns={c: c + '_table_host' for c in table.columns if c not in ['Year', 'Round', 'Team']})
table_guest = table.rename(columns={c: c + '_table_guest' for c in table.columns if c not in ['Year', 'Round', 'Team']})

merged_df = pd.merge(matches, table_host, left_on=['Year', 'Round', 'Team1_href'],
                     right_on=['Year', 'Round', 'Team'], how='left', validate="m:1")
merged_df = pd.merge(merged_df, table_guest, left_on=['Year', 'Round', 'Team2_href'],
                     right_on=['Year', 'Round', 'Team'], how='left', validate="m:1")

# Remove the redundant columns:
merged_df = merged_df.drop(columns=['Team_x', 'Team_y'])

# Extract the hour and day of week from the date:
merged_df['Date'] = pd.to_datetime(merged_df['Date'], dayfirst=True)
merged_df['Hour'] = merged_df['Date'].dt.strftime('%H:%M')
merged_df['Day_of_week'] = merged_df['Date'].dt.day_name()

# Map hour and day of week to new categories
merged_df.loc[(merged_df['Day_of_week'].isin(['Saturday', 'Sunday'])) &
              (merged_df['Hour'] < '16:00'), 'Time_Category'] = 'weekend afternoon'
merged_df.loc[(merged_df['Day_of_week'].isin(['Saturday', 'Sunday'])) &
              (merged_df['Hour'] >= '16:00'), 'Time_Category'] = 'weekend evening'
merged_df.loc[(~merged_df['Day_of_week'].isin(['Saturday', 'Sunday'])) &
              (merged_df['Hour'] < '19:00'), 'Time_Category'] = 'workday evening'
merged_df.loc[(~merged_df['Day_of_week'].isin(['Saturday', 'Sunday'])) &
              (merged_df['Hour'] >= '19:00'), 'Time_Category'] = 'workday late evening'

# Calculate the current point and set difference:
merged_df['Current_point_difference'] = merged_df['Current_point_score_host'] - merged_df['Current_point_score_guest']
merged_df['Current_set_difference'] = merged_df['Before_set_score_host'] - merged_df['Before_set_score_guest']

# calculate running max and min points difference partitioned by match and set
merged_df['Max_point_difference_throughout_set'] = merged_df.groupby(['MatchID', 'Set_number'])[
    'Current_point_difference'].rolling(window=100, min_periods=1).max().values
merged_df['Min_point_difference_throughout_set'] = merged_df.groupby(['MatchID', 'Set_number'])[
    'Current_point_difference'].rolling(window=100, min_periods=1).min().values
merged_df['Max_point_difference_throughout_match'] = merged_df.groupby(['MatchID'])['Current_point_difference'].rolling(
    window=10000, min_periods=1).max().values
merged_df['Min_point_difference_throughout_match'] = merged_df.groupby(['MatchID'])['Current_point_difference'].rolling(
    window=10000, min_periods=1).min().values

# Calculate the running average of the net crossings:
merged_df['Running_net_crossings_average'] = merged_df.groupby(['MatchID'])['Net_crossings_number'].rolling(
    window=1000, min_periods=1).mean().values

# Calculate the sum of receives for each team:
merged_df['Current_host_receives'] = merged_df[[col for col in merged_df.columns if
                                                col.startswith('Current_host_receive')]].sum(axis=1)
merged_df['Current_guest_receives'] = merged_df[[col for col in merged_df.columns if
                                                 col.startswith('Current_guest_receive')]].sum(axis=1)

# Calculate the form stats - serve effectiveness, positive_reception_ratio, perfect reception ratio, attack accuracy,
# attack effectiveness:
merged_df['Current_host_serve_effectiveness'] = (merged_df['Current_host_serve_aces'] - merged_df[
    'Current_host_serve_errors']) / merged_df['Current_host_serves']
merged_df['Current_guest_serve_effectiveness'] = (merged_df['Current_guest_serve_aces'] - merged_df[
    'Current_guest_serve_errors']) / merged_df['Current_guest_serves']
merged_df['Current_host_positive_reception_ratio'] = (merged_df['Current_host_receive_positive'] + merged_df[
    'Current_host_receive_perfect']) / merged_df['Current_host_receives']
merged_df['Current_guest_positive_reception_ratio'] = (merged_df['Current_guest_receive_positive'] + merged_df[
    'Current_guest_receive_perfect']) / merged_df['Current_guest_receives']
merged_df['Current_host_perfect_reception_ratio'] = merged_df['Current_host_receive_perfect'] / merged_df[
    'Current_host_receives']
merged_df['Current_guest_perfect_reception_ratio'] = merged_df['Current_guest_receive_perfect'] / merged_df[
    'Current_guest_receives']
merged_df['Current_host_negative_reception_ratio'] = (merged_df['Current_host_receive_negative'] + merged_df[
    'Current_host_receive_ball_returned'] + merged_df['Current_host_receive_errors']) / merged_df[
                                                         'Current_host_receives']
merged_df['Current_guest_negative_reception_ratio'] = (merged_df['Current_guest_receive_negative'] + merged_df[
    'Current_guest_receive_ball_returned'] + merged_df['Current_guest_receive_errors']) / merged_df[
                                                          'Current_guest_receives']
merged_df['Current_host_attack_accuracy'] = merged_df['Current_host_attacks_scored'] / merged_df['Current_host_attacks']
merged_df['Current_guest_attack_accuracy'] = merged_df['Current_guest_attacks_scored'] / merged_df[
    'Current_guest_attacks']
merged_df['Current_host_attack_effectiveness'] = (merged_df['Current_host_attacks_scored'] - merged_df[
    'Current_host_attack_errors'] - merged_df['Current_host_attacks_blocked']) / merged_df['Current_guest_attacks']
merged_df['Current_guest_attack_effectiveness'] = (merged_df['Current_guest_attacks_scored'] - merged_df[
    'Current_guest_attack_errors'] - merged_df['Current_guest_attacks_blocked']) / merged_df['Current_host_attacks']

# Fill NaNs in columns from 90th to the end with 0:
merged_df.iloc[:, 90:] = merged_df.iloc[:, 90:].fillna(0)

# replace inf and -inf with 0
merged_df = merged_df.replace([np.inf, -np.inf], 0)

# create a Winner column with True if the maximum value is 3, and False otherwise
merged_df['Winner'] = merged_df.groupby(['MatchID'])['Current_set_score_host'].transform(max) == 3

# create a relative capacity column:
merged_df['Relative_spectators'] = merged_df['Spectators'] / merged_df['Capacity']

# Add previous matches performance for last 5 matches:
# Decrease the Round number by 5 if it is greater than 5. Decrease it to 1 in other cases:
merged_df['Round_prev'] = np.where(merged_df['Round'].isna(), np.nan,
                                   np.where(merged_df['Round'] > 5, merged_df['Round'] - 5, 1))

# Rename columns for old table:
table_host = table.rename(
    columns={c: c + '_table_host_prev' for c in table.columns if c not in ['Year', 'Round', 'Team']})
table_guest = table.rename(
    columns={c: c + '_table_guest_prev' for c in table.columns if c not in ['Year', 'Round', 'Team']})

# Merge the table with itself to get the previous performance:
merged_df = pd.merge(merged_df, table_host, left_on=['Year', 'Round_prev', 'Team1_href'],
                     right_on=['Year', 'Round', 'Team'], how='left', validate="m:1")
merged_df = pd.merge(merged_df, table_guest, left_on=['Year', 'Round_prev', 'Team2_href'],
                     right_on=['Year', 'Round', 'Team'], how='left', validate="m:1")

# Creating new columns for the difference between the current and previous performance:
merged_df['Matches_ratio_last_5_host'] = merged_df['Won_matches_table_host'] - \
                                         merged_df['Won_matches_table_host_prev'] - \
                                         merged_df['Lost_matches_table_host'] + \
                                         merged_df['Lost_matches_table_host_prev']
merged_df['Matches_ratio_last_5_guest'] = merged_df['Won_matches_table_guest'] - \
                                          merged_df['Won_matches_table_guest_prev'] - \
                                          merged_df['Lost_matches_table_guest'] + \
                                          merged_df['Lost_matches_table_guest_prev']

# Removing unnecessary columns created during the merge:
merged_df = merged_df[merged_df.columns.drop(list(merged_df.filter(regex='_prev')))]
merged_df = merged_df.drop(['Team_y', 'Team_x', 'Round', 'Round_y'], axis=1)
merged_df = merged_df.rename(columns={'Round_x': 'Round'})

# Removing unnecessary columns from the dataframe:
merged_df = merged_df.drop(['Date', 'Capacity', 'Current_set_score_host', 'Current_set_score_guest',
                            'Final_point_score_host', 'Final_point_score_guest'], axis=1)

# Creating season points to matches column:
merged_df['Season_points_to_matches_host'] = merged_df['Season_points_table_host'] / merged_df[
    'Played_matches_table_host']
merged_df['Season_points_to_matches_guest'] = merged_df['Season_points_table_guest'] / merged_df[
    'Played_matches_table_guest']

# Save the dataframe to a csv file:
merged_df.to_csv('../Datasets/Plusliga_data.csv', index=False)

# Limit the columns to the ones that are needed for the model:
model_data = merged_df[['MatchID',  # Identifying info
                        'Winner',  # Dependent variable
                        'Time_Category',  # Match information
                        'Year',
                        'Phase',
                        'Round_original',
                        'Spectators',
                        'Relative_spectators',
                        'Matches_ratio_last_5_host',  # Table info variables
                        'Matches_ratio_last_5_guest',
                        'Season_points_to_matches_host',
                        'Season_points_to_matches_guest',
                        'Current_position_table_host',
                        'Current_position_table_guest',
                        'Sets_ratio_table_host',
                        'Sets_ratio_table_guest',
                        'Points_ratio_table_host',
                        'Points_ratio_table_guest',
                        'Set_number',  # Current situation variables
                        'Current_point_difference',
                        'Current_set_difference',
                        'Max_point_difference_throughout_set',  # Match stats variables
                        'Min_point_difference_throughout_set',
                        'Max_point_difference_throughout_match',
                        'Min_point_difference_throughout_match',
                        'Running_net_crossings_average',
                        'Current_host_serve_effectiveness',
                        'Current_guest_serve_effectiveness',
                        'Current_host_positive_reception_ratio',
                        'Current_guest_positive_reception_ratio',
                        'Current_host_perfect_reception_ratio',
                        'Current_guest_perfect_reception_ratio',
                        'Current_host_negative_reception_ratio',
                        'Current_guest_negative_reception_ratio',
                        'Current_host_attack_accuracy',
                        'Current_guest_attack_accuracy',
                        'Current_host_attack_effectiveness',
                        'Current_guest_attack_effectiveness',
                        'Current_timeouts_host',  # Coach decisions variables
                        'Current_timeouts_guest',
                        'Current_challenges_host',
                        'Current_challenges_guest']]

# Save the dataframe to a csv file:
model_data.to_csv('../Datasets/Plusliga_data_for_model.csv', index=False)


