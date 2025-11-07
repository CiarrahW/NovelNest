# BookMatch Demo — 相似书推荐最小可跑版本

一个基于 TF‑IDF 的中文网文“像这本”找书 Demo。输入一本书名或一段简介，返回相似书 Top‑K，并给出关键词理由。

## 功能
- `Feature 1`：相似书检索（title 或 text 入口）
- 解释理由：关键词重叠 + 权重 Top‑N
- Streamlit 前端 + Flask API（可选）

## 快速开始
```bash
# 1) 克隆后安装依赖（建议新建虚拟环境）
pip install -r requirements.txt

# 2) 准备示例数据（已内置）并构建索引
python scripts/build_index.py

# 3a) 直接跑前端（本地计算，不依赖 API）
streamlit run app/ui.py

# 3b) 或者先启动后端 API，再以前端请求后端的方式运行
python app/api.py               # 终端 A
STREAMLIT_USE_API=1 streamlit run app/ui.py   # 终端 B
```
> 默认会在 `models/` 下生成 `vectorizer.pkl` 与 `tfidf_matrix.pkl`。

## 目录
```
app/
  api.py          # Flask REST API: /api/similar_by_title, /api/similar_by_text
  ui.py           # Streamlit 前端：本地计算或调用 API
data/
  books_sample.csv
models/
  vectorizer.pkl
  tfidf_matrix.pkl
scripts/
  build_index.py  # 构建 TF‑IDF 模型与相似度矩阵
```

## 数据说明
`data/books_sample.csv` 字段：
- `id`：书籍唯一标识
- `title`：书名
- `author`：作者
- `intro`：简介
- `tags`：逗号分隔标签（如：强强,权谋,古言）

## 路线图
- [ ] 替换 TF‑IDF 为句向量（如 SimCSE/CoSENT 或开源中文句向量）
- [ ] 引入 ANN 索引（FAISS / HNSW）
- [ ] 用户画像（问卷 + 行为反馈）
- [ ] 自然语言入口（LLM→结构化检索）

## 许可
MIT