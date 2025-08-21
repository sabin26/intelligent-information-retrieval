import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from config import CRAWLED_DATA_FILE, INDEX_FILE
from text_processor import process_text

def build_index():
    """
    Builds field-based positional indexes and TF-IDF models from crawled data.

    The function creates and saves four main components:
    1. Positional Index: A map from a term to a dictionary, which in turn maps
       doc_id to a list of positions where the term appears.
       e.g., {'risk': {0: [3, 15], 2: [8]}}
    2. Document Store: A map from doc_id to the document's metadata.
    3. TF-IDF Matrix: A sparse matrix containing TF-IDF vectors for all docs.
    4. TF-IDF Vectorizer: The fitted TfidfVectorizer object, essential for
       transforming new queries consistently.
    """
    print("Starting field-based indexer...")

    try:
        with open(CRAWLED_DATA_FILE, 'r', encoding='utf-8') as f:
            publications = json.load(f)
    except FileNotFoundError:
        print(f"Error: Crawled data file not found at {CRAWLED_DATA_FILE}.")
        return

    # Separate indexes for different fields
    positional_index = {}
    doc_store = {}
    
    # Separate corpora for different fields
    title_corpus = []
    author_corpus = []
    abstract_corpus = []

    print("Building field-based indexes...")
    for doc_id, doc in enumerate(publications):
        doc_store[doc_id] = doc
        
        # Separate field content
        title = doc['title']
        author_names = ' '.join([author['name'] for author in doc['authors']])
        abstract = doc['abstract']
        
        # Add to respective corpora
        title_corpus.append(title)
        author_corpus.append(author_names)
        abstract_corpus.append(abstract)
        
        # Build positional index for combined content (for phrase queries)
        combined_content = title + ' ' + author_names + ' ' + abstract
        tokens = process_text(combined_content)
        
        for pos, token in enumerate(tokens):
            if token not in positional_index:
                positional_index[token] = {}
            if doc_id not in positional_index[token]:
                positional_index[token][doc_id] = []
            positional_index[token][doc_id].append(pos)

    # Create separate TF-IDF vectorizers for each field
    print("\nCreating field-specific TF-IDF models...")
    
    title_vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(1, 2))
    author_vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(1, 2))
    abstract_vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(1, 2))
    
    title_matrix = title_vectorizer.fit_transform(title_corpus)
    author_matrix = author_vectorizer.fit_transform(author_corpus)
    abstract_matrix = abstract_vectorizer.fit_transform(abstract_corpus)
    
    print(f"Title TF-IDF matrix: {title_matrix.shape}")
    print(f"Author TF-IDF matrix: {author_matrix.shape}")
    print(f"Abstract TF-IDF matrix: {abstract_matrix.shape}")

    # Save all components
    index_data = {
        'positional_index': positional_index,
        'doc_store': doc_store,
        'title_matrix': title_matrix,
        'author_matrix': author_matrix,
        'abstract_matrix': abstract_matrix,
        'title_vectorizer': title_vectorizer,
        'author_vectorizer': author_vectorizer,
        'abstract_vectorizer': abstract_vectorizer
    }
    
    joblib.dump(index_data, INDEX_FILE)
    print(f"\nField-based indexing complete. Indexed {len(publications)} documents.")
    print(f"Index saved to {INDEX_FILE}")

if __name__ == '__main__':
    build_index()