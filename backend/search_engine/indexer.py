import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from config import CRAWLED_DATA_FILE, INDEX_FILE
from text_processor import process_text

def build_index():
    """
    Builds a positional index and a TF-IDF model from crawled data.

    The function creates and saves four main components:
    1. Positional Index: A map from a term to a dictionary, which in turn maps
       doc_id to a list of positions where the term appears.
       e.g., {'risk': {0: [3, 15], 2: [8]}}
    2. Document Store: A map from doc_id to the document's metadata.
    3. TF-IDF Matrix: A sparse matrix containing TF-IDF vectors for all docs.
    4. TF-IDF Vectorizer: The fitted TfidfVectorizer object, essential for
       transforming new queries consistently.
    """
    print("Starting indexer for TF-IDF and Positional Index...")

    try:
        with open(CRAWLED_DATA_FILE, 'r', encoding='utf-8') as f:
            publications = json.load(f)
    except FileNotFoundError:
        print(f"Error: Crawled data file not found at {CRAWLED_DATA_FILE}.")
        print("Please run the crawler first using 'python main.py crawl'.")
        return

    positional_index = {}
    doc_store = {}
    corpus = [] # List of document texts for the vectorizer

    print("Building positional index...")
    for doc_id, doc in enumerate(publications):
        author_names = ' '.join([author['name'] for author in doc['authors']])
        content = doc['title'] + ' ' + author_names + ' ' + doc['abstract']
        
        # Store the original document metadata
        doc_store[doc_id] = doc
        
        # Add the raw content to the corpus for TF-IDF vectorization
        corpus.append(content)

        # Process the text to get tokens for the positional index
        tokens = process_text(content)
        
        for pos, token in enumerate(tokens):
            if token not in positional_index:
                positional_index[token] = {}
            if doc_id not in positional_index[token]:
                positional_index[token][doc_id] = []
            positional_index[token][doc_id].append(pos)

    # --- TF-IDF Vectorization ---
    print("\nCreating TF-IDF model...")
    # We use the same text_processor for tokenization to ensure consistency
    # but let TfidfVectorizer handle its own stopword removal and lowercasing.
    vectorizer = TfidfVectorizer(
        stop_words='english',
        lowercase=True,
        ngram_range=(1, 2)
    )
    
    # Fit the vectorizer on the whole corpus and transform it into a matrix
    tfidf_matrix = vectorizer.fit_transform(corpus)
    print(f"TF-IDF matrix created with shape: {tfidf_matrix.shape}")

    # Save all components needed for searching
    index_data = {
        'positional_index': positional_index,
        'doc_store': doc_store,
        'tfidf_matrix': tfidf_matrix,
        'vectorizer': vectorizer
    }
    
    joblib.dump(index_data, INDEX_FILE)
    
    print(f"\nIndexing complete. Indexed {len(publications)} documents.")
    print(f"Index saved to {INDEX_FILE}")

if __name__ == '__main__':
    build_index()