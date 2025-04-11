import pandas as pd
import networkx as nx
import tkinter as tk
from tkinter import filedialog
import os

# 弹出两个文件选择窗口
root = tk.Tk()
root.withdraw()

print("请选择 entities.parquet")
entities_path = filedialog.askopenfilename(title="选择 entities.parquet 文件", filetypes=[("Parquet 文件", "*.parquet")])
if not entities_path:
    print("未选择实体文件，程序退出。")
    exit()

print("请选择 relationships.parquet")
relations_path = filedialog.askopenfilename(title="选择 relationships.parquet 文件", filetypes=[("Parquet 文件", "*.parquet")])
if not relations_path:
    print("未选择关系文件，程序退出。")
    exit()

# 读取文件
entities_df = pd.read_parquet(entities_path)
relations_df = pd.read_parquet(relations_path)

# 创建有向图（你也可以改为 nx.Graph()）
G = nx.DiGraph()

# 添加节点
for _, row in entities_df.iterrows():
    G.add_node(row["id"], label=row["title"], type=row["type"], description=row["description"])

# 添加边
for _, row in relations_df.iterrows():
    G.add_edge(row["source"], row["target"], label=row["description"], weight=row.get("weight", 1.0))

# 输出路径
output_dir = os.path.join(os.path.dirname(__file__), "output_graphml")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "output.graphml")

# 写入 graphml
nx.write_graphml(G, output_path, encoding="utf-8")
print(f"✅ 已保存 graphml 文件至：{output_path}")
