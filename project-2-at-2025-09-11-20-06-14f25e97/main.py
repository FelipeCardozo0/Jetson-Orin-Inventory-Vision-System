# main.py

import cv2
import time
import os
from ultralytics import YOLO
from notify import notify_if_below_threshold

# --- Configuration ---
# Load your custom-trained YOLOv8 model
model = YOLO('best.pt') 

# [cite_start]Define the inventory thresholds for notification [cite: 85]
thresholds = {
    "Black Cherry Cane Sugar": 1,
    "Cantaloupe": 1,
    "Coke Diet": 1,
    "Coke Zero": 1,
    "Cold Brew Matcha Green Tea": 1,
    "Essentia": 1,
    "Ginger Ale Canada": 1,
    "Grapes": 1,
    "Guava Green Tea": 1,
    "Iced Tea Cane Sugar": 1,
    "Island Passion Fruit": 1,
    "Ito Milk Tea": 1,
    "Jasmine Green Tea": 1,
    "Kilauea Lemon Cake": 1,
    "Limonade Cane Sugar": 1,
    "Little Jasmine White Peach Black Tea": 1,
    "Lychee Oolong Tea": 1,
    "Mango": 1,
    "Mango Oolong Tea": 1,
    "Maui Custard": 1,
    "Oi Ocha Unsweetened Green Tea": 1,
    "Orange Cane Sugar": 1,
    "Passionfruit Green Tea": 1,
    "Perrier": 1,
    "Philadelphia 6 roll": 1,
    "Pineapple": 1,
    "Pineapple Cane Sugar": 1,
    "Pineapple Green Tea": 1,
    "Root Bear Cane Sugar": 1,
    "San Pe Blood Orange": 1,
    "San Pe Lemonade": 1,
    "San Pe Orange": 1,
    "Sprite": 1,
    "Strawberry": 1,
    "Sunkist Orange": 1,
    "Teas' Tea Rose Green Tea": 1,
    "Traditional Golden Oolong Tea": 1,
    "Traditional Jasmine Green Tea": 1,
    "Vanilla Cream Cane Sugar": 1,
    "Watermelon": 1
}

# Initialize the camera (0 is usually the default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

print("Camera started. Press 'q' to quit.")

# --- Main Detection Loop ---
while True:
    # Capture frame-by-frame
    success, frame = cap.read()
    if not success:
        print("Error: Failed to capture frame.")
        break

    # Run YOLOv8 inference on the frame
    results = model(frame, verbose=False) # Set verbose=False to clean up terminal output

    # --- Process Detections ---
    counts = {} # [cite: 87]
    for r in results:
        for box in r.boxes:
            # Get the class name from the model's names list
            label = model.names[int(box.cls)]
            counts[label] = counts.get(label, 0) + 1 # [cite: 89]

    print(f"Current Counts: {counts}")

    # --- Check for Notifications ---
    snapshot_filename = "low_inventory_snapshot.jpg"
    cv2.imwrite(snapshot_filename, frame) # Save a snapshot for the email
    notify_if_below_threshold(counts, thresholds, snapshot_path=snapshot_filename) # [cite: 90]
    
    # --- Display the Live Feed (optional) ---
    # You can comment this section out if running "headless"
    annotated_frame = results[0].plot()
    cv2.imshow("YOLOv8 Inventory Detection", annotated_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
        
    # Wait for a set interval before processing the next frame
    time.sleep(5) # [cite: 90]


# Release the camera and close all OpenCV windows
print("Shutting down...")
cap.release()
cv2.destroyAllWindows()



# main.py

import cv2
import time
import yaml
import argparse
import logging
from collections import defaultdict, deque
from statistics import median
from ultralytics import YOLO
from notify import check_inventory_state, item_states

# --- 1. External Configuration File ---
def load_config(config_path='config.yaml'):
    """Loads configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Error: Configuration file not found at '{config_path}'")
        exit()
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        exit()

# --- 2. Command-Line Argument for Headless Mode ---
parser = argparse.ArgumentParser(description="YOLOv8 Inventory Detection System")
parser.add_argument("--headless", action="store_true", help="Run in headless mode (no video display)")
args = parser.parse_args()

# --- Initialization ---
logging.info("Application starting...")
config = load_config()

MODEL_PATH = config['model_path']
CAMERA_INDEX = config['camera_index']
DETECTION_INTERVAL = config['detection_interval_seconds']
THRESHOLDS = config['thresholds']
SMOOTHING_WINDOW = 5  # Number of frames to average for stability

# --- 3. Improved Detection Stability (Smoothing) ---
# Use a deque to store the last N counts for each detected item.
detection_history = defaultdict(lambda: deque(maxlen=SMOOTHING_WINDOW))
stable_counts = {}

# Load the YOLOv8 model
model = YOLO(MODEL_PATH)

# Initialize Camera
cap = cv2.VideoCapture(CAMERA_INDEX)

# --- Main Detection Loop ---
while True:
    # --- 4. Application Resilience (Camera Reconnection) ---
    if not cap.isOpened():
        logging.error("Camera disconnected. Attempting to reconnect every 10 seconds...")
        time.sleep(10)
        cap = cv2.VideoCapture(CAMERA_INDEX)
        continue

    success, frame = cap.read()
    if not success:
        logging.warning("Failed to capture frame. Retrying...")
        time.sleep(1)
        continue

    # Run YOLOv8 inference
    results = model(frame, verbose=False)

    # Process detections for the current frame
    current_frame_counts = defaultdict(int)
    for r in results:
        for box in r.boxes:
            label = model.names[int(box.cls)]
            current_frame_counts[label] += 1
    
    # Update detection history for all tracked items
    for item in THRESHOLDS.keys():
        detection_history[item].append(current_frame_counts.get(item, 0))

    # Calculate stable counts using the median of the history
    for item, history in detection_history.items():
        if history:
            stable_counts[item] = int(median(history))
        else:
            stable_counts[item] = 0

    # Check for notifications based on stable counts
    snapshot_filename = "low_inventory_snapshot.jpg"
    cv2.imwrite(snapshot_filename, frame)
    check_inventory_state(stable_counts, THRESHOLDS, snapshot_path=snapshot_filename)

    # --- 5. Headless Mode & Enhanced On-Screen Display ---
    if not args.headless:
        # Create a semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (5, 5), (350, 20 + len(THRESHOLDS) * 20), (0, 0, 0), -1)
        alpha = 0.6
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        y_pos = 25
        for item, count in stable_counts.items():
            state = item_states.get(item, 'OK')
            color = (0, 255, 0) if state == 'OK' else (0, 0, 255) # Green for OK, Red for LOW
            text = f"{item}: {count}/{THRESHOLDS.get(item, 0)} [{state}]"
            cv2.putText(frame, text, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            y_pos += 20

        cv2.imshow("YOLOv8 Inventory Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    time.sleep(DETECTION_INTERVAL)

# Cleanup
logging.info("Application shutting down...")
cap.release()
cv2.destroyAllWindows()