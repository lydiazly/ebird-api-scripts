import pandas as pd

data1 = {'speciesCode': ['A', 'B', 'C'],
         'comName': ['Bird_A', 'Bird_B', 'Bird_C'],
         'sciName': ['Scientific_A', 'Scientific_B', 'Scientific_C']}
df1 = pd.DataFrame(data1)

column_names_dict = {'SPECIES_CODE': 'speciesCode',
                     'COMMON_NAME': 'comName',
                     'SCIENTIFIC_NAME': 'sciName'}

data0_0 = {'SPECIES_CODE': ['A'],
           'COMMON_NAME': ['Bird_A'],
           'SCIENTIFIC_NAME': ['Scientific_A']}
df0_0 = pd.DataFrame(data0_0).rename(columns=column_names_dict)

data2_1 = {'speciesCode': ['A', 'C', 'D'],
           'comName': ['Bird_A', 'Bird_C', 'Bird_D'],
           'sciName': ['Scientific_A', 'Scientific_C', 'Scientific_D'],
           'howMany': [10, 20, 'X']}
df2_1 = pd.DataFrame(data2_1)

data2_2 = {'speciesCode': ['A', 'C', 'E'],
           'comName': ['Bird_A', 'Bird_C', 'Bird_E'],
           'sciName': ['Scientific_A', 'Scientific_C', 'Scientific_E'],
           'howMany': [15, 25, 35]}
df2_2 = pd.DataFrame(data2_2)

# List of your df2 DataFrames
df2_list = [df2_1, df2_2]  # Add more DataFrames to this list as needed

# Merge df1 with each df2 DataFrame
result_df = df1.copy()

result_df = pd.merge(result_df, df0_0[['speciesCode', 'comName', 'sciName']], on=result_df.columns.to_list(), how='outer')
print(result_df)

result_df['howMany'] = 0

for df2 in df2_list:
    result_df = pd.merge(result_df, df2[['speciesCode', 'comName', 'sciName', 'howMany']], on=['speciesCode', 'comName', 'sciName', 'howMany'], how='outer')
    print(result_df)

# Replace 'X' with 0 in the 'howMany' column and convert it to numeric
# result_df['howMany'] = pd.to_numeric(result_df['howMany'].replace('X', 0))
result_df['howMany'] = pd.to_numeric(result_df['howMany'], errors='coerce')

# Fill NaN values in 'howMany' column with 0
result_df['howMany'].fillna(0, inplace=True)

# Aggregate the counts for each speciesCode
result_df['count'] = result_df.groupby('speciesCode')['howMany'].transform('sum').astype(int)

# Drop duplicate columns and reset index
result_df = result_df[['speciesCode', 'comName', 'sciName', 'count']].drop_duplicates().reset_index(drop=True)

# Print the combined table
print(result_df)

print(result_df.loc[:, ['speciesCode', 'count']])
