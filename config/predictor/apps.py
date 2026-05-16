from django.apps import AppConfig
import os
from django.conf import settings
import pickle
from django.apps import AppConfig


class PredictorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictor'
    ml_model = None

    def ready(self):
        model_path = os.path.join(settings.BASE_DIR, 'predictor', 'ml_models', 'house_price_model.pkl')

        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.ml_model = pickle.load(f)