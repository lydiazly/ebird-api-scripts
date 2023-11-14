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
           'comName': ['Bird_A_0', 'Bird_C', 'Bird_D'],
           'sciName': ['Scientific_A', 'Scientific_C', 'Scientific_D'],
           'howMany': [10, 20, 'X']}
df2_1 = pd.DataFrame(data2_1)

data2_2 = {'speciesCode': ['A', 'C', 'E'],
           'comName': ['Bird_A', 'Bird_C_0', 'Bird_E'],
           'sciName': ['Scientific_A', 'Scientific_C', 'Scientific_E'],
           'howMany': [15, 25, 35]}
df2_2 = pd.DataFrame(data2_2)

# List of your df DataFrames
df2_list = [df2_1, df2_2]  # Add more DataFrames to this list as needed

# Merge df1 with each df DataFrame
merged_df = df1.copy()

merged_df = pd.merge(merged_df, df0_0[['speciesCode', 'comName', 'sciName']], on=merged_df.columns.to_list(), how='outer')
print("df:")
print(merged_df)

merged_df['howMany'] = 0

for i, df in enumerate(df2_list):
    print("df:")
    print(df)
    # merged_df = pd.merge(merged_df, df[['speciesCode', 'comName', 'sciName', 'howMany']],
    #                      on=['speciesCode', 'comName', 'sciName', 'howMany'], how='outer')
    # df['howMany'] = pd.to_numeric(df['howMany'], errors='coerce').fillna(0).astype('Int64')
    # print("df after to_numeric:")
    # print(df)
    merged_df = pd.merge(merged_df, df[['speciesCode', 'howMany']],
                         on='speciesCode', how='left', suffixes=('', f'_{i+1}'))
    print("merged_df after merge:")
    print(merged_df)
    missing_ids = ~df['speciesCode'].isin(merged_df['speciesCode'])
    print("Missing:")
    print(df.loc[missing_ids, :])
    merged_df = pd.concat([merged_df, df.loc[missing_ids, ['speciesCode', 'comName', 'sciName', 'howMany']]], ignore_index=True)
    print("merged_df after appending:")
    print(merged_df)

# Replace 'X' with 0 in the 'howMany' column and convert it to numeric
# merged_df['howMany'] = pd.to_numeric(merged_df['howMany'].replace('X', 0))
# merged_df['howMany'] = pd.to_numeric(merged_df['howMany'], errors='coerce').fillna(0).astype('Int64')
count_columns = [col for col in merged_df.columns if 'howMany' in col]
merged_df[count_columns] = merged_df[count_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype('Int64')
print("merged_df after correct values:")
print(merged_df)

# Drop the 'howMany_*' columns
# merged_df.drop(columns=count_columns, inplace=True)

# Fill NaN values in 'howMany' column with 0
# merged_df['howMany'].fillna(0, inplace=True).astype('Int64')

# Aggregate the counts for each speciesCode
# merged_df['count'] = merged_df.groupby('speciesCode', as_index=False)['howMany'].transform('sum')

# Sum the 'howMany_*' columns to create 'count'
merged_df['count'] = merged_df[count_columns].sum(axis=1)


# Drop duplicate columns and reset index
# merged_df = merged_df[['speciesCode', 'comName', 'sciName', 'count']].drop_duplicates().reset_index(drop=True)

# Print the combined table
print(merged_df)
