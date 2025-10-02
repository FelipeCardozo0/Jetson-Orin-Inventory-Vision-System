#!/usr/bin/env python3
"""
main_with_logging.py - YOLOv8 Inventory Detection with SQLite Data Logging

This is an enhanced version of main.py that logs all inventory detections
to a SQLite database for monthly reporting and analysis.

The script performs real-time YOLOv8 object detection and logs each item's
count to the database for historical tracking.
"""

import cv2
import time
import yaml
import argparse
import logging
import sqlite3
from datetime import datetime
from collections import defaultdict, deque
from statistics import median
from ultralytics import YOLO
from notify import check_inventory_state, item_states

# --- Database Setup and Initialization ---

def init_database(db_path='inventory.db'):
    """
    Initialize the SQLite database and create the inventory_log table if it doesn't exist.
    
    Args:
        db_path (str): Path to the SQLite database file
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the inventory_log table with proper schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            item_name TEXT NOT NULL,
            item_count INTEGER NOT NULL
        )
    ''')
    
    # Create an index on timestamp for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON inventory_log(timestamp)
    ''')
    
    # Create an index on item_name for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_item_name 
        ON inventory_log(item_name)
    ''')
    
    conn.commit()
    logging.info(f"Database initialized at {db_path}")
    
    return conn


def log_inventory_to_database(conn, item_counts):
    """
    Log the current inventory counts to the database.
    
    Creates a new record for each item with its current count and timestamp.
    
    Args:
        conn (sqlite3.Connection): Database connection
        item_counts (dict): Dictionary mapping item names to their counts
    """
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Insert a record for each item
        for item_name, count in item_counts.items():
            cursor.execute('''
                INSERT INTO inventory_log (timestamp, item_name, item_count)
                VALUES (?, ?, ?)
            ''', (timestamp, item_name, count))
        
        conn.commit()
        logging.debug(f"Logged {len(item_counts)} items to database at {timestamp}")
        
    except sqlite3.Error as e:
        logging.error(f"Database error while logging inventory: {e}")
        conn.rollback()


# --- Configuration Loading ---

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


# --- Command-Line Arguments ---

parser = argparse.ArgumentParser(description="YOLOv8 Inventory Detection System with Data Logging")
parser.add_argument("--headless", action="store_true", help="Run in headless mode (no video display)")
parser.add_argument("--db", type=str, default="inventory.db", help="Path to SQLite database file")
args = parser.parse_args()

# --- Initialization ---

logging.info("=" * 70)
logging.info("YOLOv8 Inventory Detection System with Data Logging")
logging.info("=" * 70)

# Load configuration
config = load_config()

MODEL_PATH = config['model_path']
CAMERA_INDEX = config['camera_index']
DETECTION_INTERVAL = config['detection_interval_seconds']
THRESHOLDS = config['thresholds']
SMOOTHING_WINDOW = 5  # Number of frames to average for stability

# Initialize database
db_conn = init_database(args.db)

# Use a deque to store the last N counts for each detected item
detection_history = defaultdict(lambda: deque(maxlen=SMOOTHING_WINDOW))
stable_counts = {}

# Load the YOLOv8 model
logging.info(f"Loading YOLOv8 model from {MODEL_PATH}...")
model = YOLO(MODEL_PATH)
logging.info("Model loaded successfully!")

# Initialize Camera
logging.info(f"Initializing camera (index: {CAMERA_INDEX})...")
cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    logging.error("Failed to open camera!")
    exit()

logging.info("Camera initialized successfully!")
logging.info("Starting main detection loop...")
logging.info("=" * 70)

# --- Main Detection Loop ---

frame_count = 0

try:
    while True:
        # Camera reconnection logic (resilience)
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

        frame_count += 1

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

        # --- DATABASE LOGGING ---
        # Log the stable counts to the database
        log_inventory_to_database(db_conn, stable_counts)

        # Check for low stock notifications based on stable counts
        snapshot_filename = "low_inventory_snapshot.jpg"
        cv2.imwrite(snapshot_filename, frame)
        check_inventory_state(stable_counts, THRESHOLDS, snapshot_path=snapshot_filename)

        # Display current inventory status
        if frame_count % 10 == 0:  # Log every 10 frames to reduce clutter
            logging.info(f"Current inventory: {dict(stable_counts)}")

        # --- Headless Mode & Enhanced On-Screen Display ---
        if not args.headless:
            # Get annotated frame with detection boxes
            annotated_frame = results[0].plot()
            
            # Create a semi-transparent overlay for inventory status
            overlay = annotated_frame.copy()
            cv2.rectangle(overlay, (5, 5), (400, 25 + len(THRESHOLDS) * 25), (0, 0, 0), -1)
            alpha = 0.6
            annotated_frame = cv2.addWeighted(overlay, alpha, annotated_frame, 1 - alpha, 0)
            
            # Display inventory counts with status indicators
            y_pos = 30
            for item, count in stable_counts.items():
                state = item_states.get(item, 'OK')
                color = (0, 255, 0) if state == 'OK' else (0, 0, 255)  # Green for OK, Red for LOW
                text = f"{item}: {count}/{THRESHOLDS.get(item, 0)} [{state}]"
                cv2.putText(annotated_frame, text, (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                y_pos += 25

            # Display frame count and database status
            status_text = f"Frames: {frame_count} | DB: Connected"
            cv2.putText(annotated_frame, status_text, (10, annotated_frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            cv2.imshow("YOLOv8 Inventory Detection with Logging", annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                logging.info("User requested shutdown (pressed 'q')")
                break

        # Wait for the configured interval before next detection
        time.sleep(DETECTION_INTERVAL)

except KeyboardInterrupt:
    logging.info("Interrupted by user (Ctrl+C)")

finally:
    # Cleanup
    logging.info("=" * 70)
    logging.info("Shutting down system...")
    
    # Close database connection
    if db_conn:
        db_conn.close()
        logging.info("Database connection closed")
    
    # Release camera
    cap.release()
    logging.info("Camera released")
    
    # Close OpenCV windows
    cv2.destroyAllWindows()
    logging.info("Application shutdown complete")
    logging.info("=" * 70)

