"""
G-Code Execution Error Evaluation Module

This module provides functionality to calculate the execution error between
expected and actual toolpaths for G-code execution analysis.

The execution error is calculated as the Euclidean distance between
corresponding points in the expected and actual toolpaths, providing
a measure of how accurately a CNC machine or robot followed the G-code instructions.

Functions:
    execution_error: Calculate mean execution error and individual point errors

Usage:
    import numpy as np
    from evaluation_modules.gcode_error import execution_error
    
    # Example toolpaths
    expected = np.array([[10, 20], [15, 25], [20, 30]])
    actual = np.array([[10, 21], [14, 26], [19, 31]])
    
    mean_error, errors = execution_error(expected, actual)
    print(f"Mean execution error: {mean_error:.2f}")
"""

import numpy as np


def execution_error(expected_toolpath, actual_toolpath):
    """
    Calculate execution error between expected and actual toolpaths.
    
    This function computes the Euclidean distance between corresponding points
    in two toolpaths to measure how accurately a machine followed the intended path.
    
    Args:
        expected_toolpath (array-like): Expected toolpath coordinates as array of [x, y] pairs
        actual_toolpath (array-like): Actual executed toolpath coordinates as array of [x, y] pairs
        
    Returns:
        tuple: (mean_error, individual_errors)
            - mean_error (float): Average Euclidean distance across all points
            - individual_errors (numpy.ndarray): Euclidean distance at each point
            
    Raises:
        ValueError: If toolpaths are None, have different shapes, or are invalid
        
    Example:
        >>> expected = np.array([[10, 20], [15, 25], [20, 30]])
        >>> actual = np.array([[10, 21], [14, 26], [19, 31]])
        >>> mean_err, errors = execution_error(expected, actual)
        >>> print(f"Mean error: {mean_err:.2f}")
        Mean error: 1.25
    """
    try:
        if expected_toolpath is None or actual_toolpath is None:
            raise ValueError("Both toolpaths must be provided")

        # Convert inputs to numpy arrays if they aren't already
        expected = np.array(expected_toolpath)
        actual = np.array(actual_toolpath)

        # Verify dimensions match
        if expected.shape != actual.shape:
            raise ValueError("Toolpath dimensions must match")

        # Compute Euclidean distance error
        errors = np.linalg.norm(expected - actual, axis=1)
        mean_error = np.mean(errors)

        return mean_error, errors

    except Exception as e:
        print(f"Error calculating execution error: {str(e)}")
        return None, None

# Experimental usage
if __name__ == "__main__":
    # Example expected G-code toolpath
    expected = np.array([
        [10, 20], [15, 25], [20, 30], [25, 35], [30, 40]
    ])

    # Example actual robot movement log
    actual = np.array([
        [10, 21], [14, 26], [19, 31], [26, 34], [31, 41]
    ])

    mean_error, errors = execution_error(expected, actual)
    
    if mean_error is not None:
        print(f"Mean Execution Error: {mean_error:.2f} units")
        print(f"Error at each point: {errors}")