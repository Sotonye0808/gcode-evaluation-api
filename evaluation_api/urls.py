"""
URL configuration for the evaluation_api app.

This module defines the URL patterns that map HTTP requests to view functions
for the Evaluation API endpoints.

URL Patterns:
    - evaluate/ssim/ : SSIM calculation endpoint
    - evaluate/smoothness/ : Line smoothness evaluation endpoint  
    - evaluate/execution-error/ : G-code execution error calculation endpoint
    - health/ : Health check endpoint
"""

from django.urls import path
from .views import (
    SSIMEvaluationView,
    SmoothnessEvaluationView,
    ExecutionErrorView,
    HealthCheckView
)

app_name = 'evaluation_api'

urlpatterns = [
    # Evaluation endpoints
    path('evaluate/ssim/', SSIMEvaluationView.as_view(), name='ssim-evaluation'),
    path('evaluate/smoothness/', SmoothnessEvaluationView.as_view(), name='smoothness-evaluation'),
    path('evaluate/execution-error/', ExecutionErrorView.as_view(), name='execution-error'),
    
    # Health check endpoint
    path('health/', HealthCheckView.as_view(), name='health-check'),
]
