"""
Core Shamir's Secret Sharing implementation for images.
"""

import numpy as np
from .field_math import lagrange_coeffs_at_zero


def split_image_into_shares(img_array, n, k, prime, rng=None):
    """
    Split an image into n shares with threshold k using Shamir's Secret Sharing.
    
    Args:
        img_array: Image array (H x W for grayscale, H x W x 3 for RGB)
        n: Total number of shares to create
        k: Threshold number of shares needed for reconstruction
        prime: Prime number for finite field operations
        rng: Random number generator (optional)
        
    Returns:
        Dictionary mapping x (1..n) -> share_array
    """
    if rng is None:
        rng = np.random.default_rng()
    
    if not (2 <= k <= n):
        raise ValueError(f"Require 2 <= k <= n, got k={k}, n={n}")
    
    # Ensure image values are within field
    max_val = np.max(img_array)
    if max_val >= prime:
        raise ValueError(
            f"Image max value ({max_val}) must be less than prime ({prime})"
        )
    
    # Convert to int64 for calculations
    secrets = img_array.astype(np.int64)
    
    # Determine if grayscale or RGB
    if img_array.ndim == 2:
        # Grayscale: H x W
        H, W = img_array.shape
        is_grayscale = True
    elif img_array.ndim == 3:
        # RGB: H x W x C
        H, W, C = img_array.shape
        if C != 3:
            raise ValueError(f"Expected 3 channels for RGB, got {C}")
        is_grayscale = False
    else:
        raise ValueError(f"Unexpected image dimensions: {img_array.ndim}")
    
    # Generate random polynomial coefficients
    # Polynomial of degree k-1 has k coefficients
    # coeffs[0] = secret, coeffs[1..k-1] = random
    if is_grayscale:
        coeffs = np.empty((k, H, W), dtype=np.int64)
        coeffs[0] = secrets
        for j in range(1, k):
            coeffs[j] = rng.integers(0, prime, size=(H, W), dtype=np.int64)
    else:
        coeffs = np.empty((k, H, W, C), dtype=np.int64)
        coeffs[0] = secrets
        for j in range(1, k):
            coeffs[j] = rng.integers(0, prime, size=(H, W, C), dtype=np.int64)
    
    # Evaluate polynomial at x = 1, 2, ..., n
    shares = {}
    for x in range(1, n + 1):
        # y = sum_{j=0}^{k-1} coeffs[j] * x^j  (mod prime)
        x_pow = 1
        y = np.zeros_like(secrets, dtype=np.int64)
        for j in range(k):
            y = (y + coeffs[j] * x_pow) % prime
            x_pow = (x_pow * x) % prime
        
        # Store as uint32 to handle values up to large primes
        shares[x] = y.astype(np.uint32)
    
    return shares


def reconstruct_from_shares(share_arrays, xs, prime):
    """
    Reconstruct an image from k or more shares using Lagrange interpolation.
    
    Args:
        share_arrays: List of share arrays (each H x W or H x W x 3)
        xs: List of x-coordinates corresponding to each share
        prime: Prime number for finite field operations
        
    Returns:
        Reconstructed image array (same shape as shares)
    """
    k = len(xs)
    if k != len(share_arrays):
        raise ValueError(
            f"Number of xs ({k}) must equal number of shares ({len(share_arrays)})"
        )
    
    if k < 2:
        raise ValueError(f"Need at least 2 shares to reconstruct, got {k}")
    
    # Compute Lagrange coefficients at x=0
    lagrange_coeffs = lagrange_coeffs_at_zero(xs, prime)
    
    # Reconstruct: secret = sum_i (y_i * L_i) mod prime
    accum = None
    for li, y_arr in zip(lagrange_coeffs, share_arrays):
        # Convert to int64 to handle large intermediate values
        y_int = y_arr.astype(np.int64) % prime
        term = (y_int * int(li)) % prime
        
        if accum is None:
            accum = term
        else:
            accum = (accum + term) % prime
    
    # Convert back to appropriate dtype
    secret = accum.astype(np.int64) % prime
    
    # Determine output dtype based on max value
    max_val = np.max(secret)
    if max_val <= 255:
        return secret.astype(np.uint8)
    elif max_val <= 65535:
        return secret.astype(np.uint16)
    else:
        return secret.astype(np.uint32)


# Aliases for consistency with main.py expectations
split_secret = split_image_into_shares
reconstruct_secret = reconstruct_from_shares
