
import os
import time
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad


def encrypt_video(key):
    # Specify your input video path
    input_path = r"videos/test4.avi"
    base = os.path.splitext(os.path.basename(input_path))[0]
    output_dir = "encrypted files"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{base}_encrypted.enc")
    start_time = time.time()
    # Read video as binary
    with open(input_path, 'rb') as f:
        data = f.read()
    # Pad data to AES block size
    padded_data = pad(data, AES.block_size)
    # Generate random IV
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(padded_data)
    # Write IV + encrypted data to output
    with open(output_path, 'wb') as f:
        f.write(iv + encrypted)
    end_time = time.time()
    return end_time - start_time

if __name__ == "__main__":
    key = get_random_bytes(16)  # 128-bit key
    elapsed = encrypt_video(key)
    print(f"Encryption complete in {elapsed:.2f} seconds. Save this key to decrypt: {key.hex()}")