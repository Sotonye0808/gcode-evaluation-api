"""
SSIM (Structural Similarity Index) Evaluation Module

This module provides functionality to calculate the Structural Similarity Index (SSIM)
between two images, which measures perceptual similarity.

SSIM is a perception-based model that considers image degradation as perceived
change in structural information. It compares luminance, contrast, and structure
between two images.

Functions:
    compute_ssim: Calculate SSIM score between two images

Usage:
    from evaluation_modules.ssim import compute_ssim
    
    # Using file paths
    score = compute_ssim(original_path="original.jpg", reproduced_path="reproduced.jpg")
    print(f"SSIM score: {score:.4f}")
    
    # Using image arrays
    import cv2
    original = cv2.imread("original.jpg")
    reproduced = cv2.imread("reproduced.jpg")
    score = compute_ssim(original_image=original, reproduced_image=reproduced)
    
    # Interpret the score
    if score >= 0.9:
        print("Excellent similarity")
    elif score >= 0.7:
        print("Good similarity")
    elif score >= 0.5:
        print("Moderate similarity")
    else:
        print("Poor similarity")
        
SSIM Score Interpretation:
    - SSIM = 1.0: Perfect match (identical images)
    - SSIM > 0.9: Excellent similarity
    - SSIM > 0.7: Good similarity
    - SSIM > 0.5: Moderate similarity
    - SSIM < 0.5: Poor similarity
"""

import cv2
import os
from skimage.metrics import structural_similarity as ssim
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
common_dir = os.getenv("COMMON_DIR")

def compute_ssim(original_path=None, reproduced_path=None, original_image=None, reproduced_image=None):
    """
    Calculate SSIM (Structural Similarity Index) between two images.
    
    This function computes the SSIM score between two images, which measures
    the perceptual similarity considering luminance, contrast, and structure.
    
    Args:
        original_path (str, optional): Path to the original image file
        reproduced_path (str, optional): Path to the reproduced image file
        original_image (numpy.ndarray, optional): Original image as numpy array
        reproduced_image (numpy.ndarray, optional): Reproduced image as numpy array
        
    Returns:
        float: SSIM score between -1 and 1 (typically 0 to 1)
            - 1.0: Perfect similarity (identical images)
            - 0.0: No similarity
            - Values close to 1: High similarity
            - Values close to 0: Low similarity
            
    Raises:
        ValueError: If neither file paths nor image arrays are provided
        Exception: If image processing fails
        
    Example:
        >>> # Using file paths
        >>> score = compute_ssim("image1.jpg", "image2.jpg")
        >>> print(f"SSIM: {score:.4f}")
        SSIM: 0.8542
        
        >>> # Using image arrays
        >>> import cv2
        >>> img1 = cv2.imread("image1.jpg")
        >>> img2 = cv2.imread("image2.jpg")
        >>> score = compute_ssim(original_image=img1, reproduced_image=img2)
        
    Note:
        Images are automatically resized to match dimensions if they differ.
        The function converts color images to grayscale for comparison.
    """
    try:
        # Load images 
        # if paths are provided
        if original_path and reproduced_path:
            original = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
            reproduced = cv2.imread(reproduced_path, cv2.IMREAD_GRAYSCALE)
        # if actual images are provided, format to png/Matlike
        elif original_image is not None and reproduced_image is not None:
            original = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
            reproduced = cv2.cvtColor(reproduced_image, cv2.COLOR_BGR2GRAY)
        else:
            raise ValueError("Either image paths or image arrays must be provided")

        # Resize to match dimensions
        reproduced = cv2.resize(reproduced, (original.shape[1], original.shape[0]))

        # Compute SSIM
        score, _ = ssim(original, reproduced, full=True) # type: ignore
        return score

    except Exception as e:
        print(f"Error processing signature: {str(e)}")

"""
SSIM = 1 → Perfect match
SSIM close to 1 → High similarity
SSIM close to 0 → Low similarity
"""

# Experimental usage
if __name__ == "__main__":
    shared_dir = f"{dir}/testing_images"
    orig_path = f"{shared_dir}/signature.jpg"
    rep_path = f"{shared_dir}/signature.png"
    # using paths
    result = compute_ssim(orig_path, rep_path)
    print(f"SSIM Score: {result:.4f}")
    # if to use images
    """ original_image = cv2.imread(input_path)
    reproduced_image = cv2.imread(output_path)
    compute_ssim(original_image=original_image, reproduced_image=reproduced_image) """