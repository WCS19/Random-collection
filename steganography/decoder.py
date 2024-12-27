from PIL import Image
import random


def decode_message(image_path, key):
    """
    Decodes and retrieves a hidden message from an image using all RGB channels.
    The decoding order is determined by user set secret key.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        pixels = img.load()
        width, height = img.size

        # Calculate the total number of available bits
        total_pixels = width * height * 3

        # Generate the pseudo-random sequence based on user set key
        random.seed(key)
        embedding_order = list(range(total_pixels))
        random.shuffle(embedding_order)

        # Extract the LSBs in the order defined by the embedding sequence
        binary_message = ""
        for idx in embedding_order:
            pixel_index = idx // 3
            channel_index = idx % 3
            x = pixel_index % width
            y = pixel_index // width

            r, g, b = pixels[x, y]
            if channel_index == 0:  
                binary_message += str(r & 1)
            elif channel_index == 1:  
                binary_message += str(g & 1)
            elif channel_index == 2:  
                binary_message += str(b & 1)

            # Check for delimiter to stop early
            if len(binary_message) >= 16 and binary_message.endswith(
                "1111111111111110"
            ):
                binary_message = binary_message[:-16]  # Remove delimiter
                break

        # Convert binary to text
        message = "".join(
            chr(int(binary_message[i : i + 8], 2))
            for i in range(0, len(binary_message), 8)
        )
        return message
    except Exception as e:
        print(f"Error decoding message: {e}")
        return None
