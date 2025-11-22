import os
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def decrypt_video(key_hex):
    input_dir = "encrypted files"
    input_file = "test4_encrypted.enc"  # Change if your file name is different
    input_path = os.path.join(input_dir, input_file)
    output_dir = "decrypted files"
    os.makedirs(output_dir, exist_ok=True)
    base, ext = os.path.splitext(os.path.basename(input_file))
    output_path = os.path.join(output_dir, f"{base.replace('_encrypted','')}_decrypted.mp4")

    key = bytes.fromhex(key_hex)
    start_time = time.time()
    with open(input_path, 'rb') as f:
        iv = f.read(16)
        encrypted_data = f.read()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = cipher.decrypt(encrypted_data)
    data = unpad(padded_data, AES.block_size)
    with open(output_path, 'wb') as f:
        f.write(data)
    end_time = time.time()
    print(f"Decryption complete in {end_time - start_time:.2f} seconds. Output saved to {output_path}")

if __name__ == "__main__":
    key_hex = input("Enter the 32-character hex key used for encryption: ")
    decrypt_video(key_hex)
