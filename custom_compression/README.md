# BlockDelta Compression

Exploratory lossless compressor: split data into fixed-size blocks, store similar blocks as deltas against earlier references, then Huffman-code the payload.

Works best on data with repeating or near-duplicate blocks (uncompressed images, sparse/zero-heavy data, patterned binaries). Already-compressed formats (PNG, JPEG, gzip) and pure random data usually do not shrink — and may grow slightly from format overhead.

## How It Works

1. **Block segmentation** — default 256-byte blocks
2. **Reference lookup** — FNV-1a hash, coarse block signatures, and recent-block locality
3. **Delta or full store** — if ≤ `MAX_DELTA_PERCENTAGE` bytes differ from a reference, store only the differences; otherwise store the full block
4. **Huffman coding** — entropy-code the combined delta/literal payload

Every reconstructed block is kept as a reference so compress and decompress stay in sync.

## Format

- Header: `BKDT` magic, version, block size, original size
- Per-block metadata (type 0 = full, type 1 = delta + reference index)
- Serialized Huffman tree
- Entropy-coded payload

Delta wire format: all changed positions (uint16 BE), then all new values.

## Usage

```bash
cd custom_compression
python block_delta.py compress <input_file> [-o <output_file>]
python block_delta.py decompress <compressed_file> [-o <output_file>]
```

```python
from block_delta import BlockDeltaCompressor

BlockDeltaCompressor.compress_file("myfile.txt", "myfile.bkdt")
BlockDeltaCompressor.decompress_file("myfile.bkdt", "myfile_restored.txt")
```

## Testing

```bash
python test_compression.py          # random / repeat / text / zeroes
python verify_lossless.py           # predictable patterns
python test_image_blockalgo.py path/to/image.bmp
```

Test fixtures under `test_data/` and `verification_data/` are generated on the fly (not committed).

Measured ratios from a recent run are in [RESULTS.md](RESULTS.md).

## Tunables

In `block_delta.py`:

- `BLOCK_SIZE` (default 256)
- `MAX_DELTA_PERCENTAGE` (default 50)
- `HASH_SEED` / `HASH_PRIME` (FNV-1a)
