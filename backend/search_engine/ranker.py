import math
from config import BM25_K1, BM25_B

class BM25Ranker:
    """
    Implements the Okapi BM25 ranking algorithm.
    """
    def __init__(self, index_data):
        """
        Initializes the ranker with the necessary data from the index.

        Args:
            index_data (dict): The dictionary loaded from the index file, containing
                               'inverted_index', 'doc_store', and 'doc_lengths'.
        """
        self.inverted_index = index_data['inverted_index']
        self.doc_store = index_data['doc_store']
        self.doc_lengths = index_data['doc_lengths']
        self.num_docs = len(self.doc_store)
        self.avg_doc_length = sum(self.doc_lengths.values()) / self.num_docs
        self.k1 = BM25_K1
        self.b = BM25_B

    def _calculate_idf(self, term: str) -> float:
        """
        Calculates the Inverse Document Frequency (IDF) for a term.
        Uses a smoothed version to handle terms not in the corpus.
        """
        num_docs_with_term = len(self.inverted_index.get(term, []))
        # BM25's IDF formula
        numerator = self.num_docs - num_docs_with_term + 0.5
        denominator = num_docs_with_term + 0.5
        return math.log(numerator / denominator + 1.0)

    def score_doc(self, doc_id: int, query_tokens: list[str]) -> float:
        """
        Calculates the BM25 score for a single document given a query.

        Args:
            doc_id (int): The ID of the document to score.
            query_tokens (list[str]): The preprocessed query tokens.

        Returns:
            float: The BM25 score.
        """
        score = 0.0
        doc_len = self.doc_lengths.get(doc_id, 0)
        
        # Create a map of term frequencies for the given doc_id for quick lookup
        term_freqs = {}
        for term in query_tokens:
            postings = self.inverted_index.get(term, [])
            for posting_doc_id, freq in postings:
                if posting_doc_id == doc_id:
                    term_freqs[term] = freq
                    break
        
        for term in query_tokens:
            if term in term_freqs:
                freq = term_freqs[term]
                idf = self._calculate_idf(term)
                
                # BM25's term frequency saturation formula
                numerator = freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_length)
                
                score += idf * (numerator / denominator)
                
        return score