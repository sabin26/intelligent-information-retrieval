from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from contextlib import asynccontextmanager
from search_engine import SearchEngine
from classification import load_classifier_and_labels

# This dictionary will hold machine learning models
# to avoid reloading them on every request.
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This code runs on startup
    print("--- Loading ML models ---")
    
    # Load the Search Engine Index
    ml_models["search_engine"] = SearchEngine()
    
    # Load the Document Classifier
    classifier, labels = load_classifier_and_labels()
    ml_models["classifier"] = classifier
    ml_models["classifier_labels"] = labels
    
    print("--- Models loaded successfully ---")
    
    yield
    
    # This code runs on shutdown
    print("--- Clearing ML models ---")
    ml_models.clear()

# Initialize the FastAPI app with the lifespan manager
app = FastAPI(lifespan=lifespan)

# --- Define Pydantic models for request and response bodies ---

class Document(BaseModel):
    text: str

class ClassificationResponse(BaseModel):
    category: str
    confidence: float

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Search and Classification API"}

@app.get("/search")
async def search(q: str = Query(..., min_length=3, description="The search query string.")):
    """
    Performs a search using the loaded search engine index.
    Handles both bag-of-words and "quoted phrase" searches.
    """
    if "search_engine" not in ml_models:
        raise HTTPException(status_code=503, detail="Search engine is not available.")
    
    try:
        results = ml_models["search_engine"].search(q)
        return {"query": q, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during search: {e}")


@app.post("/classify", response_model=ClassificationResponse)
async def classify(document: Document):
    """
    Classifies a given text into one of the pre-trained categories
    (Business, Health, Politics).
    """
    if "classifier" not in ml_models or "classifier_labels" not in ml_models:
        raise HTTPException(status_code=503, detail="Classifier is not available.")
        
    try:
        text_to_classify = document.text
        
        # Predict the category index and probabilities
        classifier = ml_models["classifier"]
        labels = ml_models["classifier_labels"]
        
        prediction_index = classifier.predict([text_to_classify])[0]
        probabilities = classifier.predict_proba([text_to_classify])[0]
        
        # Get the results
        category = labels[prediction_index]
        confidence = probabilities[prediction_index]
        
        return {"category": category, "confidence": confidence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during classification: {e}")