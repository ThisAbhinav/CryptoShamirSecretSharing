"""
Compare two images for verification after reconstruction.
"""

from PIL import Image
import numpy as np
import sys


def compare_images(img1_path, img2_path):
    """
    Compare two images pixel by pixel.
    
    Args:
        img1_path: Path to first image
        img2_path: Path to second image
    """
    # Load images
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path)
    
    # Get original modes
    mode1 = img1.mode
    mode2 = img2.mode
    
    print(f"\n{'='*60}")
    print("Image Comparison")
    print(f"{'='*60}")
    print(f"\nImage 1: {img1_path}")
    print(f"  Mode: {mode1}, Size: {img1.size}")
    print(f"\nImage 2: {img2_path}")
    print(f"  Mode: {mode2}, Size: {img2.size}")
    
    # Convert to same mode for comparison
    if mode1 != mode2:
        print(f"\n[WARNING] Images have different modes ({mode1} vs {mode2})")
        print("          Converting both to RGB for comparison...")
        img1 = img1.convert("RGB")
        img2 = img2.convert("RGB")
    elif mode1 in ('RGB', 'RGBA'):
        img1 = img1.convert("RGB")
        img2 = img2.convert("RGB")
    elif mode1 == 'L':
        # Keep as grayscale
        pass
    else:
        # Convert other modes to RGB
        img1 = img1.convert("RGB")
        img2 = img2.convert("RGB")

    # Convert to numpy arrays
    arr1 = np.array(img1)
    arr2 = np.array(img2)

    # Check shape compatibility
    if arr1.shape != arr2.shape:
        print(f"\n[ERROR] Images have different shapes!")
        print(f"        Image 1: {arr1.shape}")
        print(f"        Image 2: {arr2.shape}")
        return False

    # Compare pixels
    diff = arr1 != arr2
    num_diff_pixels = np.count_nonzero(np.any(diff, axis=-1) if arr1.ndim == 3 else diff)
    total_pixels = arr1.shape[0] * arr1.shape[1]

    print(f"\n{'='*60}")
    print("Comparison Results")
    print(f"{'='*60}")
    
    if num_diff_pixels == 0:
        print("[SUCCESS] Images are IDENTICAL (perfect pixel-wise match)")
        print(f"          Total pixels: {total_pixels}")
        return True
    else:
        diff_percentage = (num_diff_pixels / total_pixels) * 100
        print(f"[ERROR] Images DIFFER at {num_diff_pixels} pixels ({diff_percentage:.2f}%)")
        print(f"        Total pixels: {total_pixels}")
        print(f"        Matching pixels: {total_pixels - num_diff_pixels}")

        # Analyze difference magnitude
        abs_diff = np.abs(arr1.astype(int) - arr2.astype(int))
        max_diff = abs_diff.max()
        mean_diff = abs_diff.mean()
        
        print(f"\nDifference Statistics:")
        print(f"        Max difference (per channel): {max_diff}")
        print(f"        Mean difference: {mean_diff:.2f}")
        
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python verify.py <image1> <image2>")
        print("\nExample:")
        print("  python verify.py original.png reconstructed.png")
    else:
        compare_images(sys.argv[1], sys.argv[2])
