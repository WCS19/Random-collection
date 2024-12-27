import random
from PIL import Image


def encode_message(image_path, message, output_path, key):
    """
    Encodes a message into an image by modifying least significant bits of all RGB channels.
    The embedding order is randomized using a user set secret key.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        pixels = img.load()
        width, height = img.size

        binary_message = (
            "".join(format(ord(char), "08b") for char in message) + "1111111111111110"
        )

        # Calculate the number of pixels available
        total_pixels = width * height * 3 
        if len(binary_message) > total_pixels:
            raise ValueError("Message is too long to fit in the image.")

        # Generate a pseudo-random sequence based on user key
        random.seed(key) 
        embedding_order = list(range(total_pixels))
        random.shuffle(embedding_order)

        # Embed the binary message in the shuffled order
        data_index = 0
        for idx in embedding_order:
            if data_index < len(binary_message):
                # Calculate the pixel and channel position
                pixel_index = idx // 3
                channel_index = idx % 3
                x = pixel_index % width
                y = pixel_index // width

                r, g, b = pixels[x, y]
                if channel_index == 0:  
                    r = (r & ~1) | int(binary_message[data_index])
                elif channel_index == 1:  
                    g = (g & ~1) | int(binary_message[data_index])
                elif channel_index == 2:  
                    b = (b & ~1) | int(binary_message[data_index])
                pixels[x, y] = (r, g, b)

                data_index += 1

        img.save(output_path, "PNG")
        print(f"Message encoded successfully and saved as {output_path}")
        return True
    except Exception as e:
        print(f"Error encoding message: {e}")
        return False
