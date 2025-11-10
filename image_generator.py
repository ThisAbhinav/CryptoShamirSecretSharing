"""
Generates images with different patterns at different bit-depths for testing.

# pattern: star, gradient, stripes
# bit depths: 4, 8

Output should be PNG only, but if its 4 bit depth, save as 8 bit PNG with only 0-15 intensity values.

Include a view function to visualize the generated images, especially ones at 4-bit depth.
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import argparse


def generate_star_pattern(width=256, height=256, bit_depth=8):
    """
    Generate a star pattern image.
    
    Args:
        width: Image width
        height: Image height
        bit_depth: Bit depth (4 or 8)
    
    Returns:
        numpy array with the star pattern
    """
    max_val = (1 << bit_depth) - 1  # 15 for 4-bit, 255 for 8-bit
    
    # Create coordinate grids
    y, x = np.ogrid[:height, :width]
    center_x, center_y = width // 2, height // 2
    
    # Calculate angle from center
    angle = np.arctan2(y - center_y, x - center_x)
    
    # Calculate distance from center
    distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    max_distance = np.sqrt(center_x**2 + center_y**2)
    
    # Create star pattern with 5 points
    num_points = 5
    star_pattern = np.abs(np.sin(num_points * angle))
    
    # Combine with radial gradient
    radial_factor = 1 - (distance / max_distance)
    pattern = star_pattern * radial_factor
    
    # Normalize to bit depth range
    pattern = (pattern * max_val).astype(np.uint8)
    
    return pattern


def generate_gradient_pattern(width=256, height=256, bit_depth=8):
    """
    Generate a gradient pattern image.
    
    Args:
        width: Image width
        height: Image height
        bit_depth: Bit depth (4 or 8)
    
    Returns:
        numpy array with the gradient pattern
    """
    max_val = (1 << bit_depth) - 1  # 15 for 4-bit, 255 for 8-bit
    
    # Create a diagonal gradient
    y, x = np.ogrid[:height, :width]
    
    # Diagonal gradient from top-left to bottom-right
    gradient = (x + y) / (width + height - 2)
    
    # Normalize to bit depth range
    pattern = (gradient * max_val).astype(np.uint8)
    
    return pattern


def generate_stripes_pattern(width=256, height=256, bit_depth=8, num_stripes=8):
    """
    Generate a stripes pattern image.
    
    Args:
        width: Image width
        height: Image height
        bit_depth: Bit depth (4 or 8)
        num_stripes: Number of vertical stripes
    
    Returns:
        numpy array with the stripes pattern
    """
    max_val = (1 << bit_depth) - 1  # 15 for 4-bit, 255 for 8-bit
    
    # Create vertical stripes
    x = np.arange(width)
    stripe_width = width / num_stripes
    
    # Generate stripe values that vary in intensity
    stripe_values = (np.floor(x / stripe_width) % num_stripes) / (num_stripes - 1)
    pattern = np.tile(stripe_values, (height, 1))
    
    # Normalize to bit depth range
    pattern = (pattern * max_val).astype(np.uint8)
    
    return pattern


def save_image(pattern, filename, bit_depth=8):
    """
    Save the pattern as a PNG image.
    For 4-bit depth, saves as 8-bit PNG with values limited to 0-15.
    
    Args:
        pattern: numpy array containing the image data
        filename: output filename
        bit_depth: bit depth of the image (4 or 8)
    """
    # Ensure the pattern is in the correct range
    if bit_depth == 4:
        # Clamp values to 0-15 range for 4-bit
        pattern = np.clip(pattern, 0, 15)
    
    # Convert to PIL Image and save
    img = Image.fromarray(pattern, mode='L')
    img.save(filename, 'PNG')
    print(f"Saved {filename} ({bit_depth}-bit depth)")


def view_image(filename):
    """
    View an image with proper rescaling for 4-bit images.
    4-bit images (values 0-15) are rescaled to 0-255 for proper visualization.
    
    Args:
        filename: Path to the image file
    """
    img = Image.open(filename)
    img_array = np.array(img)
    
    # Detect if it's 4-bit
    unique_vals = np.unique(img_array)
    is_4bit = len(unique_vals) <= 16 and np.max(img_array) <= 15
    
    # Create display array - rescale 4-bit to 0-255 for visualization
    if is_4bit:
        display_array = (img_array * 17).astype(np.uint8)  # 15 * 17 = 255
        bit_info = "4-bit (rescaled 0-15 → 0-255 for display)"
    else:
        display_array = img_array
        bit_info = "8-bit"
    
    # Display    
    # Show rescaled image
    im = plt.imshow(display_array, cmap='gray', vmin=0, vmax=255)
    plt.title(f'{filename}\n{bit_info}')
    plt.axis('off')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate and view test images with different patterns and bit depths',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a single image
  python image_generator.py --generate --pattern star --bit-depth 4 --output star.png
  
  # View an image (rescales 4-bit to 0-255 for proper visualization)
  python image_generator.py --view star.png
  
  # Generate with custom size
  python image_generator.py --generate --pattern gradient --bit-depth 8 --output grad.png --width 512 --height 512
        """
    )
    
    parser.add_argument(
        '--generate',
        action='store_true',
        help='Generate an image'
    )
    
    parser.add_argument(
        '--view',
        type=str,
        metavar='FILE',
        help='View an image file (4-bit images are rescaled to 0-255 for display)'
    )
    
    parser.add_argument(
        '--pattern',
        choices=['star', 'gradient', 'stripes'],
        help='Pattern to generate (required with --generate)'
    )
    
    parser.add_argument(
        '--bit-depth',
        type=int,
        choices=[4, 8],
        help='Bit depth: 4 or 8 (required with --generate)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output filename (required with --generate)'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        default=256,
        help='Image width (default: 256)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=256,
        help='Image height (default: 256)'
    )
    
    args = parser.parse_args()
    
    # Generate image
    if args.generate:
        if not args.pattern or not args.bit_depth or not args.output:
            parser.error('--generate requires --pattern, --bit-depth, and --output')
        
        pattern_funcs = {
            'star': generate_star_pattern,
            'gradient': generate_gradient_pattern,
            'stripes': generate_stripes_pattern
        }
        
        print(f"Generating {args.pattern} pattern at {args.bit_depth}-bit depth...")
        pattern = pattern_funcs[args.pattern](args.width, args.height, args.bit_depth)
        save_image(pattern, args.output, args.bit_depth)
    
    # View image
    elif args.view:
        print(f"Viewing {args.view}...")
        view_image(args.view)
    
    else:
        parser.print_help()



