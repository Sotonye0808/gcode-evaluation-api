"""
Evaluation Modules Package

This package contains modules for evaluating signature quality and G-code execution accuracy.
Each module provides specific evaluation metrics for different aspects of the signature
analysis and G-code execution pipeline.

Modules:
    ssim: Structural Similarity Index calculation for image comparison
    line_smoothness: Line smoothness analysis for signature quality
    gcode_error: G-code execution error calculation for accuracy measurement

The modules can be used independently or through the Django API endpoints.

Usage:
    from evaluation_modules.ssim import compute_ssim
    from evaluation_modules.line_smoothness import smoothness_test
    from evaluation_modules.gcode_error import execution_error
    
    # Calculate SSIM between two images
    ssim_score = compute_ssim("original.jpg", "reproduced.jpg")
    
    # Calculate line smoothness
    smoothness_score = smoothness_test("signature.jpg")
    
    # Calculate execution error
    mean_error, errors = execution_error(expected_path, actual_path)
"""

__version__ = "1.0.0"
__author__ = "Sotonye Dagogo"

# Import main functions for convenience
from .ssim import compute_ssim
from .line_smoothness import smoothness_test
from .gcode_error import execution_error

__all__ = [
    'compute_ssim',
    'smoothness_test', 
    'execution_error'
]
