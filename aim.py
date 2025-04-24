# aim.py
import pandas as pd
import os

# CSVファイルのパスを指定
data_path = os.path.join("..", "data", "aim_20250417.csv")

# データ読み込み
df = pd.read_csv(data_path)

# 確認
print(df.head())
