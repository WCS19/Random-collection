import time
from pathlib import Path
import lz77_codec


class CompressionMetrics:
    def __init__(self, original_size, compressed_size, compression_time, decompression_time):
        self.original_size = original_size
        self.compressed_size = compressed_size
        self.compression_time = compression_time
        self.decompression_time = decompression_time

        self.compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
        self.compression_factor = compressed_size / original_size if original_size > 0 else 0
        self.space_savings = (1 - self.compression_factor) * 100.0
        self.bits_per_byte = (compressed_size * 8.0) / original_size if original_size > 0 else 0

        original_size_mb = original_size / (1024.0 * 1024.0)
        self.compression_throughput = original_size_mb / compression_time if compression_time > 0 else 0
        self.decompression_throughput = original_size_mb / decompression_time if decompression_time > 0 else 0

        self.composite_score = (
            self.compression_ratio * self.decompression_throughput / self.compression_time
            if self.compression_time > 0 else 0
        )

    def __str__(self):
        return (
            f"Compression Metrics:\n"
            f"  Original size: {self.original_size:,} bytes\n"
            f"  Compressed size: {self.compressed_size:,} bytes\n"
            f"  Compression ratio: {self.compression_ratio:.2f}x\n"
            f"  Space savings: {self.space_savings:.2f}%\n"
            f"  Bits per byte: {self.bits_per_byte:.2f}\n"
            f"  Compression time: {self.compression_time:.4f} seconds\n"
            f"  Decompression time: {self.decompression_time:.4f} seconds\n"
            f"  Compression throughput: {self.compression_throughput:.2f} MB/s\n"
            f"  Decompression throughput: {self.decompression_throughput:.2f} MB/s\n"
            f"  Composite efficiency score: {self.composite_score:.2f}"
        )


class LZCompressor:
    @staticmethod
    def compress_file(input_path, output_path=None):
        input_path = Path(input_path)
        if not output_path:
            output_path = str(input_path) + '.lz'

        with open(input_path, 'rb') as f:
            data = f.read()

        original_size = len(data)

        start_time = time.time()
        compressed_data = lz77_codec.compress(data)
        compression_time = time.time() - start_time

        compressed_size = len(compressed_data)
        metadata = original_size.to_bytes(4, byteorder='big')

        with open(output_path, 'wb') as f:
            f.write(metadata)
            f.write(compressed_data)

        start_time = time.time()
        _ = lz77_codec.decompress(compressed_data, original_size)
        decompression_time = time.time() - start_time

        metrics = CompressionMetrics(
            original_size=original_size,
            compressed_size=compressed_size + len(metadata),
            compression_time=compression_time,
            decompression_time=decompression_time,
        )

        print(f"File compressed: {input_path} -> {output_path}")
        print(metrics)
        return metrics

    @staticmethod
    def decompress_file(input_path, output_path=None):
        input_path = Path(input_path)
        if not output_path:
            if str(input_path).endswith('.lz'):
                output_path = str(input_path)[:-3]
            else:
                output_path = str(input_path) + '.decompressed'

        with open(input_path, 'rb') as f:
            metadata = f.read(4)
            original_size = int.from_bytes(metadata, byteorder='big')
            compressed_data = f.read()

        start_time = time.time()
        decompressed_data = lz77_codec.decompress(compressed_data, original_size)
        decompression_time = time.time() - start_time

        with open(output_path, 'wb') as f:
            f.write(decompressed_data)

        original_size_mb = original_size / (1024.0 * 1024.0)
        decompression_throughput = (
            original_size_mb / decompression_time if decompression_time > 0 else 0
        )

        print(f"File decompressed: {input_path} -> {output_path}")
        print(f"Original size: {original_size:,} bytes")
        print(f"Decompression time: {decompression_time:.4f} seconds")
        print(f"Decompression throughput: {decompression_throughput:.2f} MB/s")

        return decompression_time


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LZ Lossless Compression Utility")
    parser.add_argument('action', choices=['compress', 'decompress'])
    parser.add_argument('input_file')
    parser.add_argument('-o', '--output')

    args = parser.parse_args()

    if args.action == 'compress':
        LZCompressor.compress_file(args.input_file, args.output)
    else:
        LZCompressor.decompress_file(args.input_file, args.output)
