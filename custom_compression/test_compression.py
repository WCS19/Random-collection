#!/usr/bin/env python3
"""Benchmark BlockDelta on synthetic data patterns."""

import os
import sys
import random
from pathlib import Path
from block_delta import BlockDeltaCompressor


def create_test_file(filename, size_kb, pattern_type="random"):
    size_bytes = size_kb * 1024
    data = bytearray()

    if pattern_type == "random":
        data = random.randbytes(size_bytes)

    elif pattern_type == "repeat":
        patterns = [random.randbytes(random.randint(4, 64)) for _ in range(5)]
        while len(data) < size_bytes:
            pattern = random.choice(patterns)
            data.extend(pattern * random.randint(1, 50))
        data = data[:size_bytes]

    elif pattern_type == "text":
        words = [
            "the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog",
            "hello", "world", "computer", "science", "algorithm", "python",
            "compression", "data", "block", "delta", "encode", "bytes",
        ]
        text = ""
        while len(text.encode("utf-8")) < size_bytes:
            sentence_len = random.randint(5, 15)
            text += " ".join(random.choice(words) for _ in range(sentence_len)) + ". "
        data = text.encode("utf-8")[:size_bytes]

    elif pattern_type == "zeroes":
        data = bytearray(size_bytes)
        for pos in random.sample(range(size_bytes), size_bytes // 20):
            data[pos] = random.randint(1, 255)

    with open(filename, "wb") as f:
        f.write(data)

    print(f"Created test file: {filename} ({size_kb} KB, {pattern_type} pattern)")
    return filename


def test_compression(filename):
    print(f"\nTesting compression on {filename}")
    print("-" * 50)

    compressed_file = f"{filename}.bkdt"
    print("Compressing...")
    BlockDeltaCompressor.compress_file(filename, compressed_file)

    original_size = os.path.getsize(filename)
    compressed_size = os.path.getsize(compressed_file)
    ratio = original_size / compressed_size if compressed_size > 0 else 0
    savings = (1 - (compressed_size / original_size)) * 100 if original_size > 0 else 0

    print(f"Original size: {original_size:,} bytes")
    print(f"Compressed size: {compressed_size:,} bytes")
    print(f"Compression ratio: {ratio:.2f}x")
    print(f"Space savings: {savings:.2f}%")

    decompressed_file = f"{filename}.decompressed"
    print("\nDecompressing...")
    BlockDeltaCompressor.decompress_file(compressed_file, decompressed_file)

    with open(filename, "rb") as f1, open(decompressed_file, "rb") as f2:
        data1 = f1.read()
        data2 = f2.read()

        if data1 == data2:
            print("✅ Verification successful: Decompressed data matches original")
        else:
            print("❌ Verification failed: Decompressed data does not match original")
            if len(data1) != len(data2):
                print(f"Size mismatch: original={len(data1)}, decompressed={len(data2)}")
            else:
                diff_count = sum(1 for a, b in zip(data1, data2) if a != b)
                print(f"Different bytes: {diff_count} ({diff_count/len(data1)*100:.2f}%)")

    print("-" * 50)
    return ratio, savings


def main():
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)

    test_files = [
        ("random", 100),
        ("repeat", 100),
        ("text", 100),
        ("zeroes", 100),
    ]

    results = []

    for pattern_type, size_kb in test_files:
        filename = test_dir / f"{pattern_type}_{size_kb}kb.bin"
        if not filename.exists():
            create_test_file(filename, size_kb, pattern_type)
        else:
            print(f"Using existing test file: {filename} ({size_kb} KB, {pattern_type} pattern)")

        ratio, savings = test_compression(filename)
        results.append((pattern_type, size_kb, ratio, savings))

    print("\nCompression Summary:")
    print("-" * 50)
    print(f"{'Pattern Type':<12} {'Size (KB)':<10} {'Ratio':<8} {'Savings':<8}")
    print("-" * 50)

    for pattern_type, size_kb, ratio, savings in results:
        print(f"{pattern_type:<12} {size_kb:<10} {ratio:<8.2f}x {savings:<8.2f}%")

    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            test_compression(filename)


if __name__ == "__main__":
    main()
