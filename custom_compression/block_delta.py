#!/usr/bin/env python3
"""
BlockDelta: 
A custom compression algorithm that works by storing delta changes between blocks
with hash-based lookups and entropy encoding for better performance and compression.
"""

import time
import struct
import argparse
import heapq
from pathlib import Path
from collections import Counter, defaultdict

BLOCK_SIZE = 256
MAX_DELTA_PERCENTAGE = 50
MAGIC_BYTES = b'BKDT'
VERSION = 2
HASH_SEED = 0x811C9DC5  # FNV-1a
HASH_PRIME = 0x01000193


class HuffmanNode:
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right
        self.bit = None

    def __lt__(self, other):
        return self.freq < other.freq


class EntropyEncoder:
    @staticmethod
    def build_frequency_table(data):
        return Counter(data)

    @staticmethod
    def build_huffman_tree(freq_table):
        heap = [HuffmanNode(symbol=symbol, freq=freq) for symbol, freq in freq_table.items()]
        heapq.heapify(heap)

        if len(heap) == 1:
            node = heapq.heappop(heap)
            root = HuffmanNode(freq=node.freq, left=node)
            node.bit = 0
            return root

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            left.bit = 0
            right.bit = 1
            parent = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, parent)

        return heapq.heappop(heap)

    @staticmethod
    def build_encoding_table(tree):
        encoding_table = {}

        def traverse(node, code):
            if node.symbol is not None:
                encoding_table[node.symbol] = code
                return
            if node.left:
                traverse(node.left, code + "0")
            if node.right:
                traverse(node.right, code + "1")

        traverse(tree, "")
        return encoding_table

    @staticmethod
    def serialize_huffman_tree(tree):
        # Preorder: 0 = internal, 1 = leaf + symbol
        serialized = []

        def traverse(node):
            if node.symbol is not None:
                serialized.append(1)
                serialized.append(node.symbol)
                return
            serialized.append(0)
            if node.left:
                traverse(node.left)
            if node.right:
                traverse(node.right)

        traverse(tree)
        return bytes(serialized)

    @staticmethod
    def deserialize_huffman_tree(data, pos=0):
        if data[pos] == 1:
            symbol = data[pos + 1]
            return HuffmanNode(symbol=symbol), pos + 2

        node = HuffmanNode()
        pos += 1
        left, pos = EntropyEncoder.deserialize_huffman_tree(data, pos)
        node.left = left
        left.bit = 0
        right, pos = EntropyEncoder.deserialize_huffman_tree(data, pos)
        node.right = right
        right.bit = 1
        return node, pos

    @staticmethod
    def encode(data, encoding_table):
        bit_string = ""
        for symbol in data:
            bit_string += encoding_table[symbol]

        padding = (8 - len(bit_string) % 8) % 8
        bit_string += "0" * padding

        result = bytearray()
        for i in range(0, len(bit_string), 8):
            result.append(int(bit_string[i:i+8], 2))

        return bytes(result), padding

    @staticmethod
    def decode(encoded_data, tree, padding, length):
        bit_string = ""
        for byte in encoded_data:
            bit_string += format(byte, '08b')

        bit_string = bit_string[:-padding] if padding else bit_string

        result = bytearray()
        node = tree

        for bit in bit_string:
            node = node.left if bit == "0" else node.right
            if node.symbol is not None:
                result.append(node.symbol)
                node = tree
                if len(result) >= length:
                    break

        return bytes(result)


