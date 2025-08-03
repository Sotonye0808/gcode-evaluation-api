"""
Django app configuration for Evaluation API.

This module defines the configuration for the evaluation_api Django app.
It sets the app name and default auto field type.
"""

from django.apps import AppConfig


class EvaluationApiConfig(AppConfig):
    """
    Configuration class for the Evaluation API app.
    
    This class configures the app settings including the default auto field
    type and the app name used throughout the Django project.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'evaluation_api'
    verbose_name = 'Evaluation API'
