# BlockDelta Compression Results

Test run after fixing the delta encode/decode mismatch (positions/values layout) and reference-block tracking.

## Synthetic patterns (`test_compression.py`)

| Pattern | Size | Compressed | Ratio | Savings | Lossless |
|---------|------|------------|-------|---------|----------|
| random  | 100 KB | 104,393 B | 0.98x | −1.95% | ✅ |
| repeat  | 100 KB | 52,003 B | 1.97x | 49.22% | ✅ |
| text    | 100 KB | 57,285 B | 1.79x | 44.06% | ✅ |
| zeroes  | 100 KB | 18,770 B | 5.46x | 81.67% | ✅ |

Compression time for these 100 KB cases was ~0.05–0.07 s; decompression ~0.008–0.04 s.

**Notes**
- Random data expands slightly (expected — little redundancy, format overhead).
- Text gains came mostly from Huffman on full blocks (`raw delta size` equaled the original).
- Repeat and zeroes used real block deltas and still round-tripped correctly.

## Image (`test_image_blockalgo.py`)

| File | Original | Compressed | Ratio | Savings | Lossless |
|------|----------|------------|-------|---------|----------|
| `steganography/palmtree.bmp` | 1,080,054 B | 285,865 B | 3.78x | 73.53% | ✅ |

- Compression time: ~41.2 s  
- Decompression time: ~0.12 s  
- Decompressed BMP was pixel-identical to the original

## Takeaways

BlockDelta is lossless on these inputs. It works best on data with similar repeating blocks (BMP, zeroes, repeats) and poorly on already-compressed or high-entropy data (PNG, random).
