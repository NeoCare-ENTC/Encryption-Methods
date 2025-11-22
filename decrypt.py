import tenseal as ts
import numpy as np
from PIL import Image
import time
import os
import json

DATA_DIR = "data"

# --- Loading Phase ---
print("Loading context and encrypted vector from files...")

# Load the serialized context and vector
with open(os.path.join(DATA_DIR, "secret.pkl"), "rb") as f:
    serialized_context = f.read()

with open(os.path.join(DATA_DIR, "encrypted_image.pkl"), "rb") as f:
    serialized_vector = f.read()

# Load the original image shape
with open(os.path.join(DATA_DIR, "image_shape.json"), "r") as f:
    h, w, c = json.load(f)

# --- Decryption Phase ---
print("\nReconstructing context and decrypting vector...")
start_time = time.time()

# Recreate the context and the encrypted vector from the serialized data
context = ts.context_from(serialized_context)
encrypted_img_vector = ts.ckks_vector_from(context, serialized_vector)

# Decrypt the vector
decrypted_vector = encrypted_img_vector.decrypt()
print(f"Decryption took: {time.time() - start_time:.2f} seconds")

# --- Image Reconstruction ---
# Post-processing: round, clamp to [0, 255], and convert to uint8
decrypted_array = np.array(decrypted_vector).round().clip(0, 255).astype(np.uint8)
decrypted_img_reshaped = decrypted_array.reshape(h, w, c)

decrypted_image = Image.fromarray(decrypted_img_reshaped).convert('RGB')
decrypted_image.save("images/decrypted_from_file.jpg")
print("\nDecryption complete. Image saved to 'images/decrypted_from_file.jpg'")