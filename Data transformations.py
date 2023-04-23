import pandas as pd

# read CSV file as a dataframe
matches = pd.read_csv('Matches.csv')
table = pd.read_csv('Table_standings.csv')
table_host = table.rename(columns={c: c + '_table_host' for c in table.columns if c not in ['Year', 'Round', 'Team']})
table_guest = table.rename(columns={c: c + '_table_guest' for c in table.columns if c not in ['Year', 'Round', 'Team']})

merged_df = pd.merge(matches, table_host, left_on=['Year', 'Round', 'Team1_href'],
                     right_on=['Year', 'Round', 'Team'], how='left', validate="m:1")
merged_df = pd.merge(merged_df, table_guest, left_on=['Year', 'Round', 'Team2_href'],
                     right_on=['Year', 'Round', 'Team'], how='left', validate="m:1")

# Extract the hour and day of week from the date:
merged_df['Date'] = pd.to_datetime(merged_df['Date'], dayfirst=True)
merged_df['Hour'] = merged_df['Date'].dt.strftime('%H:%M')
merged_df['Day_of_week'] = merged_df['Date'].dt.day_name()

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

# Calculate the sum of receives for each team:
merged_df['Current_host_receives'] = merged_df[[col for col in merged_df.columns if
                                                col.startswith('Current_host_receive')]].sum(axis=1)
merged_df['Current_guest_receives'] = merged_df[[col for col in merged_df.columns if
                                                col.startswith('Current_guest_receive')]].sum(axis=1)

# Calculate the form stats - serve effectiveness, positive_reception_ratio, perfect reception ratio, attack accuracy, attack effectiveness:

# Save the dataframe to a csv file:
merged_df.to_csv('Plusliga_data.csv', index=False)

# TODO:
# 1. Add the last 5 matches results for each team
# 2. Add the recent form - last 5 receptions, last 5 serves, last 5 points
# 3. Add the maximal point difference in the set and match      DONE
# 4. When the phase == playoff, change it to last round of the regular season

