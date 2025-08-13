from sklearn.metrics.pairwise import cosine_similarity

class TfIdfRanker:
    """
    Implements ranking based on TF-IDF and Cosine Similarity.
    """
    def __init__(self, vectorizer, tfidf_matrix):
        """
        Initializes the ranker with the fitted vectorizer and document matrix.

        Args:
            vectorizer: The fitted TfidfVectorizer object.
            tfidf_matrix: The sparse matrix of TF-IDF vectors for all documents.
        """
        self.vectorizer = vectorizer
        self.tfidf_matrix = tfidf_matrix

    def rank_documents(self, query: str) -> list[tuple[int, float]]:
        """
        Ranks all documents in the corpus against a query.

        Args:
            query (str): The user's search query.

        Returns:
            A list of (doc_id, score) tuples, sorted by score descending.
        """
        if not query:
            return []

        # 1. Transform the query into a TF-IDF vector using the existing vectorizer
        query_vector = self.vectorizer.transform([query])
        
        # 2. Compute cosine similarity between the query vector and all doc vectors
        # This returns a 2D array, so we take the first (and only) row
        cosine_scores = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        # 3. Create a list of (doc_id, score) tuples for docs with score > 0
        doc_scores = [
            (doc_id, score) for doc_id, score in enumerate(cosine_scores) if score > 0
        ]
        
        # 4. Sort the documents by score in descending order
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        return doc_scores