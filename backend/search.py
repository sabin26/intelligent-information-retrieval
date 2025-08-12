import joblib
from config import INDEX_FILE
from text_processor import process_text
from ranker import BM25Ranker

class SearchEngine:
    """
    The main search engine class that handles loading the index and processing queries.
    """
    def __init__(self):
        """
        Loads the index and initializes the ranker.
        """
        print("Loading index...")
        try:
            index_data = joblib.load(INDEX_FILE)
            self.doc_store = index_data['doc_store']
            self.inverted_index = index_data['inverted_index']
            self.ranker = BM25Ranker(index_data)
            print("Index loaded successfully.")
        except FileNotFoundError:
            print(f"Error: Index file not found at {INDEX_FILE}.")
            print("Please run the indexer first using 'python main.py index'.")
            exit()

    def search(self, query: str, top_k: int = 10):
        """
        Performs a search for a given query.

        Args:
            query (str): The user's search query.
            top_k (int): The number of top results to return.

        Returns:
            list[dict]: A list of ranked result dictionaries.
        """
        if not query:
            return []

        # 1. Process the query in the same way as documents
        query_tokens = process_text(query)
        if not query_tokens:
            return []

        # 2. Find candidate documents that contain at least one query term
        candidate_docs = set()
        for token in query_tokens:
            if token in self.inverted_index:
                # Add all doc_ids from the posting list of the token
                doc_ids = {doc_id for doc_id, freq in self.inverted_index[token]}
                candidate_docs.update(doc_ids)

        if not candidate_docs:
            return []

        # 3. Score each candidate document using the ranker
        scores = [
            (doc_id, self.ranker.score_doc(doc_id, query_tokens))
            for doc_id in candidate_docs
        ]

        # 4. Sort documents by score in descending order
        scores.sort(key=lambda x: x[1], reverse=True)

        # 5. Format and return the top_k results
        results = []
        for doc_id, score in scores[:top_k]:
            doc_info = self.doc_store[doc_id]
            results.append({
                'score': round(score, 4),
                'title': doc_info['title'],
                'url': doc_info['url'],
                'authors': doc_info['authors'],
                'year': doc_info['year']
            })
            
        return results

def run_search_interface():
    """
    Runs a simple command-line interface for the search engine.
    """
    engine = SearchEngine()
    
    print("\n--- Coventry University Publication Search ---")
    print("Enter your query below. Type 'exit' or 'quit' to stop.")
    
    while True:
        query = input("\nSearch> ")
        if query.lower() in ['exit', 'quit']:
            break
        
        results = engine.search(query)
        
        if not results:
            print("No results found.")
            continue
            
        print(f"\nFound {len(results)} results for '{query}':")
        for i, res in enumerate(results):
            print(f"\n{i+1}. {res['title']} ({res['year']})")
            
            # Display authors with their profile URLs for easy access
            print(f"   Authors:")
            for author in res['authors']:
                profile_url = author['url'] if author['url'] else "No profile link"
                print(f"     - {author['name']} ({profile_url})")
            
            print(f"   Publication URL: {res['url']}")
            print(f"   BM25 Score: {res['score']}")

if __name__ == '__main__':
    run_search_interface()