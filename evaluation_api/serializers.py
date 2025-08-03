"""
Serializers for the Evaluation API.

This module contains Django REST Framework serializers that handle
data validation and serialization for evaluation endpoints.

The serializers provide:
- Input validation for evaluation requests
- Data transformation and cleaning
- Error handling for invalid data
- Documentation for API request/response formats

Classes:
    SSIMEvaluationSerializer: Handles image comparison inputs
    SmoothnessEvaluationSerializer: Handles image smoothness analysis input
    ExecutionErrorSerializer: Handles toolpath comparison inputs
"""

from rest_framework import serializers
import base64
import numpy as np


class SSIMEvaluationSerializer(serializers.Serializer):
    """
    Serializer for SSIM (Structural Similarity Index) evaluation endpoint.
    
    Accepts two images for comparison either as file uploads or base64 encoded data.
    Validates image formats and ensures both images are provided.
    
    Fields:
        original_image (FileField, optional): Original image file
        reproduced_image (FileField, optional): Reproduced image file
        original_image_data (CharField, optional): Base64 encoded original image
        reproduced_image_data (CharField, optional): Base64 encoded reproduced image
        
    Validation:
        - Both original and reproduced images must be provided
        - Images must be in supported formats (PNG, JPG, JPEG, BMP, TIFF, GIF)
        - Base64 data must be valid if provided
    """
    original_image = serializers.FileField(required=False, help_text="Original image file")
    reproduced_image = serializers.FileField(required=False, help_text="Reproduced image file")
    original_image_data = serializers.CharField(required=False, help_text="Base64 encoded original image")
    reproduced_image_data = serializers.CharField(required=False, help_text="Base64 encoded reproduced image")
    
    def validate(self, data):
        """Validate that both images are provided in some form."""
        has_files = data.get('original_image') and data.get('reproduced_image')
        has_data = data.get('original_image_data') and data.get('reproduced_image_data')
        
        if not has_files and not has_data:
            raise serializers.ValidationError(
                "Both original and reproduced images must be provided either as files or base64 data."
            )
            
        # Validate file extensions if files are provided
        if has_files:
            # Updated to match service layer supported formats including SVG
            valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif', '.svg']
            for field_name in ['original_image', 'reproduced_image']:
                file = data[field_name]
                if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                    raise serializers.ValidationError(
                        f"{field_name} must be a PNG, JPEG, BMP, TIFF, GIF, or SVG file."
                    )
        
        # Validate base64 data if provided
        if has_data:
            try:
                for field_name in ['original_image_data', 'reproduced_image_data']:
                    base64_data = data[field_name]
                    # Remove data URL prefix if present
                    if ',' in base64_data:
                        base64_data = base64_data.split(',')[1]
                    
                    # Validate base64 format
                    if not base64_data.strip():
                        raise serializers.ValidationError(
                            f"Empty base64 data provided for {field_name}."
                        )
                    
                    base64.b64decode(base64_data.strip(), validate=True)
            except Exception as e:
                raise serializers.ValidationError(
                    f"Invalid base64 image data provided: {str(e)}"
                )
                
        return data


class SmoothnessEvaluationSerializer(serializers.Serializer):
    """
    Serializer for line smoothness evaluation endpoint.
    
    Accepts a single image for smoothness analysis either as file upload or base64 data.
    
    Fields:
        image (FileField, optional): Image file to analyze
        image_data (CharField, optional): Base64 encoded image data
        
    Validation:
        - One of image or image_data must be provided
        - Image must be in supported format (PNG, JPG, JPEG, BMP, TIFF, GIF)
        - Base64 data must be valid if provided
    """
    image = serializers.FileField(required=False, help_text="Image file to analyze for smoothness")
    image_data = serializers.CharField(required=False, help_text="Base64 encoded image data")
    
    def validate(self, data):
        """Validate that an image is provided."""
        if not data.get('image') and not data.get('image_data'):
            raise serializers.ValidationError(
                "Either 'image' or 'image_data' must be provided."
            )
            
        # Validate file extension if file is provided
        if data.get('image'):
            file = data['image']
            # Updated to match service layer supported formats including SVG
            valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif', '.svg']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise serializers.ValidationError(
                    "Image must be a PNG, JPEG, BMP, TIFF, GIF, or SVG file."
                )
        
        # Validate base64 data if provided
        if data.get('image_data'):
            try:
                base64_data = data['image_data']
                # Remove data URL prefix if present
                if ',' in base64_data:
                    base64_data = base64_data.split(',')[1]
                
                # Validate base64 format
                if not base64_data.strip():
                    raise serializers.ValidationError(
                        "Empty base64 data provided."
                    )
                
                base64.b64decode(base64_data.strip(), validate=True)
            except Exception as e:
                raise serializers.ValidationError(
                    f"Invalid base64 image data provided: {str(e)}"
                )
                
        return data


class ExecutionErrorSerializer(serializers.Serializer):
    """
    Serializer for G-code execution error evaluation endpoint.
    
    Accepts expected and actual toolpath data for comparison analysis.
    
    Fields:
        expected_toolpath (ListField): Expected toolpath coordinates
        actual_toolpath (ListField): Actual executed toolpath coordinates
        
    Validation:
        - Both toolpaths must be provided
        - Toolpaths must be arrays of [x, y] coordinate pairs
        - Coordinate arrays must have the same length
        - All coordinates must be numeric
    """
    expected_toolpath = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField(),
            min_length=2,
            max_length=2
        ),
        help_text="Expected toolpath as array of [x, y] coordinates"
    )
    actual_toolpath = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField(),
            min_length=2,
            max_length=2
        ),
        help_text="Actual toolpath as array of [x, y] coordinates"
    )
    
    def validate(self, data):
        """Validate that toolpaths have matching dimensions."""
        expected = data.get('expected_toolpath', [])
        actual = data.get('actual_toolpath', [])
        
        if len(expected) != len(actual):
            raise serializers.ValidationError(
                "Expected and actual toolpaths must have the same number of points."
            )
            
        if len(expected) == 0:
            raise serializers.ValidationError(
                "Toolpaths cannot be empty."
            )
            
        return data