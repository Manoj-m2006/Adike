"""
URL Patterns for the Predictor app.
"""

from django.urls import path
from predictor import views

app_name = 'predictor'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('api/translate/', views.translate_api_view, name='translate_api'),
    path('api/save-key/', views.save_gemini_key_view, name='save_gemini_key'),
]
