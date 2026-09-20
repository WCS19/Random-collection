import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np
from lz77_compression import LZCompressor


def verify_images(original_path, decompressed_path):
    original_array = np.array(Image.open(original_path))
    decompressed_array = np.array(Image.open(decompressed_path))

    if original_array.shape != decompressed_array.shape:
        print(f"ERROR: Image dimensions don't match!")
        print(f"Original: {original_array.shape}")
        print(f"Decompressed: {decompressed_array.shape}")
        return False

    if not np.array_equal(original_array, decompressed_array):
        diff = np.sum(original_array != decompressed_array)
        total = np.prod(original_array.shape)
        print(f"ERROR: Images differ by {diff} pixels ({(diff / total) * 100:.6f}%)")
        return False

    print("SUCCESS: Decompressed image is identical to the original")
    return True


def test_image_compression(image_path):
    image_path = Path(image_path)
    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}")
        return

    compressed_path = image_path.with_suffix('.lz')
    decompressed_path = image_path.with_suffix('.decompressed' + image_path.suffix)

    original_size = os.path.getsize(image_path)
    print(f"Original image: {image_path}")
    print(f"Size: {original_size:,} bytes")

    print("\nCompressing image...")
    metrics = LZCompressor.compress_file(image_path, compressed_path)

    print("\nDecompressing image...")
    LZCompressor.decompress_file(compressed_path, decompressed_path)

    print("\nVerifying results...")
    if verify_images(image_path, decompressed_path):
        print("\nCompression Summary:")
        print(f"Compression ratio: {metrics.compression_ratio:.2f}x")
        print(f"Space savings: {metrics.space_savings:.2f}%")
        print(f"Bits per byte: {metrics.bits_per_byte:.2f}")
        print(f"Compression throughput: {metrics.compression_throughput:.2f} MB/s")
        print(f"Decompression throughput: {metrics.decompression_throughput:.2f} MB/s")
        print(f"Composite efficiency score: {metrics.composite_score:.2f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_image_compression.py <image_path>")
        sys.exit(1)
    test_image_compression(sys.argv[1])
