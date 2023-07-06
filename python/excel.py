import requests
import base64
import json
import os
# import excel package
import xlrd

# print("os.environ: " + str(os.environ))
import pandas as pd

# Read Excel file
df = pd.read_excel('~/Downloads/dict-adjust2.xlsx', engine='openpyxl')

template = '{}'
columns = df['id']

length = len(columns)
print(f'columns length: {length}')

# Print the contents of the DataFrame
for index in range(length):
    if index == 0:
        print('\n\n\n\n\n')
    elif index != length - 1:
        print(template.format(columns[index]), end=', ')
    else:
        print(template.format(columns[index]))
