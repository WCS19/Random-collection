from PIL import Image
import sys
from pathlib import Path


def convert_to_bmp(input_image_path, output_bmp_path=None):
    """Convert an image to uncompressed BMP for compression testing."""
    input_path = Path(input_image_path)
    if output_bmp_path is None:
        output_bmp_path = input_path.with_suffix('.bmp')

    img = Image.open(input_path)
    img.save(output_bmp_path, format='BMP')
    print(f"Converted {input_path} to BMP: {output_bmp_path}")
    return output_bmp_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_to_bmp.py <image_path> [output_path]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    convert_to_bmp(input_path, output_path)
