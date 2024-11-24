import os

import joblib
from django.conf import settings


class ModelLoader:
    _instance = None
    _model = None
    _vectorizer = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls.load_models()
        return cls._instance

    @classmethod
    def load_models(cls):
        # Construct full paths to model files
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'naive_bayes_model.pkl')
        vectorizer_path = os.path.join(settings.BASE_DIR, 'ml_models', 'tfidf_vectorizer.pkl')

        # Load model and vectorizer
        cls._model = joblib.load(model_path)
        cls._vectorizer = joblib.load(vectorizer_path)
        print("Models loaded successfully")

    @classmethod
    def predict(cls, text) -> str:
        # Ensure models are loaded
        if cls._model is None or cls._vectorizer is None:
            cls.load_models()
        
        # Preprocess and predict
        text_vector = cls._vectorizer.transform([text.lower()])
        return cls._model.predict(text_vector)[0]

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls.load_models()
        return cls._model

    @classmethod
    def get_vectorizer(cls):
        if cls._vectorizer is None:
            cls.load_models()
        return cls._vectorizer