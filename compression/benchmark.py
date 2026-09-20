import os
import random
import matplotlib.pyplot as plt
from pathlib import Path
from lz77_compression import LZCompressor


class CompressionBenchmark:
    def __init__(self, output_dir="benchmark_results"):
        self.output_dir = Path(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.results = []

    def generate_test_data(self, size_kb, data_type="random"):
        size_bytes = size_kb * 1024

        if data_type == "random":
            return random.randbytes(size_bytes)

        elif data_type == "text":
            words = [
                "lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
                "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
                "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua",
            ]
            text = ""
            while len(text.encode('utf-8')) < size_bytes:
                text += " ".join(random.choices(words, k=random.randint(10, 20))) + ". "
            return text.encode('utf-8')[:size_bytes]

        elif data_type == "binary":
            patterns = []
            for _ in range(10):
                patterns.append(random.randbytes(random.randint(10, 100)))

            data = bytearray()
            while len(data) < size_bytes:
                pattern = random.choice(patterns)
                data.extend(pattern * random.randint(1, 20))
            return bytes(data[:size_bytes])

        else:
            raise ValueError(f"Unknown data type: {data_type}")

    def run_benchmark(self, sizes_kb=[10, 100, 1000], data_types=["random", "text", "binary"]):
        for data_type in data_types:
            for size_kb in sizes_kb:
                print(f"\nBenchmarking {data_type} data, {size_kb} KB...")

                test_data = self.generate_test_data(size_kb, data_type)
                test_file = self.output_dir / f"{data_type}_{size_kb}kb_test.bin"
                with open(test_file, "wb") as f:
                    f.write(test_data)

                metrics = LZCompressor.compress_file(test_file)
                self.results.append({
                    "data_type": data_type,
                    "size_kb": size_kb,
                    "metrics": metrics,
                })
                print(f"Composite Score: {metrics.composite_score:.4f}")

    def plot_results(self):
        if not self.results:
            print("No benchmark results to plot")
            return

        data_types = set(result["data_type"] for result in self.results)
        metrics = [
            ("compression_ratio", "Compression Ratio"),
            ("space_savings", "Space Savings (%)"),
            ("compression_throughput", "Compression Throughput (MB/s)"),
            ("decompression_throughput", "Decompression Throughput (MB/s)"),
            ("composite_score", "Composite Efficiency Score"),
        ]

        for metric_name, metric_label in metrics:
            plt.figure(figsize=(12, 8))

            for data_type in data_types:
                type_results = [r for r in self.results if r["data_type"] == data_type]
                type_results.sort(key=lambda r: r["size_kb"])
                sizes = [r["size_kb"] for r in type_results]
                values = [getattr(r["metrics"], metric_name) for r in type_results]
                plt.plot(sizes, values, 'o-', label=f"{data_type} data")

            plt.xlabel('Data Size (KB)')
            plt.ylabel(metric_label)
            plt.title(f'{metric_label} by Data Type and Size')
            plt.legend()
            plt.grid(True)
            plt.savefig(self.output_dir / f"{metric_name.lower()}.png")

        print(f"Plots saved to {self.output_dir}")

    def print_summary(self):
        if not self.results:
            print("No benchmark results to summarize")
            return

        print("\n=== Benchmark Summary ===")
        print(f"Total test cases: {len(self.results)}")

        data_types = set(result["data_type"] for result in self.results)

        print("\nAverages by data type:")
        for data_type in data_types:
            type_results = [r for r in self.results if r["data_type"] == data_type]
            avg_ratio = sum(r["metrics"].compression_ratio for r in type_results) / len(type_results)
            avg_savings = sum(r["metrics"].space_savings for r in type_results) / len(type_results)
            avg_score = sum(r["metrics"].composite_score for r in type_results) / len(type_results)

            print(f"  {data_type} data:")
            print(f"    Avg. Compression Ratio: {avg_ratio:.2f}x")
            print(f"    Avg. Space Savings: {avg_savings:.2f}%")
            print(f"    Avg. Composite Score: {avg_score:.2f}")

        best_ratio = max(self.results, key=lambda r: r["metrics"].compression_ratio)
        best_speed = max(self.results, key=lambda r: r["metrics"].decompression_throughput)
        best_score = max(self.results, key=lambda r: r["metrics"].composite_score)

        print("\nBest performers:")
        print(f"  Best Compression Ratio: {best_ratio['metrics'].compression_ratio:.2f}x")
        print(f"    - {best_ratio['data_type']} data, {best_ratio['size_kb']} KB")
        print(f"  Best Decompression Speed: {best_speed['metrics'].decompression_throughput:.2f} MB/s")
        print(f"    - {best_speed['data_type']} data, {best_speed['size_kb']} KB")
        print(f"  Best Composite Score: {best_score['metrics'].composite_score:.2f}")
        print(f"    - {best_score['data_type']} data, {best_score['size_kb']} KB")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark the LZ Compression Algorithm")
    parser.add_argument('--sizes', type=int, nargs='+', default=[10, 100, 1000])
    parser.add_argument('--types', type=str, nargs='+', default=["random", "text", "binary"])
    parser.add_argument('--output', type=str, default="benchmark_results")

    args = parser.parse_args()

    benchmark = CompressionBenchmark(args.output)
    benchmark.run_benchmark(args.sizes, args.types)
    benchmark.plot_results()
    benchmark.print_summary()
