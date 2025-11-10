"""
Share file I/O operations for saving and loading share files.
"""

import numpy as np


def save_share(share_array, x, prime, mode, original_shape, filepath):
    """
    Save a share to a .npz file with metadata.
    
    Args:
        share_array: The share data (H x W or H x W x 3)
        x: The x-coordinate for this share
        prime: The prime used for finite field operations
        mode: 'grayscale' or 'rgb'
        original_shape: Original image shape
        filepath: Path to save the share file
    """
    np.savez_compressed(
        filepath,
        share=share_array,
        x=np.array([x], dtype=np.int32),
        prime=np.array([prime], dtype=np.int32),
        mode=np.array([mode], dtype='U10'),
        original_shape=np.array(original_shape, dtype=np.int32)
    )


def load_share(filepath):
    """
    Load a share from a .npz file with metadata.
    
    Args:
        filepath: Path to the share file
        
    Returns:
        Dictionary containing:
            - 'share': The share array
            - 'x': The x-coordinate
            - 'prime': The prime used
            - 'mode': Image mode ('grayscale' or 'rgb')
            - 'original_shape': Original image shape
    """
    data = np.load(filepath, allow_pickle=False)
    
    # Handle both new format (with metadata) and old format (share only)
    if 'x' in data:
        # New format with metadata
        return {
            'share': data['share'],
            'x': int(data['x'][0]),
            'prime': int(data['prime'][0]),
            'mode': str(data['mode'][0]),
            'original_shape': tuple(data['original_shape'])
        }
    else:
        # Old format - only has 'share' array
        # Try to infer x from filename and use default values
        import os
        basename = os.path.basename(filepath)
        
        # Try to extract x from filename (e.g., share_3.npz -> x=3)
        x = None
        if basename.startswith("share_") and basename.endswith(".npz"):
            try:
                x = int(basename.split("_")[1].split(".")[0])
            except:
                pass
        
        if x is None:
            raise ValueError(
                f"Could not determine x-coordinate from old format file: {filepath}. "
                "Please use new format shares or rename file to 'share_<x>.npz'"
            )
        
        share_array = data['share']
        mode = 'grayscale' if share_array.ndim == 2 else 'rgb'
        
        return {
            'share': share_array,
            'x': x,
            'prime': 257,  # Default prime for old format
            'mode': mode,
            'original_shape': share_array.shape
        }


def validate_shares_compatible(share_data_list):
    """
    Validate that all shares are compatible for reconstruction.
    
    Args:
        share_data_list: List of share data dictionaries from load_share()
        
    Returns:
        True if compatible, raises ValueError otherwise
    """
    if not share_data_list:
        raise ValueError("No shares provided")
    
    first = share_data_list[0]
    reference_prime = first['prime']
    reference_mode = first['mode']
    reference_shape = first['original_shape']
    
    for i, share_data in enumerate(share_data_list[1:], 1):
        if share_data['prime'] != reference_prime:
            raise ValueError(
                f"Share {i} has different prime ({share_data['prime']}) "
                f"than share 0 ({reference_prime})"
            )
        if share_data['mode'] != reference_mode:
            raise ValueError(
                f"Share {i} has different mode ({share_data['mode']}) "
                f"than share 0 ({reference_mode})"
            )
        if share_data['original_shape'] != reference_shape:
            raise ValueError(
                f"Share {i} has different shape ({share_data['original_shape']}) "
                f"than share 0 ({reference_shape})"
            )
    
    return True
