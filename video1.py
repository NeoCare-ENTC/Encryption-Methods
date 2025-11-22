import tenseal as ts
import numpy as np
from PIL import Image
import time
import os
import json
import cv2

VIDEO_PATH = "videos/test_short.mp4"  # Path to your input video
OUTPUT_DIR = "data"
DECRYPTED_VIDEO_PATH = "videos/decrypted_video.mp4"  # Path to save decrypted video

# --- Video Encryption Phase ---
print("Processing video for encryption...")

# Open the video file using OpenCV
cap = cv2.VideoCapture(VIDEO_PATH)

# Get video properties (frame width, height, and fps)
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Video FPS: {fps}")
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Create a TenSEAL context for homomorphic encryption
context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 60])
context.generate_galois_keys()
context.global_scale = 2**40

# Prepare a video writer to save the decrypted video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(DECRYPTED_VIDEO_PATH, fourcc, fps, (frame_width, frame_height))

# Create a directory to store the encrypted data
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Serialize the context and encrypted data
serialized_context = context.serialize(save_secret_key=True)

# Save the serialized context
with open(os.path.join(OUTPUT_DIR, "secret.pkl"), "wb") as f:
    f.write(serialized_context)
    
# Encrypt and save frames one by one to avoid memory issues
with open(os.path.join(OUTPUT_DIR, "encrypted_frames.jsonl"), "w") as f:
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        img_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_flat = img_array.flatten().tolist()
        encrypted_img_vector = ts.ckks_vector(context, img_flat)

        # Serialize, encode to hex for JSON compatibility, and write as a new line
        serialized_hex = encrypted_img_vector.serialize().hex()
        f.write(json.dumps({"frame": serialized_hex}) + "\n")

        if frame_count % 100 == 0:
            print(f"Encrypted and saved {frame_count} frames.")
        frame_count += 1

print("Video encryption complete. Context and encrypted data saved.")

# Release video capture
cap.release()
out.release()

# --- Video Decryption Phase ---
print("Loading context and encrypted frames...")

# Load the serialized context and encrypted frames
with open(os.path.join(OUTPUT_DIR, "secret.pkl"), "rb") as f:
    serialized_context = f.read()

# Recreate the context from the serialized data
context = ts.context_from(serialized_context)

# Decrypt frames and reconstruct the video
with open(os.path.join(OUTPUT_DIR, "encrypted_frames.jsonl"), "r") as f:
    decrypted_frame_count = 0
    for line in f:
        # Load the JSON object from the line
        encrypted_frame_hex = json.loads(line)["frame"]
        # Decode from hex to bytes and create the tenseal vector
        encrypted_frame = ts.ckks_vector_from(context, bytes.fromhex(encrypted_frame_hex))

        decrypted_vector = encrypted_frame.decrypt()

        decrypted_array = np.array(decrypted_vector).round().clip(0, 255).astype(np.uint8)
        decrypted_frame = decrypted_array.reshape(frame_height, frame_width, 3)

        # Write the decrypted frame directly to the output video file
        out.write(cv2.cvtColor(decrypted_frame, cv2.COLOR_RGB2BGR))

        if decrypted_frame_count % 100 == 0:
            print(f"Decrypted and saved {decrypted_frame_count} frames.")
        decrypted_frame_count += 1

print("Video decryption complete. Decrypted video saved to 'videos/decrypted_video.mp4'.")

# Release video writer
out.release()
