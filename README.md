# Homomorphic Image Encryption Tool

This project provides a command-line tool that uses the `tenseal` library to perform true cryptographic encryption on an image's pixel data. The encrypted data can be saved to a file and decrypted later in a separate process.

## Features

- **Homomorphic Encryption**: Utilizes the CKKS scheme from Microsoft SEAL (via `tenseal`) to encrypt image data.
- **Secure Data Persistence**: Demonstrates how to save the encrypted data and the secret context to files for later decryption.

## Requirements

The project requires the following Python libraries:

- `tenseal`: For homomorphic encryption.
- `numpy`: For numerical operations on image data.

## Installation

1.  Clone the repository or download the source files.

2.  Install the required packages using pip:
    ```bash
    pip install tenseal numpy
    ```

## Usage

This tool consists of two scripts: `encrypt.py` for encryption and `decrypt.py` for decryption.

### Step 1: Encrypt an Image

Place an image you want to encrypt inside the `images/` directory (e.g., `images/test_1.png`). Then, run the encryption script:

```bash
python encrypt.py
```

This will:
- Load `images/test_1.png`.
- Encrypt its pixel data using a homomorphic encryption context.
- Save the following files into the `data/` directory:
  - `secret.pkl`: The serialized context containing the secret key needed for decryption. **Keep this file safe!**
  - `encrypted_image.pkl`: The serialized encrypted image vector.
  - `image_shape.json`: The original dimensions of the image, required for reconstruction.

### Step 2: Decrypt the Image

To decrypt the data and reconstruct the image, run the decryption script:

```bash
python decrypt.py
```

This script will:
- Load the context, encrypted data, and shape information from the `data/` directory.
- Decrypt the data.
- Reconstruct the image and save it as `images/decrypted_from_file.jpg`.