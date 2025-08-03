"""
API views for the Evaluation API.

This module contains Django REST Framework views that handle HTTP requests
for evaluation metrics and image processing.

The views provide:
- RESTful API endpoints with proper HTTP methods
- Comprehensive error handling and validation
- Detailed API documentation
- Consistent JSON response formats
- Request/response logging

Classes:
    SSIMEvaluationView: Handles SSIM calculation requests
    SmoothnessEvaluationView: Handles line smoothness evaluation requests
    ExecutionErrorView: Handles G-code execution error calculation requests
    HealthCheckView: Provides API health status
"""

import logging
import numpy as np
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .serializers import (
    SSIMEvaluationSerializer,
    SmoothnessEvaluationSerializer,
    ExecutionErrorSerializer
)
from .services import EvaluationService

logger = logging.getLogger(__name__)


class SSIMEvaluationView(APIView):
    """
    API endpoint for calculating SSIM (Structural Similarity Index) between two images.
    
    This endpoint compares two images and returns a similarity score between 0 and 1,
    where 1 indicates identical images and 0 indicates completely different images.
    
    **POST /api/evaluate/ssim/**
    
    Request formats:
    1. File upload (multipart/form-data):
       - original_image: Original image file
       - reproduced_image: Reproduced image file
       
    2. Base64 data (application/json):
       - original_image_data: Base64 encoded original image
       - reproduced_image_data: Base64 encoded reproduced image
    
    Response format:
    ```json
    {
        "success": true,
        "ssim_score": 0.8542,
        "message": "SSIM calculated successfully",
        "interpretation": "High similarity"
    }
    ```
    
    **Status Codes:**
    - 200: Calculation successful
    - 400: Bad request (invalid image data)
    - 500: Internal server error
    """
    
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for SSIM calculation."""
        try:
            # Validate request data
            serializer = SSIMEvaluationSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"SSIM validation failed: {serializer.errors}")
                return Response({
                    'success': False,
                    'error': 'Validation error',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Calculate SSIM using the service
            ssim_score = EvaluationService.calculate_ssim(
                original_image=validated_data.get('original_image'), # type: ignore
                reproduced_image=validated_data.get('reproduced_image'), # type: ignore
                original_image_data=validated_data.get('original_image_data'), # type: ignore
                reproduced_image_data=validated_data.get('reproduced_image_data') # type: ignore
            )
            
            # Provide interpretation of the score
            if ssim_score >= 0.9:
                interpretation = "Very high similarity"
            elif ssim_score >= 0.7:
                interpretation = "High similarity"
            elif ssim_score >= 0.5:
                interpretation = "Moderate similarity"
            elif ssim_score >= 0.3:
                interpretation = "Low similarity"
            else:
                interpretation = "Very low similarity"
            
            logger.info(f"SSIM calculation successful: {ssim_score:.4f}")
            
            return Response({
                'success': True,
                'ssim_score': ssim_score,
                'message': 'SSIM calculated successfully',
                'interpretation': interpretation
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"SSIM calculation validation error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Invalid image data',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"SSIM calculation server error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'details': 'An unexpected error occurred during SSIM calculation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SmoothnessEvaluationView(APIView):
    """
    API endpoint for calculating line smoothness score for signature analysis.
    
    This endpoint analyzes an image to determine how smooth the lines are,
    returning a score between 0 and 1, where 1 indicates very smooth lines.
    
    **POST /api/evaluate/smoothness/**
    
    Request formats:
    1. File upload (multipart/form-data):
       - image: Image file to analyze
       
    2. Base64 data (application/json):
       - image_data: Base64 encoded image data
    
    Response format:
    ```json
    {
        "success": true,
        "smoothness_score": 0.7234,
        "message": "Smoothness calculated successfully",
        "interpretation": "Good line smoothness"
    }
    ```
    
    **Status Codes:**
    - 200: Calculation successful
    - 400: Bad request (invalid image data)
    - 500: Internal server error
    """
    
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for smoothness calculation."""
        try:
            # Validate request data
            serializer = SmoothnessEvaluationSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Smoothness validation failed: {serializer.errors}")
                return Response({
                    'success': False,
                    'error': 'Validation error',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Calculate smoothness using the service
            smoothness_score = EvaluationService.calculate_smoothness(
                image=validated_data.get('image'), # type: ignore
                image_data=validated_data.get('image_data') # type: ignore
            )
            
            # Provide interpretation of the score
            if smoothness_score >= 0.8:
                interpretation = "Excellent line smoothness"
            elif smoothness_score >= 0.6:
                interpretation = "Good line smoothness"
            elif smoothness_score >= 0.4:
                interpretation = "Fair line smoothness"
            elif smoothness_score >= 0.2:
                interpretation = "Poor line smoothness"
            else:
                interpretation = "Very poor line smoothness"
            
            logger.info(f"Smoothness calculation successful: {smoothness_score:.4f}")
            
            return Response({
                'success': True,
                'smoothness_score': smoothness_score,
                'message': 'Smoothness calculated successfully',
                'interpretation': interpretation
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Smoothness calculation validation error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Invalid image data',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Smoothness calculation server error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'details': 'An unexpected error occurred during smoothness calculation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExecutionErrorView(APIView):
    """
    API endpoint for calculating G-code execution error between expected and actual toolpaths.
    
    This endpoint compares expected vs actual toolpath coordinates to determine
    execution accuracy, returning mean error and per-point error analysis.
    
    **POST /api/evaluate/execution-error/**
    
    Request format (application/json):
    ```json
    {
        "expected_toolpath": [[0, 0], [10, 10], [20, 20]],
        "actual_toolpath": [[0, 1], [9, 11], [21, 19]]
    }
    ```
    
    Response format:
    ```json
    {
        "success": true,
        "mean_error": 1.2345,
        "individual_errors": [1.0, 1.4142, 1.4142],
        "message": "Execution error calculated successfully",
        "analysis": {
            "max_error": 1.4142,
            "min_error": 1.0,
            "error_std": 0.2357
        }
    }
    ```
    
    **Status Codes:**
    - 200: Calculation successful
    - 400: Bad request (invalid toolpath data)
    - 500: Internal server error
    """
    
    parser_classes = [JSONParser]
    
    def post(self, request, *args, **kwargs):
        """Handle POST request for execution error calculation."""
        try:
            # Validate request data
            serializer = ExecutionErrorSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Execution error validation failed: {serializer.errors}")
                return Response({
                    'success': False,
                    'error': 'Validation error',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # Calculate execution error using the service
            mean_error, individual_errors = EvaluationService.calculate_execution_error(
                expected_toolpath=validated_data['expected_toolpath'], # type: ignore
                actual_toolpath=validated_data['actual_toolpath'] # type: ignore
            )
            
            # Calculate additional statistics
            max_error = max(individual_errors)
            min_error = min(individual_errors)
            error_std = float(np.std(individual_errors)) if individual_errors else 0.0
            
            logger.info(f"Execution error calculation successful: mean={mean_error:.4f}")
            
            return Response({
                'success': True,
                'mean_error': mean_error,
                'individual_errors': individual_errors,
                'message': 'Execution error calculated successfully',
                'analysis': {
                    'max_error': max_error,
                    'min_error': min_error,
                    'error_std': error_std,
                    'total_points': len(individual_errors)
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Execution error calculation validation error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Invalid toolpath data',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Execution error calculation server error: {str(e)}")
            return Response({
                'success': False,
                'error': 'Internal server error',
                'details': 'An unexpected error occurred during execution error calculation'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """
    API endpoint for health check and service information.
    
    **GET /api/health/**
    
    Returns the current status of the Evaluation API service along with available endpoints
    and version information.
    
    Response format:
    ```json
    {
        "status": "healthy",
        "service": "GCode Evaluation API",
        "version": "1.0.0",
        "timestamp": "2024-01-01T12:00:00Z",
        "endpoints": {
            "ssim": "/api/evaluate/ssim/",
            "smoothness": "/api/evaluate/smoothness/",
            "execution_error": "/api/evaluate/execution-error/"
        }
    }
    ```
    """
    
    def get(self, request, *args, **kwargs):
        """Handle GET request for health check."""
        from django.utils import timezone
        
        return Response({
            'status': 'healthy',
            'service': 'GCode Evaluation API',
            'version': '1.0.0',
            'timestamp': timezone.now().isoformat(),
            'endpoints': {
                'ssim': '/api/evaluate/ssim/',
                'smoothness': '/api/evaluate/smoothness/',
                'execution_error': '/api/evaluate/execution-error/'
            }
        }, status=status.HTTP_200_OK)
