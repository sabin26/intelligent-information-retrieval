# Intelligent Information Retrieval System

## Setup and Run Instructions

### Prerequisites

-   **Node.js** (for frontend)
-   **Python 3.13+** (for backend)
-   **uv** (recommended) or pip for Python package management

### Step 1: Data Collection (Crawling)

First, crawl the publication data from the source website:

```bash
cd backend/search_engine
python crawler.py
```

This will:

-   Crawl publication data from Coventry University's research portal
-   Respect robots.txt and implement polite crawling delays
-   Extract publication titles, authors, abstracts, and dates
-   Save the data to `backend/search_engine/data/crawled_data.json`

### Step 2: Build Search Index

After crawling, build the search index:

```bash
cd backend/search_engine
python indexer.py
```

This will:

-   Process the crawled data and create positional index
-   Build TF-IDF matrix combining title, author, and abstract
-   Save the index to `backend/search_engine/data/index.joblib`

### Step 3: Train Document Classifier

Train the document classification model:

```bash
cd backend/classification
python classifier.py
```

This will:

-   Load training data from `backend/classification/data/cleaned_data.csv`
-   Train a Naive Bayes classifier with TF-IDF features
-   Evaluate the model using K-fold cross-validation
-   Save the trained model to `backend/classification/data/document_classifier.joblib`

### Step 4: Install Dependencies

#### Backend Dependencies

```bash
# Using pip
pip install -r backend/requirements.txt

# Or using uv (recommended)
uv pip install -r backend/requirements.txt
```

#### Frontend Dependencies

```bash
npm install
```

### Step 5: Run the Application

#### Start the Backend API

```bash
# Using python
python fastapi dev backend/api.py

# Or using uv (recommended)
uv run fastapi dev backend/api.py
```

The backend will be available at http://127.0.0.1:8000 and docs at http://127.0.0.1:8000/docs

#### Start the Frontend

```bash
npm run dev
```

The frontend will be available at http://localhost:5173/

## Complete Workflow Summary

1. **Crawl Data**: `python backend/search_engine/crawler.py`
2. **Build Index**: `python backend/search_engine/indexer.py`
3. **Train Classifier**: `python backend/classification/classifier.py`
4. **Install Dependencies**: `pip install -r backend/requirements.txt` and `npm install`
5. **Run Backend**: `python fastapi dev backend/api.py`
6. **Run Frontend**: `npm run dev`

## Features

-   **Web Crawling**: Automated data collection from research publications
-   **Search Engine**: Field-based search with TF-IDF ranking and phrase queries
-   **Document Classification**: Automatic categorization of research documents
-   **Interactive Web Interface**: Modern React-based frontend for search and exploration

## Data Files Structure

```
backend/
├── search_engine/
│   └── data/
│       ├── crawled_data.json     # Raw crawled publication data
│       └── index.joblib          # Search index and TF-IDF model
└── classification/
    └── data/
        ├── cleaned_data.csv      # Training data for classifier
        └── document_classifier.joblib  # Trained classification model
```
