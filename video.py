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

frame_count = 0
encrypted_frames = []

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to RGB (OpenCV uses BGR)
    img_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Flatten the image array for encryption
    img_flat = img_array.flatten().tolist()

    # Encrypt the flattened image vector
    encrypted_img_vector = ts.ckks_vector(context, img_flat)

    encrypted_frames.append(encrypted_img_vector)

    # Save progress every 100 frames
    if frame_count % 100 == 0:
        print(f"Encrypted {frame_count} frames.")

    frame_count += 1

# Serialize the context and encrypted data
serialized_context = context.serialize(save_secret_key=True)

# Save the serialized context
with open(os.path.join(OUTPUT_DIR, "secret.pkl"), "wb") as f:
    f.write(serialized_context)

# Save the encrypted video frames
with open(os.path.join(OUTPUT_DIR, "encrypted_frames.pkl"), "wb") as f:
    f.write(json.dumps([frame.serialize() for frame in encrypted_frames]).encode('utf-8'))  # Serialize each frame and encode to bytes

print("Video encryption complete. Context and encrypted data saved.")

# Release video capture
cap.release()
out.release()

# --- Video Decryption Phase ---
print("Loading context and encrypted frames...")

# Load the serialized context and encrypted frames
with open(os.path.join(OUTPUT_DIR, "secret.pkl"), "rb") as f:
    serialized_context = f.read()

with open(os.path.join(OUTPUT_DIR, "encrypted_frames.pkl"), "rb") as f:
    encrypted_frames = json.loads(f.read())

# Recreate the context from the serialized data
context = ts.context_from(serialized_context)

# Decrypt frames and reconstruct the video
decrypted_frame_count = 0
decrypted_video_frames = []

for encrypted_frame_str in encrypted_frames:
    encrypted_frame = ts.ckks_vector_from(context, encrypted_frame_str.encode('utf-8'))

    # Decrypt the frame
    decrypted_vector = encrypted_frame.decrypt()

    # Post-process: round, clamp to [0, 255], and convert to uint8
    decrypted_array = np.array(decrypted_vector).round().clip(0, 255).astype(np.uint8)

    # Reshape the decrypted vector back to the original frame shape (height, width, channels)
    decrypted_frame = decrypted_array.reshape(frame_height, frame_width, 3)  # RGB format
    decrypted_video_frames.append(decrypted_frame)

    # Save progress every 100 frames
    if decrypted_frame_count % 100 == 0:
        print(f"Decrypted {decrypted_frame_count} frames.")

    decrypted_frame_count += 1

# Reconstruct the decrypted video and save it
for frame in decrypted_video_frames:
    out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))  # Convert back to BGR for OpenCV

print("Video decryption complete. Decrypted video saved to 'videos/decrypted_video.mp4'.")

# Release video writer
out.release()
