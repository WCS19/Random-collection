#!/usr/bin/env python3
"""Test BlockDelta on image files."""

import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np
from block_delta import BlockDeltaCompressor


def verify_images(original_path, decompressed_path):
    original_img = Image.open(original_path)
    decompressed_img = Image.open(decompressed_path)

    if original_img.size != decompressed_img.size:
        print(f"ERROR: Image dimensions don't match!")
        print(f"Original: {original_img.size}, Decompressed: {decompressed_img.size}")
        return False

    original_array = np.array(original_img)
    decompressed_array = np.array(decompressed_img)

    diff = np.sum(original_array != decompressed_array)
    if diff > 0:
        percent_diff = (diff / original_array.size) * 100
        print(f"ERROR: Images differ by {diff} pixels ({percent_diff:.6f}%)")
        return False

    print("SUCCESS: Decompressed image is identical to the original")
    return True


def test_image_compression(image_path):
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}")
        return False

    compressed_path = image_path.with_suffix('.bkdt')
    decompressed_path = image_path.with_suffix('.decompressed' + image_path.suffix)

    original_size = os.path.getsize(image_path)
    print(f"Original image: {image_path}")
    print(f"Size: {original_size:,} bytes")

    print("\nCompressing image...")
    BlockDeltaCompressor.compress_file(image_path, compressed_path)

    print("\nDecompressing image...")
    BlockDeltaCompressor.decompress_file(compressed_path, decompressed_path)

    compressed_size = os.path.getsize(compressed_path)
    success = verify_images(image_path, decompressed_path)

    print("\nCompression Results:")
    print(f"Original size: {original_size:,} bytes")
    print(f"Compressed size: {compressed_size:,} bytes")

    if compressed_size < original_size:
        ratio = original_size / compressed_size
        savings = (1 - (compressed_size / original_size)) * 100
        print(f"Compression ratio: {ratio:.2f}x")
        print(f"Space savings: {savings:.2f}%")
    else:
        print("No space savings (compressed file is larger than original)")

    return success


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_image_blockalgo.py <image_path>")
    else:
        test_image_compression(sys.argv[1])
