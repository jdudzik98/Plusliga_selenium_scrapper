import pandas as pd

# read CSV file as a dataframe
matches = pd.read_csv('Matches.csv')
table = pd.read_csv('Table_standings.csv')
table_host = table.rename(columns={c: c+'_table_host' for c in table.columns if c not in ['Year', 'Round', 'Team']})
table_guest = table.rename(columns={c: c+'_table_guest' for c in table.columns if c not in ['Year', 'Round', 'Team']})

merged_df = pd.merge(matches, table_host, left_on=['Year', 'Round', 'Team1_href'], right_on=['Year', 'Round', 'Team'], how='outer', validate = "m:1")
merged_df = pd.merge(merged_df, table_guest, left_on=['Year', 'Round', 'Team2_href'], right_on=['Year', 'Round', 'Team'], how='outer', validate = "m:1")


merged_df.to_csv('Plusliga_data.csv', index=False)

