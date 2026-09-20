# LZ-Based Lossless Compression

A Cython-based lossless compression algorithm implementing industry-standard metrics for evaluation.

## Overview

This compression algorithm implements an optimized variant of the LZ77 compression algorithm using Cython for high performance. The implementation provides comprehensive metrics to evaluate compression performance, including compression ratio, space savings, and throughput measurements.

## Installation

Requires a C compiler (on macOS: `xcode-select --install`), plus:

```
pip install numpy cython matplotlib
```

Then build the Cython extension (required before first use):

```
cd compression
python setup.py build_ext --inplace
```

Generated files (`lz77_codec.c`, `lz77_codec*.so`, `lz77_codec.html`, `build/`) are local artifacts and are not committed.

## Usage

### As a Command Line Tool

```bash
# Compress a file
python lz77_compression.py compress myfile.txt

# Decompress a file
python lz77_compression.py decompress myfile.txt.lz

# Specify output path
python lz77_compression.py compress myfile.txt -o compressed.bin
```

### As a Python Library

```python
from lz77_compression import LZCompressor

# Compress a file
metrics = LZCompressor.compress_file("myfile.txt", "compressed.bin")
print(metrics)  # Displays all compression metrics

# Decompress a file
LZCompressor.decompress_file("compressed.bin", "decompressed.txt")
```

## Metrics

The compression algorithm provides the following standard metrics:

### 1. Compression Ratio (CR)
- Formula: `CR = Original Size / Compressed Size`
- Interpretation: Higher is better. A CR of 4 means the file was compressed to 1/4th its original size.

### 2. Compression Factor (CF)
- Formula: `CF = Compressed Size / Original Size`
- Interpretation: Lower is better. A CF of 0.25 means 75% smaller.

### 3. Space Savings (%)
- Formula: `Space Savings = (1 - Compressed Size / Original Size) × 100`
- Interpretation: Shows how much space you saved. A result of 70% means it's 70% smaller.

### 4. Bits Per Byte
- Formula: `Bits Per Byte = Compressed Size (in bits) / Original Size (in bytes)`
- Interpretation: Lower is better. This is useful when benchmarking against entropy.

### 5. Throughput (MB/s)
- Formula: `Throughput = Size / Time`
- We report both compression and decompression throughput.

### 6. Composite Efficiency Score
- Formula: `Score = Compression Ratio × Decompression Speed / Compression Time`
- A custom composite score balancing compression ratio and speed.

## Benchmarking

The package includes a benchmarking tool to measure the performance of the compression algorithm on different types of data:

```bash
python benchmark.py --sizes 10 100 1000 --types random text binary
```

The benchmark will:
1. Generate test data of different sizes and types
2. Measure various compression metrics
3. Generate plots for each metric
4. Print a summary report with averages and best performers

## Implementation Details

- The algorithm uses a sliding window approach (LZ77 variant)
- Cython with C-level optimizations for performance
- Fast pattern matching with buffer management
- Tuned parameters for optimal balance between speed and compression ratio
- Custom format with minimal overhead for storing compressed data

## License

MIT 