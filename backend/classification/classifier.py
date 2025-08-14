import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, f1_score, confusion_matrix
from config import DATA_FILE, MODEL_FILE
import matplotlib.pyplot as plt
import seaborn as sns

def load_data_from_csv(file_path: str) -> tuple[list, list, list]:
    """
    Loads and processes data from a CSV file.

    The CSV is expected to have 'Title', 'Content', and 'Category' columns.
    'Title' and 'Content' are combined to form the document text.

    Args:
        file_path (str): The path to the CSV data file.

    Returns:
        A tuple containing:
        - texts (list): A list of combined document texts.
        - labels (list): A list of numerical labels.
        - label_names (list): A list of the string names of the labels.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Data file not found at '{file_path}'.")
        print("Please make sure the CSV file is in the same directory.")
        return list(), list(), list()

    print("--- Data Loaded Successfully ---")
    print("DataFrame Info:")
    df.info()
    print("\nFirst 5 rows of the DataFrame:")
    print(df.head())
    print("-" * 30)

    # Drop rows with missing values in key columns
    df.dropna(subset=['Title', 'Content', 'Category'], inplace=True)
    
    # Combine Title and Content into a single text feature
    df['text'] = df['Title'] + " " + df['Content']
    
    texts = df['text'].tolist()
    
    # Convert string labels to numerical labels
    # pd.factorize: it returns integer codes and the unique labels
    labels, label_names = pd.factorize(df['Category'])
    
    print(f"Loaded {len(texts)} documents.")
    print(f"Found categories: {list(label_names)}")
    
    return texts, labels.tolist(), list(label_names)

def plot_confusion_matrix(cm, class_names):
    """
    Renders a confusion matrix using Seaborn.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names, ax=ax)
    plt.title('Confusion Matrix')
    plt.ylabel('Actual Category')
    plt.xlabel('Predicted Category')
    
    # Show the plot
    plt.show()

def train_and_evaluate(texts: list, labels: list, label_names: list):
    """
    Trains a classifier, evaluates its performance with detailed metrics
    and plots, and returns the trained pipeline.
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
    
    # Calculate and print Accuracy and F1-Score
    accuracy = accuracy_score(y_test, y_pred)
    # Use 'macro' average for F1-score to treat all classes equally
    f1 = f1_score(y_test, y_pred, average='macro') 
    
    print(f"Accuracy on test set: {accuracy:.4f}")
    print(f"Macro F1-Score on test set: {f1:.4f}")
    
    # Print the detailed Classification Report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_names))
    
    # Calculate and plot the Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plot_confusion_matrix(cm, label_names)
    
    # 5. Now, train the final model on ALL data for production use
    print("\nRetraining the model on the full dataset for production...")
    final_model = model_pipeline.fit(texts, labels)
    
    return final_model

def main():
    """
    Main function to run the classifier.
    It loads a pre-trained model or trains a new one from the CSV file.
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
        print("No pre-trained model found. Training a new one from CSV.")
        # Load data from CSV
        texts, labels, label_names_from_data = load_data_from_csv(DATA_FILE)
        
        if not texts:
            print("\nExiting: Could not load data.")
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