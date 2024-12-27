import os
from tkinter import Tk, Label, Entry, Button, Text, filedialog, messagebox
from encoder import encode_message
from decoder import decode_message


def browse_file(entry):
    """Open a file dialog and set the selected file path to the entry field."""
    file_path = filedialog.askopenfilename(
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("All files", "*.*"),
        ]
    )
    if file_path:  # Ensure the user selected a file
        entry.delete(0, "end")
        entry.insert(0, file_path)


def encode_action():
    """Handle the encode button click event."""
    input_path = input_entry.get()
    message = message_entry.get("1.0", "end").strip()
    key = key_entry.get().strip()

    if not input_path or not os.path.exists(input_path):
        messagebox.showerror("Error", "Image not found. Please select a valid image.")
        return
    if not message:
        messagebox.showerror("Error", "Message cannot be empty.")
        return
    if not key:
        messagebox.showerror("Error", "Key cannot be empty.")
        return

    output_path = os.path.splitext(input_path)[0] + "_encoded.png"
    if encode_message(input_path, message, output_path, key):
        messagebox.showinfo(
            "Success", f"Message encoded successfully!\nSaved as: {output_path}"
        )
    else:
        messagebox.showerror("Error", "Failed to encode the message.")


def decode_action():
    """Handle the decode button click event."""
    input_path = input_entry.get()
    key = key_entry.get().strip()

    if not input_path or not os.path.exists(input_path):
        messagebox.showerror("Error", "Image not found. Please select a valid image.")
        return
    if not key:
        messagebox.showerror("Error", "Key cannot be empty.")
        return

    message = decode_message(input_path, key)
    if message:
        messagebox.showinfo("Decoded Message", message)
    else:
        messagebox.showerror("Error", "Failed to decode the message.")


# Initialize GUI application
app = Tk()
app.title("Steganography Tool")

# Input file path
Label(app, text="Image Path:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
input_entry = Entry(app, width=50)
input_entry.grid(row=0, column=1, padx=10, pady=10)
Button(app, text="Browse", command=lambda: browse_file(input_entry)).grid(
    row=0, column=2, padx=10, pady=10
)

# Input key
Label(app, text="Key:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
key_entry = Entry(app, width=50)
key_entry.grid(row=1, column=1, padx=10, pady=10, columnspan=2)

# Message text box
Label(app, text="Message:").grid(row=2, column=0, padx=10, pady=10, sticky="ne")
message_entry = Text(app, width=50, height=10)
message_entry.grid(row=2, column=1, padx=10, pady=10, columnspan=2)

# Buttons for encoding and decoding
Button(app, text="Encode", command=encode_action, bg="lightblue").grid(
    row=3, column=1, pady=10, sticky="e"
)
Button(app, text="Decode", command=decode_action, bg="lightgreen").grid(
    row=3, column=2, pady=10, sticky="w"
)

# Start the GUI loop
app.mainloop()
