from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from helpers import initialize_assets
from prediction import Predictor

# Allowed origins for CORS configuration
origins = [
    "http://localhost:3000",
    "http://localhost"
]

# Create a FastAPI instance
app = FastAPI()

# Configure CORS middleware for the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize assets from helper functions
try:
    tfidf_vectorizers, one_hot_encoders, count_vectorizer, final_columns, classifier, label_encoder = initialize_assets()
except Exception as e:
    # Log or handle exception during asset initialization
    print(f"Error initializing assets: {e}")

# Endpoint to process and predict data from uploaded file
@app.post("/predict/")
def predict(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        # Handle errors related to file reading
        return {"error": f"Failed to read file: {e}"}

    try:
        predictor = Predictor(df)
        preprocessed_df, user_id = predictor.preprocess(tfidf_vectorizers, count_vectorizer, one_hot_encoders, final_columns)
        records = predictor.predict(classifier, preprocessed_df, label_encoder, user_id)
        return records
    except Exception as e:
        # Handle errors from preprocessing or prediction
        return {"error": f"Prediction process failed: {e}"}
