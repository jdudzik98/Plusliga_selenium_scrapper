import pandas as pd

# read CSV file as a dataframe
matches = pd.read_csv('Matches.csv')
table = pd.read_csv('Table_standings.csv')

#merged_df = pd.merge(matches, table, on=['Year', 'Round'], how='outer')
#merged_df = pd.merge(matches, table, on=['Year', 'Round', ], how='outer', suffixes=('_df1', '_df2'))
merged_df = pd.merge(matches, table, left_on=['Year', 'Round', 'Team1_href'], right_on=['Year', 'Round', 'Team'], how='outer', suffixes=('', '_table_host'))
merged_df = pd.merge(merged_df, table, left_on=['Year', 'Round', 'Team2_href'], right_on=['Year', 'Round', 'Team'], how='outer', suffixes=('', '_table_guest'))


merged_df.to_csv('Plusliga_data.csv', index=False)

