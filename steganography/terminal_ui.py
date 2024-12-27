from encoder import encode_message
from decoder import decode_message
import getpass 


def main():
    print("Steganography Tool")
    print("1. Encode a message")
    print("2. Decode a message")
    choice = input("Choose an option (1/2): ").strip()

    if choice == "1":
        image_path = input("Enter the path to the input image: ").strip()
        message = input("Enter the message to hide: ").strip()
        key = getpass.getpass("Enter the key for encoding (hidden): ").strip()
        output_path = input(
            "Enter the path to save the encoded image (including filename.png): "
        ).strip()

        if not key:
            print("Error: Key cannot be empty!")
            return

        try:
            encode_message(image_path, message, output_path, key)
            print("Message encoded successfully!")
        except Exception as e:
            print(f"Error encoding message: {str(e)}")
            return
    elif choice == "2":
        image_path = input("Enter the path to the encoded image: ").strip()
        key = getpass.getpass("Enter the key for decoding (hidden): ").strip()

        if not key:
            print("Error: Key cannot be empty!")
            return

        try:
            message = decode_message(image_path, key)
            if message:
                print(f"Hidden Message: {message}")
            else:
                print("Failed to decode the message.")
        except Exception as e:
            print(f"Error decoding message: {str(e)}")
            return
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
