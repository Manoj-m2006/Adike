"""
URL Patterns for the Predictor app.
"""

from django.urls import path
from predictor import views

app_name = 'predictor'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
]
