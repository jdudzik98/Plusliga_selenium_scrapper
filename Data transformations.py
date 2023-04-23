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

# Calculate the running average of the net crossings: TODO: correct this
merged_df['Running_net_crossings_average'] = merged_df.groupby(['MatchID'])['Net_crossings_number'].rolling(
    window=1000, min_periods=1).mean().values

# Calculate the sum of receives for each team:
merged_df['Current_host_receives'] = merged_df[[col for col in merged_df.columns if
                                                col.startswith('Current_host_receive')]].sum(axis=1)
merged_df['Current_guest_receives'] = merged_df[[col for col in merged_df.columns if
                                                col.startswith('Current_guest_receive')]].sum(axis=1)

# Calculate the form stats - serve effectiveness, positive_reception_ratio, perfect reception ratio, attack accuracy, attack effectiveness:
merged_df['Current_host_serve_effectiveness'] = (merged_df['Current_host_serve_aces'] - merged_df['Current_host_serve_errors'])/merged_df['Current_host_serves']
merged_df['Current_guest_serve_effectiveness'] = (merged_df['Current_guest_serve_aces'] - merged_df['Current_guest_serve_errors'])/merged_df['Current_guest_serves']
merged_df['Current_host_positive_reception_ratio'] = (merged_df['Current_host_receive_positive'] + merged_df['Current_host_receive_perfect'])/merged_df['Current_host_receives']
merged_df['Current_guest_positive_reception_ratio'] = (merged_df['Current_guest_receive_positive'] + merged_df['Current_guest_receive_perfect'])/merged_df['Current_guest_receives']
merged_df['Current_host_perfect_reception_ratio'] = merged_df['Current_host_receive_perfect']/merged_df['Current_host_receives']
merged_df['Current_guest_perfect_reception_ratio'] = merged_df['Current_guest_receive_perfect']/merged_df['Current_guest_receives']
merged_df['Current_host_negative_reception_ratio'] = (merged_df['Current_host_receive_negative']+merged_df['Current_host_receive_ball_returned'] + merged_df['Current_host_receive_errors'])/merged_df['Current_host_receives']
merged_df['Current_guest_negative_reception_ratio'] = (merged_df['Current_guest_receive_negative']+merged_df['Current_guest_receive_ball_returned'] + merged_df['Current_guest_receive_errors'])/merged_df['Current_guest_receives']
merged_df['Current_host_attack_accuracy'] = merged_df['Current_host_attacks_scored']/merged_df['Current_host_attacks']
merged_df['Current_guest_attack_accuracy'] = merged_df['Current_guest_attacks_scored']/merged_df['Current_guest_attacks']
merged_df['Current_host_attack_effectiveness'] = (merged_df['Current_host_attacks_scored']-merged_df['Current_host_attack_errors']-merged_df['Current_host_attacks_blocked'])/merged_df['Current_guest_attacks']
merged_df['Current_guest_attack_effectiveness'] = (merged_df['Current_guest_attacks_scored']-merged_df['Current_guest_attack_errors']-merged_df['Current_guest_attacks_blocked'])/merged_df['Current_host_attacks']


# Fill NaNs in columns from
merged_df.iloc[:, 90:] = merged_df.iloc[:, 90:].fillna(0)

# Save the dataframe to a csv file:
merged_df.to_csv('Plusliga_data.csv', index=False)

# TODO:
# 1. Add the last 5 matches results for each team
# 2. Add the recent form - last 5 receptions, last 5 serves, last 5 points - switched to running sum
# 3. Add the maximal point difference in the set and match      DONE
# 4. When the phase == playoff, change it to last round of the regular season DONE
# 5. Review the variables and change them to running sums/averages etc.

