import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Optional, TypedDict

from config import INDEX_FILE
from text_processor import process_text

class Author(TypedDict):
    name: str
    profileUrl: Optional[str]

class Publication(TypedDict):
    title: str
    authors: List[Author]
    abstract: str
    date: str
    publicationUrl: str
    relevancyScore: float

class SearchEngine:
    """
    The main search engine class that handles field-based searching with weighted scoring.
    Supports both phrase queries and bag-of-words queries with field-specific weighting.
    """
    def __init__(self):
        """
        Loads all necessary data structures from the index file.
        """
        print("Loading field-based index...")
        try:
            index_data = joblib.load(INDEX_FILE)
            self.positional_index = index_data['positional_index']
            self.doc_store = index_data['doc_store']
            
            # Field-specific components
            self.title_matrix = index_data['title_matrix']
            self.author_matrix = index_data['author_matrix']
            self.abstract_matrix = index_data['abstract_matrix']
            self.title_vectorizer = index_data['title_vectorizer']
            self.author_vectorizer = index_data['author_vectorizer']
            self.abstract_vectorizer = index_data['abstract_vectorizer']
            
            # Default field weights (can be adjusted based on query type)
            self.field_weights = {
                'title': 3.0,    # Highest weight for title matches
                'author': 2.0,   # Medium weight for author matches
                'abstract': 1.0  # Standard weight for abstract matches
            }
            
            print("Field-based index loaded successfully.")
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

    def _calculate_field_scores(self, query: str) -> dict:
        """
        Calculate TF-IDF scores for the query against each field.
        Returns a dictionary with field names as keys and score arrays as values.
        """
        field_scores = {}
        
        try:
            # Transform query for each field
            title_query_vec = self.title_vectorizer.transform([query])
            author_query_vec = self.author_vectorizer.transform([query])
            abstract_query_vec = self.abstract_vectorizer.transform([query])
            
            # Calculate cosine similarities
            field_scores['title'] = cosine_similarity(title_query_vec, self.title_matrix).flatten()
            field_scores['author'] = cosine_similarity(author_query_vec, self.author_matrix).flatten()
            field_scores['abstract'] = cosine_similarity(abstract_query_vec, self.abstract_matrix).flatten()
            
        except ValueError as e:
            print(f"Warning: Query transformation failed: {e}")
            # Return zero scores if transformation fails
            num_docs = len(self.doc_store)
            field_scores = {
                'title': np.zeros(num_docs),
                'author': np.zeros(num_docs),
                'abstract': np.zeros(num_docs)
            }
        
        return field_scores

    def _detect_query_intent(self, query: str) -> dict:
        """
        Analyze the query to determine field weights based on content.
        Adjusts weights based on query characteristics.
        """
        weights = self.field_weights.copy()
        
        # Check for author-like queries (names, "by", etc.)
        author_indicators = ['by ', ' author', 'written by', 'researcher']
        if any(indicator in query.lower() for indicator in author_indicators):
            weights['author'] = 4.0
            weights['title'] = 2.0
        
        # Check for title-like queries (longer phrases, specific terminology)
        if len(query.split()) > 4 or query.startswith('"'):
            weights['title'] = 4.0
            weights['abstract'] = 0.8
        
        return weights

    def search(self, query: str, top_k: int = 1000):
        """
        Performs a field-based search for a given query.
        
        - If the query is wrapped in quotes ("..."), it performs a phrase search.
        - Otherwise, it performs a weighted field-based search.
        - Results are ranked using weighted combination of field scores.

        Args:
            query (str): The user's search query.
            top_k (int): The number of top results to return.

        Returns:
            A list of formatted result dictionaries.
        """
        # 1. Detect query type and adjust weights
        is_phrase_query = query.startswith('"') and query.endswith('"')
        search_query = query.strip('"') if is_phrase_query else query
        
        # Adjust field weights based on query characteristics
        current_weights = self._detect_query_intent(search_query)
        
        if is_phrase_query:
            print("--- Detected Phrase Query ---")
            phrase_tokens = process_text(search_query)
            
            # Use the positional index to get matching documents
            matching_doc_ids = self._find_docs_with_phrase(phrase_tokens)
            
            if not matching_doc_ids:
                return []
            
            # Calculate field scores for all documents
            field_scores = self._calculate_field_scores(search_query)
            
            # Combine scores with weights, but only for matching documents
            final_scores = []
            for doc_id in matching_doc_ids:
                weighted_score = (
                    current_weights['title'] * field_scores['title'][doc_id] +
                    current_weights['author'] * field_scores['author'][doc_id] +
                    current_weights['abstract'] * field_scores['abstract'][doc_id]
                ) / sum(current_weights.values())  # Normalize by total weight
                
                final_scores.append((doc_id, weighted_score))
            
            # Sort by score
            final_scores.sort(key=lambda x: x[1], reverse=True)

        else:
            print("--- Detected Field-Based Query ---")
            print(f"Using weights: Title={current_weights['title']:.1f}, "
                  f"Author={current_weights['author']:.1f}, "
                  f"Abstract={current_weights['abstract']:.1f}")
            
            # Calculate field scores for all documents
            field_scores = self._calculate_field_scores(search_query)
            
            # Combine scores with weights
            final_scores = []
            num_docs = len(self.doc_store)
            
            for doc_id in range(num_docs):
                weighted_score = (
                    current_weights['title'] * field_scores['title'][doc_id] +
                    current_weights['author'] * field_scores['author'][doc_id] +
                    current_weights['abstract'] * field_scores['abstract'][doc_id]
                ) / sum(current_weights.values())  # Normalize by total weight
                
                if weighted_score > 0:  # Only include documents with some relevance
                    final_scores.append((doc_id, weighted_score))
            
            # Sort by score
            final_scores.sort(key=lambda x: x[1], reverse=True)

        # 2. Format and return the top_k results
        results: List[Publication] = []
        for doc_id, score in final_scores[:top_k]:
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
                "abstract": doc_info.get("abstract", ""),
                "date": doc_info.get("date", "N/A"),
                "publicationUrl": doc_info.get("url", ""),
                "relevancyScore": round(score, 4)
            }
            results.append(publication)
        
        return results

    def search_field_specific(self, query: str, field: str, top_k: int = 1000):
        """
        Performs a search targeting a specific field only.
        
        Args:
            query (str): The search query
            field (str): The field to search in ('title', 'author', or 'abstract')
            top_k (int): Number of results to return
        """
        if field not in ['title', 'author', 'abstract']:
            raise ValueError("Field must be 'title', 'author', or 'abstract'")
        
        field_scores = self._calculate_field_scores(query)
        scores = field_scores[field]
        
        # Create list of (doc_id, score) pairs
        doc_scores = [(i, scores[i]) for i in range(len(scores)) if scores[i] > 0]
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Format results
        results: List[Publication] = []
        for doc_id, score in doc_scores[:top_k]:
            doc_info = self.doc_store[doc_id]
            
            formatted_authors: List[Author] = [
                {"name": author["name"], "profileUrl": author.get("url")}
                for author in doc_info.get("authors", [])
            ]
            
            publication: Publication = {
                "title": doc_info.get("title", "No Title"),
                "authors": formatted_authors,
                "abstract": doc_info.get("abstract", ""),
                "date": doc_info.get("date", "N/A"),
                "publicationUrl": doc_info.get("url", ""),
                "relevancyScore": round(score, 4)
            }
            results.append(publication)
        
        return results

