#!/usr/bin/env python3
"""Verify BlockDelta is lossless on predictable synthetic inputs."""

import os
import sys
from pathlib import Path
from block_delta import BlockDeltaCompressor


def create_test_file(filename, size_kb, pattern_type="simple"):
    size_bytes = size_kb * 1024
    data = bytearray()

    if pattern_type == "simple":
        pattern = bytes([i % 256 for i in range(64)])
        repetitions = size_bytes // len(pattern) + 1
        data = (pattern * repetitions)[:size_bytes]

    elif pattern_type == "graduated":
        block_size = 256
        num_blocks = (size_bytes + block_size - 1) // block_size
        for i in range(num_blocks):
            block_pattern = bytes([(i + j) % 256 for j in range(block_size)])
            data.extend(block_pattern[:min(block_size, size_bytes - len(data))])
            if len(data) >= size_bytes:
                break

    with open(filename, "wb") as f:
        f.write(data[:size_bytes])

    print(f"Created verification file: {filename} ({size_kb} KB, {pattern_type} pattern)")
    return filename


def verify_lossless(filename):
    print(f"\nVerifying lossless compression on {filename}")
    print("-" * 50)

    original_copy = f"{filename}.original"
    with open(filename, "rb") as f_in, open(original_copy, "wb") as f_out:
        f_out.write(f_in.read())

    compressed_file = f"{filename}.bkdt"
    print("Compressing...")
    BlockDeltaCompressor.compress_file(filename, compressed_file)

    original_size = os.path.getsize(filename)
    compressed_size = os.path.getsize(compressed_file)
    ratio = original_size / compressed_size if compressed_size > 0 else 0

    print(f"Original size: {original_size:,} bytes")
    print(f"Compressed size: {compressed_size:,} bytes")
    print(f"Compression ratio: {ratio:.2f}x")

    decompressed_file = f"{filename}.decompressed"
    print("\nDecompressing...")
    BlockDeltaCompressor.decompress_file(compressed_file, decompressed_file)

    with open(original_copy, "rb") as f1, open(decompressed_file, "rb") as f2:
        data1 = f1.read()
        data2 = f2.read()

        if len(data1) != len(data2):
            print(f"❌ FAILED: Size mismatch - original={len(data1)}, decompressed={len(data2)}")
            return False

        diff_count = 0
        diff_positions = []
        for i, (b1, b2) in enumerate(zip(data1, data2)):
            if b1 != b2:
                diff_count += 1
                if len(diff_positions) < 10:
                    diff_positions.append((i, b1, b2))

        if diff_count == 0:
            print("✅ SUCCESS: Decompressed data is byte-for-byte identical to original")
            return True

        print(f"❌ FAILED: {diff_count} bytes differ ({diff_count/len(data1)*100:.2f}%)")
        print("First few differences:")
        for pos, orig, decomp in diff_positions:
            print(f"  Position {pos}: original=0x{orig:02x}, decompressed=0x{decomp:02x}")
        return False


def main():
    test_dir = Path("verification_data")
    test_dir.mkdir(exist_ok=True)

    test_cases = [
        ("simple", 10),
        ("simple", 100),
        ("graduated", 10),
        ("graduated", 100),
    ]

    success_count = 0
    for pattern_type, size_kb in test_cases:
        filename = test_dir / f"{pattern_type}_{size_kb}kb.bin"
        create_test_file(filename, size_kb, pattern_type)
        if verify_lossless(filename):
            success_count += 1

    total = len(test_cases)
    print(f"\nSummary: {success_count}/{total} tests passed")

    if success_count == total:
        print("✅ ALL TESTS PASSED: BlockDelta compression is lossless")
        return 0

    print("❌ SOME TESTS FAILED: BlockDelta compression is not lossless")
    return 1


if __name__ == "__main__":
    sys.exit(main())
