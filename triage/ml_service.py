from openai import OpenAI
from typing import Optional, Tuple

class MLTriageService:
    VALID_LABELS = {"FRAUD", "LOCKOUT", "DISPUTE", "OTHER"}

    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        self._openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.classifier = self._build_classifier_pipeline()
        self._is_trained = False
        
    def _build_classifier_pipeline(self):
        # Import heavy ML deps lazily so Django startup stays snappy.
        from sklearn.pipeline import Pipeline
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.ensemble import RandomForestClassifier

        return Pipeline(
            [
                ("tfidf", TfidfVectorizer()),
                ("clf", RandomForestClassifier(n_estimators=100)),
            ]
        )
    
    def train_model(self, training_data_path):
        import pandas as pd
        from sklearn.model_selection import train_test_split

        df = pd.read_csv(training_data_path)
        X_train, X_test, y_train, y_test = train_test_split(
            df['description'], df['label'], test_size=0.2
        )
        self.classifier.fit(X_train, y_train)
        self._is_trained = True
        return self.classifier.score(X_test, y_test)
    
    def predict_with_llm(self, case_description: str) -> str:
        if not self._openai_client:
            return "OTHER"

        response = self._openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial case triage system. "
                        "Classify this case into one of: Fraud, Account Lockout, Transaction Dispute, or Other. "
                        "Respond with exactly one label."
                    ),
                },
                {"role": "user", "content": case_description},
            ],
        )
        raw = (response.choices[0].message.content or "").strip()
        normalized = raw.upper()

        # Be tolerant: map model output to one of our labels.
        if "FRAUD" in normalized:
            return "FRAUD"
        if "LOCK" in normalized:
            return "LOCKOUT"
        if "DISPUT" in normalized:
            return "DISPUTE"
        if "OTHER" in normalized:
            return "OTHER"

        # Last resort: treat anything unknown as OTHER to keep DB constraints valid.
        return "OTHER"
    
    def hybrid_predict(self, case_description: str) -> Tuple[str, float]:
        # Rule-based checks first
        if "lock" in case_description.lower():
            return "LOCKOUT", 0.95
        
        # ML prediction (only if trained)
        if self._is_trained:
            ml_pred = self.classifier.predict_proba([case_description])
        else:
            ml_pred = None
        
        # LLM prediction for uncertain cases
        if ml_pred is None:
            llm_pred = self.predict_with_llm(case_description)
            return llm_pred, 0.4
        if ml_pred.max() < 0.7:
            llm_pred = self.predict_with_llm(case_description)
            return llm_pred, 0.8  # Default confidence for LLM
        
        return self.classifier.classes_[ml_pred.argmax()], ml_pred.max()