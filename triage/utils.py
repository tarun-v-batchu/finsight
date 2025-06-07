import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# GPT-based classification
def classify_with_gpt(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Classify financial support tickets"},
                  {"role": "user", "content": text}],
    )
    return response.choices[0].message.content.strip()

# ML-based backup classification
def classify_with_ml(text, model, vectorizer):
    X = vectorizer.transform([text])
    return model.predict(X)[0]
