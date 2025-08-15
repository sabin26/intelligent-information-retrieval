import joblib
from typing import List, Optional, TypedDict

from config import INDEX_FILE
from text_processor import process_text
from ranker import TfIdfRanker

class Author(TypedDict):
    name: str
    profileUrl: Optional[str]

class Publication(TypedDict):
    title: str
    authors: List[Author]
    date: str
    publicationUrl: str
    relevancyScore: float

class SearchEngine:
    """
    The main search engine class that handles loading the index and processing queries.
    It uses a single search method that intelligently handles both phrase and
    bag-of-words queries based on user input format.
    """
    def __init__(self):
        """
        Loads all necessary data structures from the index file.
        """
        print("Loading index...")
        try:
            index_data = joblib.load(INDEX_FILE)
            self.positional_index = index_data['positional_index']
            self.doc_store = index_data['doc_store']
            self.ranker = TfIdfRanker(index_data['vectorizer'], index_data['tfidf_matrix'])
            print("Index loaded successfully.")
        except FileNotFoundError:
            print(f"Error: Index file not found at {INDEX_FILE}.")
            print("Please run the indexer first using 'python main.py index'.")
            exit()

    def _find_docs_with_phrase(self, phrase_tokens: list[str]) -> set[int]:
        """
        Helper function to find documents containing an exact sequence of tokens
        using the positional index.
        """
        if not phrase_tokens:
            return set()

        first_term = phrase_tokens[0]
        if first_term not in self.positional_index:
            return set()
        
        candidate_docs = set(self.positional_index[first_term].keys())

        for i in range(1, len(phrase_tokens)):
            term = phrase_tokens[i]
            if not candidate_docs: 
                break
            if term not in self.positional_index: 
                return set()

            docs_with_term = self.positional_index[term]
            matching_docs_for_term = set()

            for doc_id in candidate_docs:
                if doc_id in docs_with_term:
                    prev_positions = self.positional_index[phrase_tokens[i-1]][doc_id]
                    current_positions = docs_with_term[doc_id]
                    if any((pos + 1) in current_positions for pos in prev_positions):
                        matching_docs_for_term.add(doc_id)
            
            candidate_docs = matching_docs_for_term
        
        return candidate_docs
        
    def search(self, query: str, top_k: int = 10):
        """
        Performs a search for a given query.
        
        - If the query is wrapped in quotes ("..."), it performs a phrase search.
        - Otherwise, it performs a standard bag-of-words search.
        
        All results are ranked using TF-IDF and cosine similarity.

        Args:
            query (str): The user's search query.
            top_k (int): The number of top results to return.

        Returns:
            A list of formatted result dictionaries.
        """
        # 1. Detect query type
        is_phrase_query = query.startswith('"') and query.endswith('"')
        
        scores = []
        search_query = query

        if is_phrase_query:
            print("--- Detected Phrase Query ---")
            phrase = query.strip('"')
            search_query = phrase # Use the stripped phrase for ranking
            phrase_tokens = process_text(phrase)
            
            # Use the positional index to get a precise list of matching documents
            matching_doc_ids = self._find_docs_with_phrase(phrase_tokens)
            
            if not matching_doc_ids:
                return []
            
            # Rank all documents to get their scores...
            all_ranked_docs = self.ranker.rank_documents(search_query)
            
            # ...but only keep the ones that contained the exact phrase.
            scores = [
                (doc_id, score) for doc_id, score in all_ranked_docs 
                if doc_id in matching_doc_ids
            ]

        else: # Bag-of-words query
            print("--- Detected Bag-of-Words Query ---")
            scores = self.ranker.rank_documents(search_query)

        # 2. Format and return the top_k results
        results: List[Publication] = []
        for doc_id, score in scores[:top_k]:
            doc_info = self.doc_store[doc_id]
            
            # Format authors to match the Author interface
            formatted_authors: List[Author] = [
                {"name": author["name"], "profileUrl": author.get("url")}
                for author in doc_info.get("authors", [])
            ]
            
            # Create the publication object with the correct keys
            publication: Publication = {
                "title": doc_info.get("title", "No Title"),
                "authors": formatted_authors,
                "date": doc_info.get("date", "N/A"),
                "publicationUrl": doc_info.get("url", ""),
                "relevancyScore": round(score, 4)
            }
            results.append(publication)
        return results

def run_search_interface():
    """
    Runs the main interactive search loop.
    """
    engine = SearchEngine()
    
    print("\n--- Coventry University Publication Search (TF-IDF) ---")
    print("Enter a query. Use \"quotes\" for exact phrase searches.")
    print("Type 'exit' or 'quit' to stop.")
    
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
            print(f"\n{i+1}. {res['title']} ({res['date']})")
            print("   Authors:")
            for author in res['authors']:
                profile_url = author['profileUrl'] if author['profileUrl'] else "No profile link"
                print(f"     - {author['name']} ({profile_url})")
            print(f"   Publication URL: {res['publicationUrl']}")
            print(f"   Cosine Similarity Score: {res['relevancyScore']}")

if __name__ == '__main__':
    run_search_interface()