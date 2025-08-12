import json
import joblib
from collections import defaultdict, Counter
from tqdm import tqdm

from config import CRAWLED_DATA_FILE, INDEX_FILE
from text_processor import process_text

def build_index():
    """
    Builds an inverted index from the crawled publication data.
    
    The function creates and saves three main components:
    1. Inverted Index: A map from a term to a list of (doc_id, term_frequency) tuples.
    2. Document Store: A map from doc_id to the document's metadata (title, url, etc.).
    3. Document Lengths: A map from doc_id to the total number of tokens in the document.
    """
    print("Starting indexer...")
    
    try:
        with open(CRAWLED_DATA_FILE, 'r', encoding='utf-8') as f:
            publications = json.load(f)
    except FileNotFoundError:
        print(f"Error: Crawled data file not found at {CRAWLED_DATA_FILE}.")
        print("Please run the crawler first using 'python main.py crawl'.")
        return

    # The core data structures for our search engine
    inverted_index = defaultdict(list)
    doc_store = {}
    doc_lengths = {}
    
    # Process each publication
    for doc_id, doc in enumerate(tqdm(publications, desc="Indexing documents")):
        # Extract just the names from the author dictionaries for indexing
        author_names = ' '.join([author['name'] for author in doc['authors']])
        # Combine title and authors for the searchable content
        content = doc['title'] + ' ' + author_names
        
        # Store the original document metadata
        doc_store[doc_id] = {
            'title': doc['title'],
            'url': doc['url'],
            'authors': doc['authors'],
            'year': doc['year']
        }
        
        # Process the text to get tokens
        tokens = process_text(content)
        
        # Store the length of the processed document (for BM25)
        doc_lengths[doc_id] = len(tokens)
        
        # Calculate term frequencies for the current document
        term_counts = Counter(tokens)
        
        # Populate the inverted index
        for term, freq in term_counts.items():
            inverted_index[term].append((doc_id, freq))

    # Save the created index and associated data to a file
    index_data = {
        'inverted_index': inverted_index,
        'doc_store': doc_store,
        'doc_lengths': doc_lengths
    }
    
    joblib.dump(index_data, INDEX_FILE)
    
    print(f"\nIndexing complete. Indexed {len(publications)} documents.")
    print(f"Index saved to {INDEX_FILE}")

if __name__ == '__main__':
    build_index()