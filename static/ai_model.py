from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Training data
texts = [
    "This product is excellent",
    "This product is very good",
    "I really like this product",
    "The product is amazing",
    "This product is bad",
    "This product is very poor",
    "I don't like this product",
    "The product is terrible"
]

labels = [
    "Positive",
    "Positive",
    "Positive",
    "Positive",
    "Negative",
    "Negative",
    "Negative",
    "Negative"
]

# Convert text into numbers
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# Train the AI model
model = LogisticRegression()
model.fit(X, labels)


def predict_label(text):
    text_vector = vectorizer.transform([text])
    prediction = model.predict(text_vector)

    return prediction[0]