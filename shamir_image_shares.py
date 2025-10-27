"""
shamir_image_shares.py

Usage examples:
  # Create 5 shares with threshold 3:
  python shamir_image_shares.py split input.png outdir --n 5 --k 3

  # Reconstruct from any 3 share files (share_1.npz, share_3.npz, share_5.npz):
  python shamir_image_shares.py reconstruct outdir/reconstructed.png outdir/share_1.npz outdir/share_3.npz outdir/share_5.npz
"""

import os
import argparse
import numpy as np
from PIL import Image

PRIME = 257  # finite field prime, >255 so every byte fits


# ----------------- finite-field helpers -----------------
def modinv(a, p=PRIME):
    a = int(a) % p
    if a == 0:
        raise ZeroDivisionError("Inverse of 0 does not exist")
    # Extended Euclidean
    lm, hm = 1, 0
    low, high = a % p, p
    while low > 1:
        r = high // low
        nm, new = hm - lm * r, high - low * r
        lm, low, hm, high = nm, new, lm, low
    return lm % p


def lagrange_coeffs_at_zero(xs, p=PRIME):
    """
    Given xs = [x1, x2, ..., xk] (distinct, nonzero),
    returns list of scalar L_i values (mod p) such that:
      secret = sum_i (y_i * L_i) mod p
    where L_i = prod_{j != i} (-x_j) * inv(x_i - x_j)
    """
    k = len(xs)
    xs = [int(x) % p for x in xs]
    coeffs = []
    for i in range(k):
        xi = xs[i]
        num = 1
        den = 1
        for j in range(k):
            if j == i:
                continue
            xj = xs[j]
            num = (num * (-xj)) % p  # evaluate basis at 0 -> multiply by (-xj)
            den = (den * (xi - xj)) % p
        inv_den = modinv(den, p)
        coeffs.append((num * inv_den) % p)
    return coeffs


# ----------------- core functions -----------------
def split_image_into_shares(img_arr, n, k, rng=None):
    """
    img_arr: H x W x 3 uint8 numpy array (values 0..255)
    Returns dict mapping x (1..n) -> share_array (H x W x 3) dtype=np.uint16
    """
    if rng is None:
        rng = np.random.default_rng()

    H, W, C = img_arr.shape
    assert C == 3, "Input must be RGB"

    # Secret values in field (0..255) -> we work mod PRIME
    secrets = img_arr.astype(np.int64)  # shape H,W,3

    # Generate random polynomial coefficients for each pixel/channel:
    # degree k-1 => k coefficients with coeff[0] = secret
    # We'll create coefficients shape (k, H, W, 3)
    coeffs = np.empty((k, H, W, 3), dtype=np.int64)
    coeffs[0] = secrets  # constant term is secret
    # other coefficients random in 0..PRIME-1
    for j in range(1, k):
        coeffs[j] = rng.integers(0, PRIME, size=(H, W, 3), dtype=np.int64)

    shares = {}
    for x in range(1, n + 1):
        # Evaluate polynomial at x: y = sum_{j=0}^{k-1} coeffs[j] * x^j  (mod PRIME)
        x_pow = 1
        y = np.zeros_like(secrets, dtype=np.int64)
        for j in range(k):
            y = (y + coeffs[j] * x_pow) % PRIME
            x_pow = (x_pow * x) % PRIME
        # store as uint16 arrays so values up to 256 fit (0..256)
        shares[x] = y.astype(np.uint16)
    return shares


def reconstruct_from_shares(share_arrays, xs):
    """
    share_arrays: list of numpy arrays (each H x W x 3) dtype integer (0..PRIME-1)
    xs: list of x positions corresponding to each share (same length)
    Returns reconstructed image array H x W x 3 dtype uint8
    """
    p = PRIME
    k = len(xs)
    if k != len(share_arrays):
        raise ValueError("Number of xs must equal number of share arrays")

    # compute scalar Lagrange coefficients (same for all pixels)
    Ls = lagrange_coeffs_at_zero(xs, p=p)  # length k, ints mod p

    # combine: secret = sum_i y_i * L_i mod p
    # Cast arrays to int64 to avoid overflow
    accum = None
    for li, y in zip(Ls, share_arrays):
        y_int = y.astype(np.int64) % p
        term = (y_int * int(li)) % p
        if accum is None:
            accum = term
        else:
            accum = (accum + term) % p

    # result should be in 0..255 (original image). Convert to uint8
    secret = accum.astype(np.int64) % p
    # sanity check: any pixel equal to 256 would be unusual if original was 0..255
    if np.any(secret == 256):
        # if this happens, wrap 256 -> 0 (since original bytes are 0..255)
        secret = np.where(secret == 256, 0, secret)
    return secret.astype(np.uint8)


# ----------------- file helpers -----------------
def save_share_npz(share_array, filename):
    # saves as numpy .npz (uint16)
    np.savez_compressed(filename, share=share_array)


def load_share_npz(filename):
    data = np.load(filename)
    return data["share"].astype(np.uint16)


def save_uint8_image(arr, filename):
    im = Image.fromarray(arr, mode="RGB")
    im.save(filename)


# ----------------- CLI -----------------
def cmd_split(args):
    img = Image.open(args.input).convert("RGB")
    arr = np.array(img, dtype=np.uint8)
    shares = split_image_into_shares(arr, args.n, args.k)
    os.makedirs(args.outdir, exist_ok=True)
    for x, sarr in shares.items():
        path = os.path.join(args.outdir, f"share_{x}.npz")
        save_share_npz(sarr, path)
        print(f"Saved share {x} -> {path}")
    print(f"Split complete: {args.n} shares, threshold {args.k}")


def cmd_reconstruct(args):
    # args.share_files are file paths; xs are extracted from filenames if they match share_X.npz,
    # otherwise user must provide integer xs as --xs
    share_files = args.share_files
    xs = []
    for f in share_files:
        base = os.path.basename(f)
        # try parsing share_X.npz
        if base.startswith("share_") and base.endswith(".npz"):
            try:
                x = int(base.split("_")[1].split(".")[0])
            except:
                x = None
        else:
            x = None
        if x is None:
            raise ValueError(
                f"Could not infer x from filename {f}. Name shares 'share_<x>.npz'"
            )
        xs.append(x)

    # load arrays
    share_arrays = [load_share_npz(f) for f in share_files]
    recon = reconstruct_from_shares(share_arrays, xs)
    save_uint8_image(recon, args.output)
    print(f"Reconstructed image saved to {args.output}")


def main():
    p = argparse.ArgumentParser(description="Shamir image secret sharing (RGB)")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("split")
    sp.add_argument("input", help="input RGB image (PNG/JPG)")
    sp.add_argument("outdir", help="output directory for shares (.npz)")
    sp.add_argument("--n", type=int, default=5, help="number of shares (default 5)")
    sp.add_argument("--k", type=int, default=3, help="threshold k (default 3)")

    rp = sub.add_parser("reconstruct")
    rp.add_argument("output", help="reconstructed output PNG path")
    rp.add_argument(
        "share_files", nargs="+", help="paths to share .npz files (at least k)"
    )

    args = p.parse_args()
    if args.cmd == "split":
        if not (2 <= args.k <= args.n <= 255):
            raise SystemExit("Require 2 <= k <= n <= 255")
        cmd_split(args)
    elif args.cmd == "reconstruct":
        if len(args.share_files) < 2:
            raise SystemExit("Provide at least 2 shares to reconstruct (and >= k).")
        cmd_reconstruct(args)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
