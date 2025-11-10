# Shamir's Secret Sharing for Images

**By Team: Abhinav, Nikhil, Pranjal (Cryptography Team 6)**

We have added support for:

- RGB and Grayscale images
- Different intensity ranges (4-bit, 8-bit, 16-bit)
- Automatic prime selection based on image properties
- Metadata storage in shares (x-coordinate, prime, mode, shape)
- Interactive visualization and drawing tools

## Project Structure

```
CryptoShamirSecretSharing/
├── main.py                    # CLI entry point
├── core/                      # Core modules
│   ├── __init__.py           # Module exports
│   ├── field_math.py         # Finite field operations
│   ├── image_utils.py        # Image loading/saving utilities
│   ├── share_io.py           # Share file I/O with metadata
│   └── shamir.py             # Shamir secret sharing logic
├── view.py                    # Share visualization tool
├── verify.py                  # Image comparison tool
├── shamir_image_shares.py     # Legacy standalone implementation
└── shares/                    # Directory for share files
```

## Quick Start

### Installation

```bash
# Install required dependencies
pip install numpy pillow matplotlib
```

### Basic Usage

#### 1. **Split an image into shares**

```bash
# Split RGB image into 5 shares with threshold 3
python main.py split input.png shares --n 5 --k 3

# Split grayscale image
python main.py split input.png shares --n 5 --k 3 --grayscale

# Split with custom prime (for special intensity ranges)
python main.py split input.png shares --n 5 --k 3 --prime 17
```

#### 2. **Reconstruct image from shares**

```bash
# Use any k shares to reconstruct
python main.py reconstruct output.png shares/share_1.npz shares/share_3.npz shares/share_5.npz
```

#### 3. **View share metadata and visualize**

```bash
# View share information and pixel values
python view.py shares/share_1.npz
```

#### 4. **Verify reconstruction**

```bash
# Compare original and reconstructed images
python verify.py input.png output.png
```

## Features

### 1. Multi-Intensity Range Support

The system automatically detects and handles different pixel intensity ranges:

| Bit Depth | Value Range | Auto-Selected Prime | Use Case |
|-----------|-------------|---------------------|----------|
| 4-bit     | 0-15        | 17                  | Low-res images, sketches |
| 8-bit     | 0-255       | 257                 | Standard images (JPEG, PNG) |
| 16-bit    | 0-65535     | 65537               | High dynamic range images |

**Example with 4-bit image (0-15 range):**
```bash
python main.py split low_res.png shares --n 5 --k 3
# Prime 17 is automatically selected
```

### 2. Grayscale and RGB Support

- **Auto-detect**: Automatically handles both grayscale and RGB images
- **Force grayscale**: Convert RGB to grayscale during split
  ```bash
  python main.py split color_image.png shares --n 5 --k 3 --grayscale
  ```

### 3. Enhanced Share Format

Each share file (`.npz`) contains:
- **`share`**: The actual share data array
- **`x`**: X-coordinate for this share (constant per pixel)
- **`prime`**: Prime used for finite field
- **`mode`**: `'grayscale'` or `'rgb'`
- **`original_shape`**: Original image dimensions

This metadata ensures:
- No dependency on filenames
- Automatic validation of share compatibility
- Proper reconstruction without guessing parameters

### 4. Interactive Visualization

The `view.py` tool provides:
- **Metadata display**: View share properties
- **Pixel intensity values**: See actual values for small images
- **Visual heatmaps**: Grayscale and RGB channel visualization
- **Interactive drawing**: Modify shares with a brush tool

## Detailed Usage

```bash
python3 main.py --help
```

## Mathematical Details

### X-Value Storage

**Design Decision**: X-values are stored in share metadata (not embedded in pixel data).

**Rationale:**

- Consistent x-value across all pixels in a share
- No dependency on filename conventions
- Simpler reconstruction logic
- Smaller share file size

## Team

- **Abhinav Lodha** (U20220003)
- **Nikhil Henry** (U20220060)
- **Pranjal Rastogi** (U20220066)

Help taken from Claude Sonnet and other online resources. Help taken from Github Copilot.
