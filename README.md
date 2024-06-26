# README

## Run the application locally

To get the application running on your local machine, follow these steps:

### Prerequisites

- Node js
- Python 

### Instructions

Steps to run the code:

1.Unzip the provided file
Start UI:
   Navigate to frontend
   npm install
   npm start

Start Fast API:
   Navigate to backend
   uvicorn app:app --reload
   During the backend service initialization, a ~600MB `sessions.csv` file will be downloaded
   url : http://localhost:3000/

Predicting the results:
Upload any test data (Sample provided in backend/test_data)
Predictions will be provided on screen

Frameworks:
React
FastAPI
Pandas
Random Forest
TFIDF
CountVectorizer

## Roadmap for Future Improvements
1. Implement and fine-tune an Classifier model to improve prediction accuracy.
2. Build new features to improve accuracy of model.
3. Implement explainability like LIME or SHAP
4. Improve UI design
