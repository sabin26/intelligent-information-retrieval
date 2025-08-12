import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Initialize components once to be efficient
STOP_WORDS = set(stopwords.words('english'))
STEMMER = PorterStemmer()

def process_text(text: str) -> list[str]:
    """
    Cleans and preprocesses a piece of text.
    
    The pipeline is:
    1. Convert to lowercase.
    2. Tokenize the text into words.
    3. Remove punctuation and non-alphanumeric characters.
    4. Remove common English stopwords.
    5. Apply Porter stemming to reduce words to their root form.

    Args:
        text (str): The input string to process.

    Returns:
        list[str]: A list of processed tokens.
    """
    if not isinstance(text, str):
        return []
        
    # 1. Lowercasing
    text = text.lower()
    
    # 2. Tokenization
    tokens = word_tokenize(text)
    
    # 3-5. Filtering, stopword removal, and stemming in one loop for efficiency
    processed_tokens = []
    for token in tokens:
        # Keep only alphabetic tokens
        if token.isalpha():
            # Remove stopwords
            if token not in STOP_WORDS:
                # Stem the token
                stemmed_token = STEMMER.stem(token)
                processed_tokens.append(stemmed_token)
                
    return processed_tokens

if __name__ == '__main__':
    # Example usage
    sample_text = "This is a sample text about Information Retrieval, showing tokenization and stemming."
    processed = process_text(sample_text)
    print(f"Original: {sample_text}")
    print(f"Processed: {processed}")
    # Expected output: ['sampl', 'text', 'inform', 'retriev', 'show', 'token', 'stem']