"""
Service layer for Evaluation API business logic.

This module contains the evaluation logic for image processing and signature analysis.
It acts as an interface between the API views and the underlying evaluation modules.

The service layer provides:
- SSIM calculation for image comparison
- Line smoothness analysis
- G-code execution error calculation
- File handling and temporary file management
- Error handling and logging

Classes:
    EvaluationService: Handles all evaluation metrics
"""

import os
import tempfile
import logging
from typing import Tuple, Optional, List, Union, Dict, Any
import base64
import io
import numpy as np
from PIL import Image, ImageFile
import xml.etree.ElementTree as ET

# Import our existing modules
from evaluation_modules.ssim import compute_ssim
from evaluation_modules.line_smoothness import smoothness_test
from evaluation_modules.gcode_error import execution_error

# Enable loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

logger = logging.getLogger(__name__)


class EvaluationService:
    """
    Service class for handling evaluation metrics.
    
    This service provides methods for calculating various evaluation
    metrics for signature analysis and G-code execution quality.
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = {'PNG', 'JPEG', 'JPG', 'BMP', 'TIFF', 'GIF', 'SVG'}
    
    @staticmethod
    def _normalize_image_format(image: Image.Image) -> Image.Image:
        """
        Normalize image format for consistent processing.
        
        Args:
            image (Image.Image): PIL Image object
            
        Returns:
            Image.Image: Normalized image in RGB mode
        """
        # Convert to RGB if not already (handles RGBA, P, L modes)
        if image.mode not in ['RGB', 'L']:
            if image.mode == 'RGBA':
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                image = background
            else:
                image = image.convert('RGB')
        
        return image
    
    @staticmethod
    def _convert_svg_to_png(svg_data: bytes, output_path: str, width: int = 800, height: int = 600) -> None:
        """
        Convert SVG data to PNG using cairosvg or fallback methods.
        
        Args:
            svg_data (bytes): SVG file data
            output_path (str): Path to save PNG file
            width (int): Output width in pixels
            height (int): Output height in pixels
            
        Raises:
            ValueError: If SVG conversion fails
        """
        try:
            # Try using svglib + reportlab
            try:
                from svglib.svglib import renderSVG
                from reportlab.graphics import renderPM
                import tempfile
                    
                # Create temporary SVG file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as temp_svg:
                    temp_svg.write(svg_data.decode('utf-8'))
                    temp_svg_path = temp_svg.name
                    
                try:
                    # Convert SVG to PIL Image
                    drawing = renderSVG.renderSVG(temp_svg_path)
                    pil_image = renderPM.drawToPIL(drawing, fmt='PNG')
                        
                    # Resize if needed
                    if pil_image.size != (width, height):
                        pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
                        
                    # Save as PNG
                    pil_image.save(output_path, 'PNG')
                    logger.debug("SVG converted using svglib")
                    return
                        
                finally:
                    # Clean up temporary SVG file
                    if os.path.exists(temp_svg_path):
                        os.unlink(temp_svg_path)
                            
            except ImportError:
                logger.debug("svglib not available, trying wand")

            # Fallback: Create a basic image with SVG dimensions
            try:
                # Parse SVG to get dimensions
                svg_text = svg_data.decode('utf-8')
                root = ET.fromstring(svg_text)
                    
                # Extract width and height if available
                svg_width = root.get('width', str(width))
                svg_height = root.get('height', str(height))
                    
                # Convert to pixels if they have units
                try:
                    if 'px' in svg_width:
                        svg_width = int(float(svg_width.replace('px', '')))
                    else:
                        svg_width = int(float(svg_width))
                except:
                    svg_width = width
                    
                try:
                    if 'px' in svg_height:
                        svg_height = int(float(svg_height.replace('px', '')))
                    else:
                        svg_height = int(float(svg_height))
                except:
                    svg_height = height
                    
                # Create a white image as fallback
                fallback_image = Image.new('RGB', (svg_width, svg_height), 'white')
                fallback_image.save(output_path, 'PNG')
                    
                logger.warning("SVG converted using fallback method (white image). Install cairosvg, svglib, or Wand for proper SVG rendering.")
                return
                    
            except Exception as e:
                raise ValueError(f"Failed to parse SVG: {str(e)}")
                    
        except Exception as e:
            raise ValueError(f"SVG conversion failed: {str(e)}")
    
    @staticmethod
    def _prepare_image_from_file(image_file) -> str:
        """
        Save uploaded file to temporary location with format validation.
        
        Args:
            image_file: Django uploaded file object
            
        Returns:
            str: Path to temporary file
            
        Raises:
            ValueError: If image format is not supported
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        try:
            # Read the image data
            image_data = b''
            for chunk in image_file.chunks():
                image_data += chunk
            
            # Check if it's an SVG file
            if image_data.startswith(b'<svg') or b'<svg' in image_data[:100]:
                logger.debug("Detected SVG file upload")
                EvaluationService._convert_svg_to_png(image_data, temp_file.name)
                return temp_file.name
            
            # Validate and process the image
            try:
                image = Image.open(io.BytesIO(image_data))
                
                # Verify the image can be loaded
                image.verify()
                
                # Reopen for processing (verify() closes the file)
                image = Image.open(io.BytesIO(image_data))
                
                # Check if format is supported
                if image.format not in EvaluationService.SUPPORTED_FORMATS:
                    raise ValueError(f"Unsupported image format: {image.format}")
                
                # Normalize the image format
                normalized_image = EvaluationService._normalize_image_format(image)
                
                # Save as PNG for consistent processing
                normalized_image.save(temp_file.name, 'PNG', optimize=True)
                
            except Exception as e:
                raise ValueError(f"Invalid or corrupted image file: {str(e)}")
            
            return temp_file.name
            
        finally:
            temp_file.close()
    
    @staticmethod
    def _prepare_image_from_base64(base64_data: str) -> str:
        """
        Convert base64 image data to temporary file with format validation.
        
        Args:
            base64_data (str): Base64 encoded image data
            
        Returns:
            str: Path to temporary file
            
        Raises:
            ValueError: If base64 data is invalid or image format is not supported
        """
        try:
            # Clean the base64 data
            if not base64_data:
                raise ValueError("Empty base64 data provided")
            
            # Remove data URL prefix if present (e.g., "data:image/png;base64,")
            if ',' in base64_data:
                header, base64_data = base64_data.split(',', 1)
                logger.debug(f"Removed data URL header: {header}")
            
            # Remove any whitespace and newlines
            base64_data = ''.join(base64_data.split())
            
            # Validate base64 format
            if not base64_data:
                raise ValueError("Empty base64 data after cleaning")
            
            # Decode base64 data
            try:
                image_data = base64.b64decode(base64_data, validate=True)
            except Exception as e:
                raise ValueError(f"Invalid base64 encoding: {str(e)}")
            
            if len(image_data) == 0:
                raise ValueError("Decoded image data is empty")
            
            # Check if it's an SVG
            if image_data.startswith(b'<svg') or b'<svg' in image_data[:100]:
                logger.debug("Detected SVG from base64 data")
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                temp_file.close()
                EvaluationService._convert_svg_to_png(image_data, temp_file.name)
                return temp_file.name
            
            # Detect image format from magic bytes
            detected_format = EvaluationService._detect_image_format(image_data)
            logger.debug(f"Detected format from magic bytes: {detected_format}")
            
            if not detected_format:
                # Log first 32 bytes for debugging
                header_hex = image_data[:32].hex() if len(image_data) >= 32 else image_data.hex()
                logger.error(f"Cannot detect image format. Header bytes: {header_hex}")
                raise ValueError(f"Cannot detect image format from data. Header: {header_hex}")
            
            # Check if format is supported
            if detected_format not in EvaluationService.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported image format: {detected_format}")
            
            # Create BytesIO object for PIL
            image_buffer = io.BytesIO(image_data)
            image_buffer.seek(0)
            
            try:
                # Open image with PIL
                image = Image.open(image_buffer)
                
                # Verify the image integrity
                image.verify()
                
                # Reopen for processing (verify() closes the file)
                image_buffer.seek(0)
                image = Image.open(image_buffer)
                
                # Log image details for debugging
                logger.debug(f"Image format: {image.format}, Mode: {image.mode}, Size: {image.size}")
                
                # Normalize the image format
                normalized_image = EvaluationService._normalize_image_format(image)
                
                # Save to temporary file as PNG
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                normalized_image.save(temp_file.name, 'PNG', optimize=True)
                temp_file.close()
                
                logger.debug(f"Successfully processed image and saved to: {temp_file.name}")
                return temp_file.name
                
            except Exception as e:
                raise ValueError(f"Cannot process {detected_format} image data: {str(e)}")
            
        except ValueError:
            # Re-raise ValueError as-is
            raise
        except Exception as e:
            # Catch any other unexpected errors
            logger.error(f"Unexpected error processing base64 image: {str(e)}")
            raise ValueError(f"Unexpected error processing base64 image: {str(e)}")
    
    @staticmethod
    def _detect_image_format(image_data: bytes) -> Optional[str]:
        """
        Detect image format from binary data using magic bytes.
        
        Args:
            image_data (bytes): Binary image data
            
        Returns:
            Optional[str]: Detected format or None if unrecognized
        """
        if len(image_data) < 16:
            return None
        
        # Check for SVG (XML-based)
        if image_data.startswith(b'<svg') or b'<svg' in image_data[:100]:
            return 'SVG'
        
        # Check magic bytes for different formats
        if image_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'PNG'
        elif image_data.startswith(b'\xff\xd8\xff'):
            return 'JPEG'
        elif image_data.startswith(b'BM'):
            return 'BMP'
        elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):
            return 'GIF'
        elif image_data.startswith(b'II*\x00') or image_data.startswith(b'MM\x00*'):
            return 'TIFF'
        elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
            return 'WEBP'
        
        return None
    
    @staticmethod
    def calculate_ssim(
        original_image=None, 
        reproduced_image=None,
        original_image_data=None,
        reproduced_image_data=None
    ) -> float:
        """
        Calculate SSIM between two images.
        
        Args:
            original_image: Original image file (Django UploadedFile)
            reproduced_image: Reproduced image file (Django UploadedFile)
            original_image_data (str): Base64 encoded original image
            reproduced_image_data (str): Base64 encoded reproduced image
            
        Returns:
            float: SSIM score between 0 and 1
            
        Raises:
            ValueError: If image processing fails
        """
        temp_files = []
        try:
            # Validate input parameters
            if not ((original_image and reproduced_image) or 
                   (original_image_data and reproduced_image_data)):
                raise ValueError("Must provide either image files or base64 data for both images")
            
            # Prepare image paths
            if original_image and reproduced_image:
                logger.debug("Processing uploaded image files")
                original_path = EvaluationService._prepare_image_from_file(original_image)
                reproduced_path = EvaluationService._prepare_image_from_file(reproduced_image)
            else:
                logger.debug("Processing base64 image data")
                original_path = EvaluationService._prepare_image_from_base64(original_image_data) # type: ignore
                reproduced_path = EvaluationService._prepare_image_from_base64(reproduced_image_data) # type: ignore
            
            temp_files.extend([original_path, reproduced_path])
            
            # Calculate SSIM using existing module
            ssim_score = compute_ssim(original_path=original_path, reproduced_path=reproduced_path)
            
            if ssim_score is None:
                raise ValueError("SSIM calculation returned None")
            
            logger.info(f"SSIM calculated successfully: {ssim_score:.4f}")
            return float(ssim_score)
            
        except ValueError:
            # Re-raise ValueError as-is for proper error handling
            raise
        except Exception as e:
            logger.error(f"Unexpected error calculating SSIM: {str(e)}")
            raise ValueError(f"SSIM calculation failed: {str(e)}")
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if temp_file and os.path.exists(temp_file):
                        os.unlink(temp_file)
                        logger.debug(f"Cleaned up temporary file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {temp_file}: {str(e)}")
    
    @staticmethod
    def calculate_smoothness(image=None, image_data=None) -> float:
        """
        Calculate line smoothness score for an image.
        
        Args:
            image: Image file (Django UploadedFile)
            image_data (str): Base64 encoded image data
            
        Returns:
            float: Smoothness score between 0 and 1
            
        Raises:
            ValueError: If image processing fails
        """
        temp_file = None
        try:
            # Validate input parameters
            if not (image or image_data):
                raise ValueError("Must provide either image file or base64 data")
            
            # Prepare image path
            if image:
                logger.debug("Processing uploaded image file for smoothness")
                temp_file = EvaluationService._prepare_image_from_file(image)
            else:
                logger.debug("Processing base64 image data for smoothness")
                temp_file = EvaluationService._prepare_image_from_base64(image_data) # type: ignore
            
            # Calculate smoothness using existing module
            smoothness_score = smoothness_test(temp_file)
            
            logger.info(f"Smoothness calculated successfully: {smoothness_score:.4f}")
            return float(smoothness_score)
            
        except ValueError:
            # Re-raise ValueError as-is for proper error handling
            raise
        except Exception as e:
            logger.error(f"Unexpected error calculating smoothness: {str(e)}")
            raise ValueError(f"Smoothness calculation failed: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        logger.debug(f"Cleaned up temporary file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {temp_file}: {str(e)}")
    
    @staticmethod
    def calculate_execution_error(
        expected_toolpath: List[List[float]], 
        actual_toolpath: List[List[float]]
    ) -> Tuple[float, List[float]]:
        """
        Calculate G-code execution error between expected and actual toolpaths.
        
        Args:
            expected_toolpath: List of [x, y] coordinate pairs for expected path
            actual_toolpath: List of [x, y] coordinate pairs for actual path
            
        Returns:
            tuple: (mean_error, individual_errors)
                - mean_error (float): Average execution error
                - individual_errors (List[float]): Error at each point
                
        Raises:
            ValueError: If calculation fails
        """
        try:
            # Validate input data
            if not expected_toolpath or not actual_toolpath:
                raise ValueError("Both expected and actual toolpaths must be provided")
            
            # Convert to numpy arrays
            expected = np.array(expected_toolpath)
            actual = np.array(actual_toolpath)
            
            # Validate array shapes
            if expected.ndim != 2 or actual.ndim != 2:
                raise ValueError("Toolpaths must be 2D arrays")
            
            if expected.shape[1] != 2 or actual.shape[1] != 2:
                raise ValueError("Toolpath coordinates must be [x, y] pairs")
            
            # Calculate execution error using existing module
            mean_error, errors = execution_error(expected, actual)
            
            if mean_error is None:
                raise ValueError("Execution error calculation returned None")
            
            logger.info(f"Execution error calculated successfully: {mean_error:.4f}")
            return float(mean_error), errors.tolist() # type: ignore
            
        except ValueError:
            # Re-raise ValueError as-is for proper error handling
            raise
        except Exception as e:
            logger.error(f"Unexpected error calculating execution error: {str(e)}")
            raise ValueError(f"Execution error calculation failed: {str(e)}")