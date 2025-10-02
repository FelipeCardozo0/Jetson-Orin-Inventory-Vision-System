#!/usr/bin/env python3
"""
client.py - Raspberry Pi Client for YOLOv8 Video Streaming

This script captures video from an Arducam, runs YOLOv8 inference, and streams
the annotated frames to a central WebSocket server.

Usage:
    python client.py <server_url> <camera_id>
    
Example:
    python client.py ws://192.168.1.100:8000 cam1
"""

import cv2
import time
import base64
import argparse
import asyncio
import websockets
import json
import logging
from ultralytics import YOLO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoStreamClient:
    """Handles video capture, YOLOv8 inference, and WebSocket streaming."""
    
    def __init__(self, server_url, camera_id, model_path='best.pt', camera_index=0):
        """
        Initialize the video streaming client.
        
        Args:
            server_url (str): WebSocket server URL (e.g., 'ws://192.168.1.100:8000')
            camera_id (str): Unique camera identifier (e.g., 'cam1', 'cam2')
            model_path (str): Path to the YOLOv8 model file
            camera_index (int): Camera device index (0 for default camera)
        """
        self.server_url = server_url
        self.camera_id = camera_id
        self.model_path = model_path
        self.camera_index = camera_index
        
        # WebSocket connection
        self.websocket = None
        self.reconnect_delay = 5  # seconds
        
        # Load YOLOv8 model
        logger.info(f"Loading YOLOv8 model from {model_path}...")
        self.model = YOLO(model_path)
        logger.info("Model loaded successfully!")
        
        # Initialize camera
        logger.info(f"Initializing camera (index: {camera_index})...")
        self.cap = cv2.VideoCapture(camera_index)
        
        if not self.cap.isOpened():
            logger.error("Failed to open camera!")
            raise RuntimeError("Could not open camera")
        
        logger.info("Camera initialized successfully!")
    
    async def connect_to_server(self):
        """Establish WebSocket connection to the server with reconnection logic."""
        while True:
            try:
                # Construct the WebSocket URL with camera_id
                ws_url = f"{self.server_url}/ws/publish/{self.camera_id}"
                logger.info(f"Connecting to server at {ws_url}...")
                
                self.websocket = await websockets.connect(
                    ws_url,
                    ping_interval=20,
                    ping_timeout=10,
                    max_size=10 * 1024 * 1024  # 10MB max message size
                )
                
                logger.info(f"Connected to server as {self.camera_id}!")
                return
                
            except Exception as e:
                logger.error(f"Connection failed: {e}")
                logger.info(f"Retrying in {self.reconnect_delay} seconds...")
                await asyncio.sleep(self.reconnect_delay)
    
    async def capture_and_stream(self):
        """Main loop: capture frames, run inference, and stream to server."""
        frame_count = 0
        
        while True:
            try:
                # Ensure we're connected
                if self.websocket is None or self.websocket.closed:
                    await self.connect_to_server()
                
                # Capture frame from camera
                success, frame = self.cap.read()
                
                if not success:
                    logger.warning("Failed to capture frame from camera")
                    await asyncio.sleep(0.1)
                    continue
                
                # Run YOLOv8 inference on the frame
                results = self.model(frame, verbose=False)
                
                # Get annotated frame with detection boxes and labels
                annotated_frame = results[0].plot()
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                # Convert to base64 for transmission
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Create JSON message
                message = json.dumps({
                    'camera_id': self.camera_id,
                    'frame': frame_base64,
                    'timestamp': time.time()
                })
                
                # Send frame to server
                await self.websocket.send(message)
                
                frame_count += 1
                if frame_count % 30 == 0:  # Log every 30 frames
                    logger.info(f"Sent {frame_count} frames from {self.camera_id}")
                
                # Small delay to prevent overwhelming the server
                await asyncio.sleep(0.033)  # ~30 FPS
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed")
                self.websocket = None
                await asyncio.sleep(self.reconnect_delay)
                
            except Exception as e:
                logger.error(f"Error in capture loop: {e}")
                await asyncio.sleep(1)
    
    def cleanup(self):
        """Release resources."""
        logger.info("Cleaning up resources...")
        if self.cap is not None:
            self.cap.release()
        logger.info("Cleanup complete")


async def main():
    """Main entry point."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='YOLOv8 Video Streaming Client for Raspberry Pi'
    )
    parser.add_argument(
        'server_url',
        type=str,
        help='WebSocket server URL (e.g., ws://192.168.1.100:8000)'
    )
    parser.add_argument(
        'camera_id',
        type=str,
        help='Unique camera identifier (e.g., cam1, cam2, cam3, cam4)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='best.pt',
        help='Path to YOLOv8 model file (default: best.pt)'
    )
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera device index (default: 0)'
    )
    
    args = parser.parse_args()
    
    # Create and run the client
    client = VideoStreamClient(
        server_url=args.server_url,
        camera_id=args.camera_id,
        model_path=args.model,
        camera_index=args.camera
    )
    
    try:
        await client.capture_and_stream()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        client.cleanup()


if __name__ == '__main__':
    # Run the async main function
    asyncio.run(main())

