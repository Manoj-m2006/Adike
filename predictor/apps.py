"""
Django Application Configuration for the Predictor app.
"""

from django.apps import AppConfig


class PredictorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictor'
    verbose_name = 'Arecanut Disease Predictor'

    def ready(self):
        """
        App ready lifecycle hook.
        Optionally pre-warms the singleton ResNet-50 inference engine.
        """
        import os
        from predictor.config import MODEL_PATH

        # Avoid double execution during Django reloader checks
        if os.environ.get('RUN_MAIN') == 'true' or not os.environ.get('DJANGO_SETTINGS_MODULE'):
            if MODEL_PATH.exists():
                try:
                    from predictor.ml_model import get_inference_engine
                    # Pre-warm model in memory for instant first request
                    get_inference_engine()
                except Exception as e:
                    # Model will be loaded on demand if startup initialization meets an error
                    pass
