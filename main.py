"""
Shamir's Secret Sharing on Images
Main entry point for CLI operations.

By Team: Abhinav, Nikhil, Pranjal
"""

import os
import argparse
from core import (
    load_image,
    save_image,
    detect_image_properties,
    split_image_into_shares,
    reconstruct_from_shares,
    save_share,
    load_share,
    validate_shares_compatible,
    next_prime,
)


def cmd_split(args):
    """Handle the split command to create shares from an image."""
    print(f"[INFO] Loading image: {args.input_image}")
    
    # Load image (force grayscale if requested)
    img_array = load_image(args.input_image, grayscale=args.grayscale)
    
    # Detect image properties
    props = detect_image_properties(img_array)
    print(f"[OK] Image mode: {props['mode']}")
    print(f"[OK] Image shape: {props['shape']}")
    print(f"[OK] Value range: [{props['min_value']}, {props['max_value']}]")
    print(f"[OK] Detected bit depth: {props['bit_depth']}-bit")
    
    # Determine prime to use
    if args.prime is not None:
        prime = args.prime
        if prime <= props['max_value']:
            print(f"[WARNING] Provided prime ({prime}) is not greater than max pixel value ({props['max_value']})")
            print(f"          Recommended prime: {props['recommended_prime']}")
            return
    else:
        prime = props['recommended_prime']
    
    print(f"[OK] Using prime: {prime}")
    
    # Split image into shares
    print(f"\n[INFO] Splitting image into {args.n} shares (threshold k={args.k})...")
    shares = split_image_into_shares(img_array, args.n, args.k, prime)
    
    # Save shares to files
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"\n[INFO] Saving shares to: {args.output_dir}")
    
    for x, share_array in shares.items():
        filepath = os.path.join(args.output_dir, f"share_{x}.npz")
        save_share(share_array, x, prime, props['mode'], props['shape'], filepath)
        print(f"  [OK] Saved share_{x}.npz (x={x})")
    
    print(f"\n[SUCCESS] Created {args.n} shares with threshold {args.k}")
    print(f"          Any {args.k} shares can reconstruct the original image.")


def cmd_reconstruct(args):
    """Handle the reconstruct command to rebuild image from shares."""
    print(f"[INFO] Loading {len(args.share_files)} shares...")
    
    # Load all shares
    share_data_list = []
    for filepath in args.share_files:
        share_data = load_share(filepath)
        share_data_list.append(share_data)
        print(f"  [OK] Loaded {os.path.basename(filepath)} (x={share_data['x']})")
    
    # Validate shares are compatible
    try:
        validate_shares_compatible(share_data_list)
    except ValueError as e:
        print(f"\n[ERROR] {e}")
        return
    
    # Extract data from shares
    share_arrays = [sd['share'] for sd in share_data_list]
    xs = [sd['x'] for sd in share_data_list]
    prime = share_data_list[0]['prime']
    mode = share_data_list[0]['mode']
    
    print(f"\n[OK] All shares compatible")
    print(f"     Prime: {prime}")
    print(f"     Mode: {mode}")
    print(f"     X values: {xs}")
    
    # Reconstruct image
    print(f"\n[INFO] Reconstructing image...")
    reconstructed = reconstruct_from_shares(share_arrays, xs, prime)
    
    # Save reconstructed image
    save_image(reconstructed, args.output_image, mode=mode)
    print(f"\n[SUCCESS] Reconstructed image saved to: {args.output_image}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Shamir's Secret Sharing on Images - By Team Abhinav, Nikhil, Pranjal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split an image into 5 shares with threshold 3 (auto-detect prime):
  python main.py split input.png shares --n 5 --k 3

  # Split with custom prime:
  python main.py split input.png shares --n 5 --k 3 --prime 257

  # Split grayscale image:
  python main.py split input.png shares --n 5 --k 3 --grayscale

  # Reconstruct from shares:
  python main.py reconstruct output.png shares/share_1.npz shares/share_3.npz shares/share_5.npz
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Split command
    split_parser = subparsers.add_parser(
        'split',
        help='Split an image into shares'
    )
    split_parser.add_argument(
        'input_image',
        type=str,
        help='Path to input image file'
    )
    split_parser.add_argument(
        'output_dir',
        type=str,
        help='Directory to save share files'
    )
    split_parser.add_argument(
        '--n',
        type=int,
        required=True,
        help='Total number of shares to create'
    )
    split_parser.add_argument(
        '--k',
        type=int,
        required=True,
        help='Threshold number of shares needed for reconstruction'
    )
    split_parser.add_argument(
        '--prime',
        type=int,
        default=None,
        help='Prime number for finite field (auto-detected if not provided)'
    )
    split_parser.add_argument(
        '--grayscale',
        action='store_true',
        help='Force grayscale mode (convert RGB to grayscale)'
    )
    
    # Reconstruct command
    reconstruct_parser = subparsers.add_parser(
        'reconstruct',
        help='Reconstruct an image from shares'
    )
    reconstruct_parser.add_argument(
        'output_image',
        type=str,
        help='Path to save reconstructed image file'
    )
    reconstruct_parser.add_argument(
        'share_files',
        type=str,
        nargs='+',
        help='Paths to share files for reconstruction (at least k shares)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    try:
        if args.command == 'split':
            cmd_split(args)
        elif args.command == 'reconstruct':
            cmd_reconstruct(args)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())