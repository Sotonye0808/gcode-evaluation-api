"""
Main URL configuration for the GCode Evaluation API.

This service handles all image processing and evaluation metrics.
It provides stateless endpoints for signature analysis and evaluation.

The API provides the following main endpoints:
- /api/evaluate/ - All evaluation metric endpoints
- /api/health/ - Health check
- /admin/ - Django admin interface (minimal)

For more information on URL patterns, see:
https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    """Root API endpoint providing service information and available endpoints."""
    return JsonResponse({
        'service': 'GCode Evaluation API',
        'version': '1.0.0',
        'description': 'API for evaluating G-code generation quality through image processing and analysis',
        'endpoints': {
            'health': '/api/health/',
            'ssim_evaluation': '/api/evaluate/ssim/',
            'smoothness_evaluation': '/api/evaluate/smoothness/',
            'execution_error': '/api/evaluate/execution-error/',
        },
        'documentation': '/admin/',
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('evaluation_api.urls')),
    path('', api_root, name='api-root'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
