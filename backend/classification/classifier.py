import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from config import DATA_DIR, MODEL_FILE

def load_data(data_path: str) -> tuple[list, list, list]:
    """
    Loads text data from a directory structure.

    Assumes that `data_path` contains subdirectories, where each subdirectory
    is a category, and each file in it is a document.

    Args:
        data_path (str): The path to the data directory.

    Returns:
        A tuple containing:
        - texts (list): A list of document texts.
        - labels (list): A list of numerical labels corresponding to the texts.
        - label_names (list): A list of the string names of the labels.
    """
    texts = []
    labels = []
    label_names = sorted([d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))])
    label_map = {name: i for i, name in enumerate(label_names)}

    print(f"Loading data... Found categories: {label_names}")

    for label_name in label_names:
        category_path = os.path.join(data_path, label_name)
        for filename in os.listdir(category_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(category_path, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        texts.append(f.read())
                        labels.append(label_map[label_name])
                except Exception as e:
                    print(f"Warning: Could not read file {file_path}: {e}")
    
    print(f"Loaded {len(texts)} documents.")
    return texts, labels, label_names

def train_and_evaluate(texts: list, labels: list, label_names: list):
    """
    Trains a classifier, evaluates its performance, and returns the trained pipeline.
    """
    # 1. Split data for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # 2. Create the Scikit-learn Pipeline
    # This chains the text vectorizer and the classifier together.
    # TfidfVectorizer handles tokenization, stopword removal, and TF-IDF weighting.
    model_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_df=0.95, min_df=2)),
        ('clf', MultinomialNB(alpha=0.1))
    ])
    
    # 3. Train the model
    print("\nTraining the model...")
    model_pipeline.fit(X_train, y_train)
    
    # 4. Evaluate the model on the test set
    print("\nEvaluating model performance...")
    y_pred = model_pipeline.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy on test set: {accuracy:.4f}")
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_names))
    
    # 5. Now, train the final model on ALL data for production use
    print("\nRetraining the model on the full dataset for production...")
    final_model = model_pipeline.fit(texts, labels)
    
    return final_model

def main():
    """
    Main function to run the classifier.
    It loads a pre-trained model or trains a new one if not found.
    """
    classifier = None
    label_names = []

    # Check if a trained model already exists
    if os.path.exists(MODEL_FILE):
        print(f"Loading pre-trained model from {MODEL_FILE}...")
        data = joblib.load(MODEL_FILE)
        classifier = data['model']
        label_names = data['labels']
        print("Model loaded successfully.")
    else:
        print("No pre-trained model found. Training a new one.")
        # Load data from the directory structure
        texts, labels, label_names_from_data = load_data(DATA_DIR)
        
        if not texts:
            print("\nError: No data found. Please follow the instructions in README_DATA.md")
            return
            
        label_names = label_names_from_data
        
        # Train, evaluate, and get the final model
        classifier = train_and_evaluate(texts, labels, label_names)
        
        # Save the trained model and label names for future use
        print(f"\nSaving model to {MODEL_FILE}...")
        joblib.dump({'model': classifier, 'labels': label_names}, MODEL_FILE)
        print("Model saved.")

    # --- Interactive Prediction Loop ---
    print("\n--- Document Classifier Ready ---")
    print("Enter a sentence or a paragraph to classify.")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        user_input = input("\nEnter text> ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        if not user_input.strip():
            continue

        # Use the trained pipeline to predict
        predicted_label_index = classifier.predict([user_input])[0]
        predicted_label_name = label_names[predicted_label_index]
        
        # Get probability estimates
        probabilities = classifier.predict_proba([user_input])[0]
        confidence = probabilities[predicted_label_index]
        
        print(f"\n=> Predicted Category: ** {predicted_label_name.upper()} **")
        print(f"   Confidence: {confidence:.2%}")

if __name__ == '__main__':
    main()