def run_search_interface():
    """
    Runs the main interactive search loop with field-based search capabilities.
    """
    engine = SearchEngine()
    
    print("\n--- Coventry University Publication Search (Field-Based) ---")
    print("Enter a query. Use \"quotes\" for exact phrase searches.")
    print("Use 'title:', 'author:', or 'abstract:' prefixes for field-specific searches.")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        query = input("\nSearch> ")
        if query.lower() in ['exit', 'quit']:
            break
        
        # Check for field-specific queries
        if query.startswith(('title:', 'author:', 'abstract:')):
            field, search_term = query.split(':', 1)
            results = engine.search_field_specific(search_term.strip(), field)
            print(f"\nSearching in {field} field for: '{search_term.strip()}'")
        else:
            results = engine.search(query)
        
        if not results:
            print("No results found.")
            continue
            
        print(f"\nFound {len(results)} results:")
        for i, res in enumerate(results[:10]):  # Show top 10
            print(f"\n{i+1}. {res['title']} ({res['date']})")
            print("   Authors:")
            for author in res['authors']:
                profile_url = author['profileUrl'] if author['profileUrl'] else "No profile link"
                print(f"     - {author['name']} ({profile_url})")
            print(f"   Abstract: {res['abstract'][:200]}...")  # Truncate abstract
            print(f"   Publication URL: {res['publicationUrl']}")
            print(f"   Relevance Score: {res['relevancyScore']}")

if __name__ == '__main__':
    run_search_interface()