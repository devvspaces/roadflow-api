from django.apps import AppConfig


class CurriculumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Curriculum'

    def ready(self):
        # Preload the model when the app starts
        from utils.base.ml_loader import ModelLoader
        ModelLoader()
