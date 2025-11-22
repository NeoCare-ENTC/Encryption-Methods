import tenseal as ts
import numpy as np
from PIL import Image
import time
import os
import json

# Load the image and convert it to a numpy array
img = Image.open("images/test_1.png")
img_array = np.array(img)
h, w, c = img_array.shape

# Flatten the image array and convert to a list of floats for encryption
img_flat = img_array.flatten().tolist()
print(f"Image shape: {img_array.shape}, Flattened length: {len(img_flat)}")

# Create a TenSEAL context for homomorphic encryption
# Using the CKKS scheme for approximate arithmetic on real numbers
context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 60])
context.generate_galois_keys()
# Set the global scale for the context
context.global_scale = 2**40

print("Encrypting image...")
start_time = time.time()

# Encrypt the entire flattened image vector at once
encrypted_img_vector = ts.ckks_vector(context, img_flat)

print(f"Encryption took: {time.time() - start_time:.2f} seconds")

# Create a directory to store the encrypted data and context
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)

# Serialize the context (with the secret key) and the encrypted vector
serialized_context = context.serialize(save_secret_key=True)
serialized_vector = encrypted_img_vector.serialize()

# Save the serialized data and image shape to files
with open(os.path.join(output_dir, "secret.pkl"), "wb") as f:
    f.write(serialized_context)

with open(os.path.join(output_dir, "encrypted_image.pkl"), "wb") as f:
    f.write(serialized_vector)

with open(os.path.join(output_dir, "image_shape.json"), "w") as f:
    json.dump((h, w, c), f)

print(f"\nEncryption complete. Context and encrypted data saved in '{output_dir}/' directory.")
