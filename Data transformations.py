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

# Calculate cumulative count of serves for each team:
merged_df['Cumulative_serving_host'] = merged_df.groupby(['MatchID'])['Serving_team'].transform(
    lambda x: x.eq('Host').cumsum())
merged_df['Cumulative_serving_guest'] = merged_df.groupby(['MatchID'])['Serving_team'].transform(
    lambda x: x.eq('Guest').cumsum())

# Calculate cumulative count of error serves for both teams :
merged_df['Cumulative_serving_host_errors'] = (merged_df['Serving_team'] + merged_df['Serve_effect'])
merged_df['Cumulative_serving_guest_errors'] = merged_df.groupby(['MatchID', 'Set_number'])[
    'Cumulative_serving_host_errors'].transform(lambda x: x.eq("Guesterror").cumsum())
merged_df['Cumulative_serving_host_errors'] = merged_df.groupby(['MatchID', 'Set_number'])[
    'Cumulative_serving_host_errors'].transform(lambda x: x.eq("Hosterror").cumsum())

# Save the dataframe to a csv file:
merged_df.to_csv('Plusliga_data.csv', index=False)

# TODO:
# 1. Add the last 5 matches results for each team
# 2. Add the recent form - last 5 receptions, last 5 serves, last 5 points
# 3. Add the maximal point difference in the set and match      DONE
