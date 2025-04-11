import pandas as pd
from tkinter import filedialog
import tkinter as tk

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(title="选择 .parquet 文件", filetypes=[("Parquet 文件", "*.parquet")])
if not file_path:
    print("未选择文件")
    exit()

df = pd.read_parquet(file_path)
print("字段列表：", list(df.columns))
print("前几行数据：")
print(df.head())
