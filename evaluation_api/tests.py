"""
Tests for the Evaluation API.

This module contains unit tests for the API endpoints and services.
Tests cover all evaluation endpoints with various input scenarios.
"""

import json
import base64
from io import BytesIO
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class HealthCheckTestCase(APITestCase):
    """Test cases for the health check endpoint."""
    
    def test_health_check(self):
        """Test that health check returns correct response."""
        url = reverse('evaluation_api:health-check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'GCode Evaluation API')
        self.assertIn('endpoints', data)


class SSIMEvaluationTestCase(APITestCase):
    """Test cases for SSIM evaluation endpoint."""
    
    def setUp(self):
        """Set up test data."""
        # Create a small test image
        self.test_image = Image.new('RGB', (10, 10), color='white') # type: ignore
        self.test_image_bytes = BytesIO()
        self.test_image.save(self.test_image_bytes, format='PNG')
        self.test_image_bytes.seek(0)
        
        # Create base64 encoded image data
        self.test_image_b64 = base64.b64encode(self.test_image_bytes.getvalue()).decode('utf-8')
    
    def test_ssim_with_base64_data(self):
        """Test SSIM calculation with base64 image data."""
        url = reverse('evaluation_api:ssim-evaluation')
        data = {
            'original_image_data': self.test_image_b64,
            'reproduced_image_data': self.test_image_b64
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('ssim_score', response_data)
        self.assertGreaterEqual(response_data['ssim_score'], 0.0)
        self.assertLessEqual(response_data['ssim_score'], 1.0)
    
    def test_ssim_missing_data(self):
        """Test SSIM endpoint with missing image data."""
        url = reverse('evaluation_api:ssim-evaluation')
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertFalse(response_data['success'])
        self.assertIn('error', response_data)


class SmoothnessEvaluationTestCase(APITestCase):
    """Test cases for smoothness evaluation endpoint."""
    
    def setUp(self):
        """Set up test data."""
        # Create a small test image
        self.test_image = Image.new('RGB', (10, 10), color='white') # type: ignore
        self.test_image_bytes = BytesIO()
        self.test_image.save(self.test_image_bytes, format='PNG')
        self.test_image_bytes.seek(0)
        
        # Create base64 encoded image data
        self.test_image_b64 = base64.b64encode(self.test_image_bytes.getvalue()).decode('utf-8')
    
    def test_smoothness_with_base64_data(self):
        """Test smoothness calculation with base64 image data."""
        url = reverse('evaluation_api:smoothness-evaluation')
        data = {
            'image_data': self.test_image_b64
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('smoothness_score', response_data)
        self.assertGreaterEqual(response_data['smoothness_score'], 0.0)
        self.assertLessEqual(response_data['smoothness_score'], 1.0)
    
    def test_smoothness_missing_data(self):
        """Test smoothness endpoint with missing image data."""
        url = reverse('evaluation_api:smoothness-evaluation')
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertFalse(response_data['success'])


class ExecutionErrorTestCase(APITestCase):
    """Test cases for execution error evaluation endpoint."""
    
    def test_execution_error_calculation(self):
        """Test execution error calculation with valid toolpath data."""
        url = reverse('evaluation_api:execution-error')
        data = {
            'expected_toolpath': [[0, 0], [10, 10], [20, 20]],
            'actual_toolpath': [[0, 1], [9, 11], [21, 19]]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertIn('mean_error', response_data)
        self.assertIn('individual_errors', response_data)
        self.assertIn('analysis', response_data)
        self.assertGreaterEqual(response_data['mean_error'], 0.0)
    
    def test_execution_error_mismatched_lengths(self):
        """Test execution error with mismatched toolpath lengths."""
        url = reverse('evaluation_api:execution-error')
        data = {
            'expected_toolpath': [[0, 0], [10, 10]],
            'actual_toolpath': [[0, 1], [9, 11], [21, 19]]
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertFalse(response_data['success'])
    
    def test_execution_error_missing_data(self):
        """Test execution error endpoint with missing toolpath data."""
        url = reverse('evaluation_api:execution-error')
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.json()
        self.assertFalse(response_data['success'])


class APIRootTestCase(APITestCase):
    """Test cases for the API root endpoint."""
    
    def test_api_root(self):
        """Test that API root returns service information."""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['service'], 'GCode Evaluation API')
        self.assertIn('endpoints', data)
        self.assertIn('version', data)
