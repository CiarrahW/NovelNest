from flask import Flask, request, jsonify
import os, pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

APP_DIR = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(APP_DIR, '..'))
DATA_PATH = os.path.join(ROOT, 'data', 'books_sample.csv')
VEC_PATH = os.path.join(ROOT, 'models', 'vectorizer.pkl')
MAT_PATH = os.path.join(ROOT, 'models', 'tfidf_matrix.pkl')

app = Flask(__name__)

def _load_assets():
    with open(VEC_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    with open(MAT_PATH, 'rb') as f:
        tfidf_matrix = pickle.load(f)
    books = pd.read_csv(DATA_PATH)
    return vectorizer, tfidf_matrix, books

vectorizer, tfidf_matrix, books = _load_assets()

def _explain(idx_top, q_vec):
    # 取关键词：查询文本与候选文本 TF-IDF 权重较高的交集
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

@app.post('/api/similar_by_title')
def similar_by_title():
    payload = request.get_json(force=True)
    title = (payload or {}).get('title', '').strip()
    k = int((payload or {}).get('k', 5))
    if not title:
        return jsonify({'error': 'title required'}), 400

    # 找到该书
    match = books[books['title'].str.contains(title, case=False, na=False)]
    if match.empty:
        return jsonify({'error': 'title not found in dataset'}), 404

    idx = match.index[0]
    q_vec = tfidf_matrix[idx]
    sims = cosine_similarity(q_vec, tfidf_matrix).ravel()
    # 排除自身
    sims[idx] = -1
    top_idx = sims.argsort()[::-1][:k]
    results = []
    for i in top_idx:
        results.append({
            'book_id': int(books.iloc[i]['id']),
            'title': books.iloc[i]['title'],
            'author': books.iloc[i]['author'],
            'score': float(sims[i]),
            'why': _explain(i, q_vec),
        })
    return jsonify(results)

@app.post('/api/similar_by_text')
def similar_by_text():
    payload = request.get_json(force=True)
    text = (payload or {}).get('text', '').strip()
    k = int((payload or {}).get('k', 5))
    if not text:
        return jsonify({'error': 'text required'}), 400
    q_vec = vectorizer.transform([text])
    from sklearn.metrics.pairwise import cosine_similarity
    sims = cosine_similarity(q_vec, tfidf_matrix).ravel()
    top_idx = sims.argsort()[::-1][:k]
    results = []
    for i in top_idx:
        results.append({
            'book_id': int(books.iloc[i]['id']),
            'title': books.iloc[i]['title'],
            'author': books.iloc[i]['author'],
            'score': float(sims[i]),
            'why': _explain(i, q_vec),
        })
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)