class BlockDeltaCompressor:
    @staticmethod
    def hash_block(block, seed=HASH_SEED):
        hash_value = seed
        for byte in block:
            hash_value ^= byte
            hash_value = (hash_value * HASH_PRIME) & 0xFFFFFFFF
        return hash_value

    @staticmethod
    def compute_block_signature(block):
        if not block:
            return (0, 0, 0, 0)

        if len(block) >= 4:
            quarter = len(block) // 4
            samples = [block[0], block[quarter], block[2 * quarter], block[-1]]
        else:
            samples = list(block) + [0] * (4 - len(block))

        return (samples[0], samples[1], min(block), max(block), sum(block) // len(block))

    @staticmethod
    def compress(input_data):
        start_time = time.time()

        # Header: MAGIC(4) + VERSION(1) + BLOCK_SIZE(2) + ORIGINAL_SIZE(4)
        output = bytearray()
        output.extend(MAGIC_BYTES)
        output.append(VERSION)
        output.extend(struct.pack(">H", BLOCK_SIZE))
        output.extend(struct.pack(">I", len(input_data)))

        blocks = [input_data[i:i+BLOCK_SIZE] for i in range(0, len(input_data), BLOCK_SIZE)]

        raw_delta_data = bytearray()
        block_metadata = []
        hash_table = defaultdict(list)
        signature_table = defaultdict(list)
        reference_blocks = {}

        for i, block in enumerate(blocks):
            if i == 0:
                block_metadata.append((0, len(block)))
                raw_delta_data.extend(block)

                block_hash = BlockDeltaCompressor.hash_block(block)
                hash_table[block_hash].append(i)
                signature = BlockDeltaCompressor.compute_block_signature(block)
                signature_table[signature].append(i)
                reference_blocks[i] = block
                continue

            candidates = []

            block_hash = BlockDeltaCompressor.hash_block(block)
            if block_hash in hash_table:
                candidates.extend(hash_table[block_hash])

            signature = BlockDeltaCompressor.compute_block_signature(block)
            sig_matches = signature_table[signature]
            candidates.extend([idx for idx in sig_matches if idx not in candidates])

            recent_indices = range(max(0, i - 10), i)
            candidates.extend([idx for idx in recent_indices if idx not in candidates])

            best_match = None
            best_match_idx = -1
            lowest_diff_count = float('inf')

            for ref_idx in candidates:
                if ref_idx not in reference_blocks:
                    continue

                ref_block = reference_blocks[ref_idx]
                if abs(len(ref_block) - len(block)) > MAX_DELTA_PERCENTAGE * len(block) // 100:
                    continue

                diff_count = 0
                min_len = min(len(block), len(ref_block))
                for j in range(min_len):
                    if block[j] != ref_block[j]:
                        diff_count += 1
                diff_count += abs(len(block) - len(ref_block))

                if diff_count < lowest_diff_count:
                    lowest_diff_count = diff_count
                    best_match = ref_block
                    best_match_idx = ref_idx

            if best_match is None:
                for ref_idx, ref_block in reference_blocks.items():
                    diff_count = 0
                    min_len = min(len(block), len(ref_block))
                    for j in range(min_len):
                        if block[j] != ref_block[j]:
                            diff_count += 1
                    diff_count += abs(len(block) - len(ref_block))

                    if diff_count < lowest_diff_count:
                        lowest_diff_count = diff_count
                        best_match = ref_block
                        best_match_idx = ref_idx

            diff_percentage = (lowest_diff_count * 100) / len(block) if len(block) > 0 else 100

            if best_match is not None and diff_percentage <= MAX_DELTA_PERCENTAGE:
                delta_positions = []
                delta_values = []
                min_len = min(len(block), len(best_match))

                for j in range(min_len):
                    if block[j] != best_match[j]:
                        delta_positions.append(j)
                        delta_values.append(block[j])

                if len(block) > len(best_match):
                    for j in range(len(best_match), len(block)):
                        delta_positions.append(j)
                        delta_values.append(block[j])

                block_metadata.append((1, best_match_idx, len(delta_positions)))

                # Wire format: all positions, then all values (must match decompress)
                for pos in delta_positions:
                    raw_delta_data.extend(struct.pack(">H", pos))
                for val in delta_values:
                    raw_delta_data.append(val)

                reference_blocks[i] = block
                block_hash = BlockDeltaCompressor.hash_block(block)
                hash_table[block_hash].append(i)
                signature = BlockDeltaCompressor.compute_block_signature(block)
                signature_table[signature].append(i)
            else:
                block_metadata.append((0, len(block)))
                raw_delta_data.extend(block)

                block_hash = BlockDeltaCompressor.hash_block(block)
                hash_table[block_hash].append(i)
                signature = BlockDeltaCompressor.compute_block_signature(block)
                signature_table[signature].append(i)
                reference_blocks[i] = block

        freq_table = EntropyEncoder.build_frequency_table(raw_delta_data)
        huffman_tree = EntropyEncoder.build_huffman_tree(freq_table)
        encoding_table = EntropyEncoder.build_encoding_table(huffman_tree)
        encoded_delta, padding = EntropyEncoder.encode(raw_delta_data, encoding_table)
        serialized_tree = EntropyEncoder.serialize_huffman_tree(huffman_tree)

        output.extend(struct.pack(">I", len(block_metadata)))

        for metadata in block_metadata:
            if metadata[0] == 0:
                block_type, block_len = metadata
                output.append(block_type)
                output.extend(struct.pack(">H", block_len))
            else:
                block_type, ref_idx, delta_count = metadata
                output.append(block_type)
                output.extend(struct.pack(">H", ref_idx))
                output.extend(struct.pack(">H", delta_count))

        output.extend(struct.pack(">H", len(serialized_tree)))
        output.extend(serialized_tree)
        output.extend(struct.pack(">I", len(raw_delta_data)))
        output.append(padding)
        output.extend(struct.pack(">I", len(encoded_delta)))
        output.extend(encoded_delta)

        compression_time = time.time() - start_time
        original_size = len(input_data)
        compressed_size = len(output)
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
        space_savings = (1 - (compressed_size / original_size)) * 100 if original_size > 0 else 0

        print(f"Original size: {original_size:,} bytes")
        print(f"Compressed size: {compressed_size:,} bytes")
        print(f"Raw delta size: {len(raw_delta_data):,} bytes")
        print(f"Entropy coded size: {len(encoded_delta):,} bytes")
        print(f"Compression ratio: {compression_ratio:.2f}x")
        print(f"Space savings: {space_savings:.2f}%")
        print(f"Compression time: {compression_time:.4f} seconds")

        return bytes(output)

    @staticmethod
    def decompress(compressed_data):
        start_time = time.time()

        if len(compressed_data) < 11 or compressed_data[:4] != MAGIC_BYTES:
            raise ValueError("Invalid BlockDelta compressed data")

        version = compressed_data[4]
        block_size = struct.unpack(">H", compressed_data[5:7])[0]
        original_size = struct.unpack(">I", compressed_data[7:11])[0]

        if version != VERSION:
            raise ValueError(f"Unsupported version: {version}, expected {VERSION}")

        pos = 11
        num_blocks = struct.unpack(">I", compressed_data[pos:pos+4])[0]
        pos += 4

        block_metadata = []
        for _ in range(num_blocks):
            block_type = compressed_data[pos]
            pos += 1

            if block_type == 0:
                block_len = struct.unpack(">H", compressed_data[pos:pos+2])[0]
                pos += 2
                block_metadata.append((0, block_len))
            else:
                ref_idx = struct.unpack(">H", compressed_data[pos:pos+2])[0]
                pos += 2
                delta_count = struct.unpack(">H", compressed_data[pos:pos+2])[0]
                pos += 2
                block_metadata.append((1, ref_idx, delta_count))

        tree_size = struct.unpack(">H", compressed_data[pos:pos+2])[0]
        pos += 2
        serialized_tree = compressed_data[pos:pos+tree_size]
        pos += tree_size

        huffman_tree, _ = EntropyEncoder.deserialize_huffman_tree(serialized_tree)

        original_delta_size = struct.unpack(">I", compressed_data[pos:pos+4])[0]
        pos += 4
        padding = compressed_data[pos]
        pos += 1
        encoded_size = struct.unpack(">I", compressed_data[pos:pos+4])[0]
        pos += 4
        encoded_delta = compressed_data[pos:pos+encoded_size]

        raw_delta_data = EntropyEncoder.decode(
            encoded_delta, huffman_tree, padding, original_delta_size
        )

        output = bytearray()
        reference_blocks = {}
        delta_pos = 0

        for i, metadata in enumerate(block_metadata):
            if metadata[0] == 0:
                _, block_len = metadata
                block_data = raw_delta_data[delta_pos:delta_pos+block_len]
                delta_pos += block_len
                reference_blocks[i] = block_data
                output.extend(block_data)
            else:
                _, ref_idx, delta_count = metadata

                if ref_idx not in reference_blocks:
                    raise ValueError(
                        f"Invalid reference block index: {ref_idx} "
                        f"(available keys: {sorted(reference_blocks.keys())})"
                    )

                ref_block = reference_blocks[ref_idx]
                block_data = bytearray(ref_block)
                expected_len = min(block_size, original_size - len(output))

                # Wire format matches compress: all positions, then all values
                positions = []
                for _ in range(delta_count):
                    positions.append(
                        struct.unpack(">H", raw_delta_data[delta_pos:delta_pos+2])[0]
                    )
                    delta_pos += 2

                values = raw_delta_data[delta_pos:delta_pos + delta_count]
                delta_pos += delta_count

                for delta_position, delta_value in zip(positions, values):
                    if delta_position >= len(block_data):
                        block_data.extend(bytes(delta_position - len(block_data) + 1))
                    block_data[delta_position] = delta_value

                block_data = block_data[:expected_len]
                if len(block_data) < expected_len:
                    block_data.extend(bytes(expected_len - len(block_data)))

                reference_blocks[i] = bytes(block_data)
                output.extend(block_data)

        output = output[:original_size]
        print(f"Decompression time: {time.time() - start_time:.4f} seconds")
        return bytes(output)

    @staticmethod
    def compress_file(input_path, output_path=None):
        input_path = Path(input_path)
        if not output_path:
            output_path = str(input_path) + '.bkdt'

        with open(input_path, 'rb') as f:
            data = f.read()

        compressed_data = BlockDeltaCompressor.compress(data)

        with open(output_path, 'wb') as f:
            f.write(compressed_data)

        print(f"File compressed: {input_path} -> {output_path}")
        return len(data) / len(compressed_data) if len(compressed_data) > 0 else 0

    @staticmethod
    def decompress_file(input_path, output_path=None):
        input_path = Path(input_path)
        if not output_path:
            if str(input_path).endswith('.bkdt'):
                output_path = str(input_path)[:-5]
            else:
                output_path = str(input_path) + '.decompressed'

        with open(input_path, 'rb') as f:
            compressed_data = f.read()

        decompressed_data = BlockDeltaCompressor.decompress(compressed_data)

        with open(output_path, 'wb') as f:
            f.write(decompressed_data)

        print(f"File decompressed: {input_path} -> {output_path}")
        return 0.0


def main():
    parser = argparse.ArgumentParser(description="BlockDelta Compression Tool")
    parser.add_argument('action', choices=['compress', 'decompress'])
    parser.add_argument('input_file')
    parser.add_argument('-o', '--output')

    args = parser.parse_args()

    if args.action == 'compress':
        BlockDeltaCompressor.compress_file(args.input_file, args.output)
    else:
        BlockDeltaCompressor.decompress_file(args.input_file, args.output)


if __name__ == "__main__":
    main()
