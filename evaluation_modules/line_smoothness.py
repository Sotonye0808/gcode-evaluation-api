"""
Line Smoothness Evaluation Module

This module provides functionality to calculate the smoothness score of lines
in signature images or other line-based drawings.

The smoothness is calculated by analyzing the curvature variance along contours
in the image. Lower variance indicates smoother, more consistent lines.

Functions:
    smoothness_test: Calculate line smoothness score for an image

Usage:
    from evaluation_modules.line_smoothness import smoothness_test
    
    # Calculate smoothness for an image
    score = smoothness_test("path/to/signature.jpg")
    print(f"Smoothness score: {score:.4f}")
    
    # Interpret the score
    if score >= 0.8:
        print("Excellent line quality")
    elif score >= 0.6:
        print("Good line quality")
    else:
        print("Poor line quality")
"""

import numpy as np
import cv2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
common_dir = os.getenv("COMMON_DIR")

def smoothness_test(image_path):
    """
    Calculate the smoothness score for lines in an image.
    
    This function analyzes the curvature variance of contours in an image
    to determine how smooth and consistent the lines are. The score ranges
    from 0 to 1, where higher values indicate smoother lines.
    
    Args:
        image_path (str): Path to the image file to analyze
        
    Returns:
        float: Smoothness score between 0 and 1
            - Values close to 1 indicate very smooth lines
            - Values close to 0 indicate jagged or inconsistent lines
            
    Raises:
        FileNotFoundError: If the image file does not exist
        ValueError: If the image cannot be read or processed
        
    Example:
        >>> score = smoothness_test("signature.jpg")
        >>> print(f"Smoothness: {score:.4f}")
        Smoothness: 0.7823
        
    Note:
        The function preprocesses the image with Gaussian blur and uses
        Canny edge detection to find contours for analysis.
    """
    try:
        # Input validation
        if not os.path.exists(image_path):
            raise FileNotFoundError("Image file not found")
            
        # Load and preprocess image
        signature = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if signature is None:
            raise ValueError("Could not read image")
            
        # Apply Gaussian blur to reduce noise
        signature = cv2.GaussianBlur(signature, (3,3), 0)
        
        # Edge detection with optimized parameters
        edges = cv2.Canny(signature, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        curvature_variances = []

        for contour in contours:
            contour = contour.squeeze()
            if len(contour.shape) < 2 or len(contour) < 3:
                continue
                
            # Calculate gradients
            dx = np.gradient(contour[:, 0].astype(float))
            dy = np.gradient(contour[:, 1].astype(float))
            ddx = np.gradient(dx)
            ddy = np.gradient(dy)
            
            # Avoid division by zero with small epsilon
            denominator = (dx**2 + dy**2)**1.5
            epsilon = 1e-10
            denominator = np.where(denominator < epsilon, epsilon, denominator)
            
            # Calculate curvature safely
            curvature = np.abs(ddx * dy - dx * ddy) / denominator
            
            # Filter out invalid values
            valid_curvature = curvature[~np.isnan(curvature)]
            if len(valid_curvature) > 0:
                curvature_variances.append(np.var(valid_curvature))

        # Compute normalized smoothness score
        if curvature_variances:
            smoothness_score = 1.0 / (1.0 + np.mean(curvature_variances))
        else:
            smoothness_score = 0.0
            
        return smoothness_score

    except Exception as e:
        print(f"Error processing signature: {str(e)}")
        return 0.0

if __name__ == "__main__":
    input_path = f"{dir}/testing_images/signature.jpg"
    score = smoothness_test(input_path)
    print(f"Line Smoothness Score: {score:.4f}")