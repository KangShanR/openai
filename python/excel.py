import requests
import base64
import json
import os
# import excel package
import xlrd

# print("os.environ: " + str(os.environ))
import pandas as pd

# Read Excel file
df = pd.read_excel('~/Downloads/dict-adjust1.xlsx', engine='openpyxl')

# Print the contents of the DataFrame
for value in df['dict_code']:
    print('"{}"'.format(value), end=', ')
