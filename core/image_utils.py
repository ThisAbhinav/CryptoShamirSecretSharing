"""
Image loading, saving, and property detection utilities.
"""

import numpy as np
from PIL import Image
from .field_math import next_prime


def detect_image_properties(img_array):
    """
    Detect properties of an image array.
    
    Args:
        img_array: Numpy array representing the image
        
    Returns:
        Dictionary containing:
            - 'mode': 'grayscale' or 'rgb'
            - 'max_value': Maximum pixel intensity value
            - 'min_value': Minimum pixel intensity value
            - 'recommended_prime': Recommended prime for finite field
            - 'shape': Original shape of the image
            - 'bit_depth': Detected bit depth (4, 8, 16, etc.)
    """
    mode = 'grayscale' if img_array.ndim == 2 else 'rgb'
    max_val = int(np.max(img_array))
    min_val = int(np.min(img_array))
    
    # Detect bit depth based on max value
    if max_val <= 15:
        bit_depth = 4  # 4-bit (0-15)
    elif max_val <= 255:
        bit_depth = 8  # 8-bit (0-255)
    elif max_val <= 65535:
        bit_depth = 16  # 16-bit (0-65535)
    else:
        bit_depth = 32  # Higher precision
    
    # Calculate recommended prime (next prime after max_value)
    recommended_prime = next_prime(max_val)
    
    return {
        'mode': mode,
        'max_value': max_val,
        'min_value': min_val,
        'recommended_prime': recommended_prime,
        'shape': img_array.shape,
        'bit_depth': bit_depth,
    }


# Alias for consistency
detect_image_mode = detect_image_properties


def load_image(filepath, grayscale=None):
    """
    Load an image from file and convert to numpy array.
    
    Args:
        filepath: Path to the image file
        grayscale: If True, force grayscale. If False, force RGB.
                   If None, keep original format.
        
    Returns:
        Numpy array of the image (H x W for grayscale, H x W x 3 for RGB)
    """
    img = Image.open(filepath)
    
    if grayscale is True:
        img = img.convert('L')
    elif grayscale is False:
        img = img.convert('RGB')
    elif img.mode == 'L':
        # Already grayscale
        pass
    elif img.mode in ('RGB', 'RGBA'):
        img = img.convert('RGB')
    else:
        # Convert any other mode to RGB
        img = img.convert('RGB')
    
    # Convert to numpy array with appropriate dtype
    arr = np.array(img)
    
    return arr


def save_image(img_array, filepath, mode='auto'):
    """
    Save a numpy array as an image file.
    
    Args:
        img_array: Numpy array to save (H x W for grayscale, H x W x 3 for RGB)
        filepath: Path where to save the image
        mode: 'grayscale', 'rgb', or 'auto' (auto-detect from shape)
    """
    # Ensure uint8 dtype
    if img_array.dtype != np.uint8:
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    
    # Detect mode if auto
    if mode == 'auto':
        mode = 'grayscale' if img_array.ndim == 2 else 'rgb'
    
    if mode == 'grayscale':
        if img_array.ndim == 3:
            # Convert RGB to grayscale if needed
            img_array = np.mean(img_array, axis=2).astype(np.uint8)
        img = Image.fromarray(img_array, mode='L')
    else:  # RGB
        if img_array.ndim == 2:
            # Convert grayscale to RGB
            img_array = np.stack([img_array] * 3, axis=-1)
        img = Image.fromarray(img_array, mode='RGB')
    
    img.save(filepath)


def normalize_to_uint8(img_array, original_max_value):
    """
    Normalize an image array to uint8 range (0-255).
    
    Args:
        img_array: Image array with arbitrary range
        original_max_value: Original maximum value in the data
        
    Returns:
        Normalized uint8 array
    """
    if original_max_value <= 255:
        # Already in uint8 range
        return np.clip(img_array, 0, 255).astype(np.uint8)
    else:
        # Scale to 0-255
        scaled = (img_array.astype(np.float64) * 255.0 / original_max_value)
        return np.clip(scaled, 0, 255).astype(np.uint8)
