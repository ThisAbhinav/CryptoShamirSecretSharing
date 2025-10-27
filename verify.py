from PIL import Image
import numpy as np
import sys


def compare_images(img1_path, img2_path):
    # Load images
    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")

    # Convert to numpy
    arr1 = np.array(img1)
    arr2 = np.array(img2)

    # First check shape
    if arr1.shape != arr2.shape:
        print("Images have different shapes!")
        print("Image1:", arr1.shape)
        print("Image2:", arr2.shape)
        return

    # Compare pixels
    diff = arr1 != arr2
    num_diff_pixels = np.count_nonzero(diff)

    if num_diff_pixels == 0:
        print("✅ Images are identical (pixel-wise match).")
    else:
        print(f"❌ Images differ at {num_diff_pixels} pixels.")

        # Optional: summarize difference magnitude
        abs_diff = np.abs(arr1.astype(int) - arr2.astype(int))
        print("Max per-channel difference:", abs_diff.max())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_images.py <image1> <image2>")
    else:
        compare_images(sys.argv[1], sys.argv[2])
