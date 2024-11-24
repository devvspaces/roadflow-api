import joblib

# Load the model
model = joblib.load('naive_bayes_model.pkl')

# Load the vectorizer
vectorizer = joblib.load('tfidf_vectorizer.pkl')

# Predict on new text
new_text = "The course videos are very engaging and kept me motivated throughout!"
new_text_vector = vectorizer.transform([new_text.lower()])
predicted_category = model.predict(new_text_vector)[0]
print(f"Predicted category: {predicted_category}")