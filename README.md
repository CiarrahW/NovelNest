# NovelNest
## Project Map
### 1. Data Layer — Collection & Storage
	•	Source: Web-scraped or curated book metadata (title, author, synopsis, tags, stats, popularity, completion status).
	•	Goal: Build a clean and consistent dataset for later modeling.
	•	Format: books.csv stored in a lightweight SQL/CSV format.
	•	Format: features
	book_id       INTEGER PRIMARY KEY,
    title         TEXT,
    author        TEXT,
    intro         TEXT,
    tags          TEXT,
    main_chars    TEXT,
    support_chars TEXT,
    other_info    TEXT,
    category      TEXT,
    perspective   TEXT,
    series        TEXT,
    status        TEXT,
    word_count    INTEGER,
    publish_status TEXT,
    sign_status    TEXT,
    last_update_time TEXT,
    chapter_count   INTEGER
### 2. Representation Layer — Text Processing & Embedding (NLP)
	•	Preprocessing: Chinese tokenization (jieba), stopword removal, keyword extraction.
	•	Feature Encoding:
	  Phase 1: TF-IDF baseline for quick similarity demo.
	  Phase 2: Sentence embeddings (e.g., SimCSE/CoSENT or multilingual models).
### 3. Retrieval & Recommendation Layer
	•	Similarity Search: Cosine similarity or approximate nearest neighbor (FAISS/HNSW).
	•	Ranking Logic: Blend vector similarity with auxiliary scores (popularity, update frequency, completion).
	•	Feedback Loop: User “like / dislike” data refines personal vector profile over time.
	•	Explainability: Extract overlapping keywords or topics as “reason” tags.
### 4. Interaction Layer - UI

## Features
### F1. Similar-to-this Book: 
Input a title → returns top-K similar books.

The system embeds that book’s description into a vector and compares it against all books in the database using vector similarity search. It then returns the Top-N most similar books along with explanation tags that highlight shared themes, styles, or character dynamics.

### F2. Profile-driven Rec:
An MBTI-style questionnaire builds each user’s initial reading profile, then generates a personalized booklist with reasoning.

The user’s long-term profile is continuously updated based on feedback — what they like, dislike, or have already read — enabling iterative, personalized rankings and recommendations.

### F3. Natural-Language Interface (LLM):
Users can simply describe what they want to read, such as

“A slow-burn romance between rivals set in a historical court.”

The LLM rewrites the input into structured retrieval conditions and vector queries, feeding back into the Feature 2 pipeline to produce unified, context-aware recommendations.
