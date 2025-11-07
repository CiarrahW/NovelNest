import os, pickle, jieba, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / 'data' / 'books_sample.csv'
MODELS_DIR = ROOT / 'models'
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def preprocess(text: str) -> str:
    # 简单中文分词 + 去空白
    if not isinstance(text, str): return ''
    tokens = jieba.lcut(text.replace('\n', ' '))
    tokens = [t.strip() for t in tokens if t.strip()]
    return ' '.join(tokens)

def main():
    df = pd.read_csv(DATA_PATH)
    corpus = (df['intro'].fillna('') + ' ' + df['tags'].fillna('')).apply(preprocess).tolist()
    vectorizer = TfidfVectorizer(max_features=20000)
    X = vectorizer.fit_transform(corpus)

    with open(MODELS_DIR / 'vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    with open(MODELS_DIR / 'tfidf_matrix.pkl', 'wb') as f:
        pickle.dump(X, f)

    print('Saved:', MODELS_DIR / 'vectorizer.pkl', MODELS_DIR / 'tfidf_matrix.pkl')
    print('Rows:', X.shape[0], 'Dims:', X.shape[1])

if __name__ == '__main__':
    main()