import os, pickle, requests, json
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

APP_DIR = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(APP_DIR, '..'))
DATA_PATH = os.path.join(ROOT, 'data', 'books_sample.csv')
VEC_PATH = os.path.join(ROOT, 'models', 'vectorizer.pkl')
MAT_PATH = os.path.join(ROOT, 'models', 'tfidf_matrix.pkl')

st.set_page_config(page_title='BookMatch Demo', page_icon='📚', layout='wide')
st.title('📚 BookMatch Demo — 相似书推荐')

use_api = os.environ.get('STREAMLIT_USE_API') == '1'
api_url = os.environ.get('API_URL', 'http://127.0.0.1:5000')

@st.cache_resource
def load_assets():
    with open(VEC_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    with open(MAT_PATH, 'rb') as f:
        tfidf_matrix = pickle.load(f)
    books = pd.read_csv(DATA_PATH)
    return vectorizer, tfidf_matrix, books

if not use_api:
    vectorizer, tfidf_matrix, books = load_assets()

def explain(idx_top, q_vec, vectorizer, tfidf_matrix):
    feature_names = np.array(vectorizer.get_feature_names_out())
    q_weights = q_vec.toarray().ravel()
    top_term_ids = q_weights.argsort()[-8:][::-1]
    q_terms = set(feature_names[top_term_ids])
    doc_vec = tfidf_matrix[idx_top]
    doc_weights = doc_vec.toarray().ravel()
    doc_term_ids = doc_weights.argsort()[-12:][::-1]
    doc_terms = set(feature_names[doc_term_ids])
    common = [w for w in feature_names if w in q_terms and w in doc_terms]
    return common[:5]

with st.sidebar:
    st.markdown("### 输入方式")
    mode = st.radio("选择：", ["按书名找相似", "粘贴简介找相似"])
    k = st.slider("返回数量 Top‑K", 3, 10, 5)

if mode == "按书名找相似":
    title = st.text_input("书名（样例：长安风月 / 京华故梦 / 霜刃未曾试 / 星河入梦 / 明月照归途）")
    if st.button("生成推荐", use_container_width=True) and title.strip():
        if use_api:
            resp = requests.post(f"{api_url}/api/similar_by_title", json={"title": title, "k": k})
            if resp.status_code == 200:
                results = resp.json()
            else:
                st.error(resp.text)
                results = []
        else:
            # 本地计算
            match = books[books['title'].str.contains(title, case=False, na=False)]
            if match.empty:
                st.warning("示例数据未找到该书，可尝试“粘贴简介找相似”。")
                results = []
            else:
                idx = match.index[0]
                q_vec = tfidf_matrix[idx]
                sims = cosine_similarity(q_vec, tfidf_matrix).ravel()
                sims[idx] = -1
                top_idx = sims.argsort()[::-1][:k]
                results = []
                for i in top_idx:
                    results.append({
                        "book_id": int(books.iloc[i]['id']),
                        "title": books.iloc[i]['title'],
                        "author": books.iloc[i]['author'],
                        "score": float(sims[i]),
                        "why": explain(i, q_vec, vectorizer, tfidf_matrix)
                    })
        if results:
            for r in results:
                st.markdown(f"**{r['title']}** · {r['author']} — 相似度 {r['score']:.3f}")
                if r.get("why"):
                    st.caption("理由：" + "、".join(r["why"]))
                st.divider()

else:
    text = st.text_area("粘贴一本书的简介 / 你喜欢的元素描述", height=160,
                        placeholder="例如：古言权谋，女主成长，群像，文风细腻……")
    if st.button("生成推荐", use_container_width=True) and text.strip():
        if use_api:
            resp = requests.post(f"{api_url}/api/similar_by_text", json={"text": text, "k": k})
            if resp.status_code == 200:
                results = resp.json()
            else:
                st.error(resp.text); results = []
        else:
            vectorizer, tfidf_matrix, books = load_assets()
            q_vec = vectorizer.transform([text])
            sims = cosine_similarity(q_vec, tfidf_matrix).ravel()
            top_idx = sims.argsort()[::-1][:k]
            results = []
            for i in top_idx:
                results.append({
                    "book_id": int(books.iloc[i]['id']),
                    "title": books.iloc[i]['title'],
                    "author": books.iloc[i]['author'],
                    "score": float(sims[i]),
                    "why": explain(i, q_vec, vectorizer, tfidf_matrix)
                })
        if results:
            for r in results:
                st.markdown(f"**{r['title']}** · {r['author']} — 相似度 {r['score']:.3f}")
                if r.get("why"):
                    st.caption("理由：" + "、".join(r["why"]))
                st.divider()