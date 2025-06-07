import openai
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

class MLTriageService:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        self.classifier = self._build_classifier_pipeline()
        
    def _build_classifier_pipeline(self):
        return Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('clf', RandomForestClassifier(n_estimators=100))
        ])
    
    def train_model(self, training_data_path):
        df = pd.read_csv(training_data_path)
        X_train, X_test, y_train, y_test = train_test_split(
            df['description'], df['label'], test_size=0.2
        )
        self.classifier.fit(X_train, y_train)
        return self.classifier.score(X_test, y_test)
    
    def predict_with_llm(self, case_description):
        openai.api_key = self.openai_api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial case triage system. Classify this case into one of: Fraud, Account Lockout, Transaction Dispute, or Other."},
                {"role": "user", "content": case_description}
            ]
        )
        return response.choices[0].message['content']
    
    def hybrid_predict(self, case_description):
        # Rule-based checks first
        if "lock" in case_description.lower():
            return "LOCKOUT", 0.95
        
        # ML prediction
        ml_pred = self.classifier.predict_proba([case_description])
        
        # LLM prediction for uncertain cases
        if ml_pred.max() < 0.7:
            llm_pred = self.predict_with_llm(case_description)
            return llm_pred, 0.8  # Default confidence for LLM
        
        return self.classifier.classes_[ml_pred.argmax()], ml_pred.max()