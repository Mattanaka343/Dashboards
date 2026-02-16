from glob import glob
import pandas as pd

paths = glob('../Data/*.csv', recursive=True)
data = []

idx_min = 0
min=100000000
for i, path in enumerate(paths):
    data.append(pd.read_csv(path))
    if len(data[i].columns) <= min:
        min = len(data[i].columns)
        idx_min = i


columns_to_extract = None
for i, df in enumerate(data):
    if i == 0:
        columns_to_extract = set(df.columns) & set(data[idx_min].columns) 
    else:
        columns_to_extract = set(df.columns) & columns_to_extract

columns_to_extract = list(columns_to_extract)

data = [df[columns_to_extract] for df in data]

final = pd.concat(data).drop_duplicates()

final.to_csv('../Data/general_data.csv',index=False)

