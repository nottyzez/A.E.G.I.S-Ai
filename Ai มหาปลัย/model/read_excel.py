import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd

path = r'C:\Users\Admin\Downloads\Dataset-20261017T044013Z-1-001\hydroponic_log (1).xlsx'

for sname in ['Control', 'ขาด N', 'ขาด P', 'ขาด K']:
    df = pd.read_excel(path, sheet_name=sname, header=None)
    print(f'\n========== {sname} ==========')
    print(df.to_string())
