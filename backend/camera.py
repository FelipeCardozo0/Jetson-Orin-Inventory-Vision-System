"""
USB Camera Handler for Jetson Orin Nano
Handles camera initialization, frame capture, reconnection logic,
and runtime camera switching between multiple sources.
"""

import cv2
import logging
import platform
import time
from typing import Optional, Tuple, List, Dict
import numpy as np

logger = logging.getLogger(__name__)


class USBCamera:
    """
    Robust USB camera handler with automatic reconnection
    Supports UVC-compliant cameras
    """
    
    def __init__(self, camera_index: int = 0, width: int = 1280, height: int = 720, fps: int = 30):
        """
        Initialize USB camera handler
        
        Args:
            camera_index: V4L2 device index (default: 0 for /dev/video0)
            width: Frame width in pixels
            height: Frame height in pixels
            fps: Target frames per second
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened = False
        self.frame_count = 0
        self.last_frame: Optional[np.ndarray] = None
        
    def open(self) -> bool:
        """
        Open camera connection with optimal settings for Jetson
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use V4L2 backend for Linux/Jetson
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera at index {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Set MJPEG format for better USB bandwidth utilization
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            
            # Set buffer size to 1 to minimize latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Verify actual settings
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            
            logger.info(f"Camera opened: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            self.is_opened = True
            self.frame_count = 0
            return True
            
        except Exception as e:
            logger.error(f"Exception opening camera: {e}")
            return False
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the camera
        
        Returns:
            Tuple of (success, frame)
            - success: True if frame was read successfully
            - frame: numpy array of shape (H, W, 3) in BGR format, or None
        """
        if not self.is_opened or self.cap is None:
            return False, None
        
        try:
            ret, frame = self.cap.read()
            
            if ret and frame is not None:
                self.frame_count += 1
                self.last_frame = frame.copy()
                return True, frame
            else:
                logger.warning(f"Failed to read frame (count: {self.frame_count})")
                return False, None
                
        except Exception as e:
            logger.error(f"Exception reading frame: {e}")
            return False, None
    
    def get_last_frame(self) -> Optional[np.ndarray]:
        """
        Return the last successfully captured frame
        Useful for displaying stale frame during reconnection
        """
        return self.last_frame
    
    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_opened = False
        logger.info("Camera released")
    
    def reconnect(self, max_attempts: int = 5, retry_delay: float = 2.0) -> bool:
        """
        Attempt to reconnect to camera
        
        Args:
            max_attempts: Maximum number of reconnection attempts
            retry_delay: Delay between attempts in seconds
            
        Returns:
            True if reconnection successful
        """
        logger.warning("Attempting camera reconnection...")
        self.release()
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Reconnection attempt {attempt}/{max_attempts}")
            time.sleep(retry_delay)
            
            if self.open():
                logger.info("Camera reconnected successfully")
                return True
        
        logger.error("Camera reconnection failed")
        return False
    
    def is_healthy(self) -> bool:
        """
        Check if camera is healthy and responsive
        
        Returns:
            True if camera is working properly
        """
        if not self.is_opened or self.cap is None:
            return False
        
        # Try to grab a frame without decoding
        return self.cap.grab()
    
    def get_info(self) -> dict:
        """
        Get camera information and current settings
        
        Returns:
            Dictionary with camera properties
        """
        if not self.is_opened or self.cap is None:
            return {
                "status": "closed",
                "camera_index": self.camera_index
            }
        
        return {
            "status": "open",
            "camera_index": self.camera_index,
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": int(self.cap.get(cv2.CAP_PROP_FPS)),
            "frames_captured": self.frame_count,
            "backend": self.cap.getBackendName()
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
    
    # ------------------------------------------------------------------
    # Camera enumeration & runtime switching
    # ------------------------------------------------------------------

    @staticmethod
    def enumerate_cameras(max_index: int = 10) -> List[Dict]:
        """
        Probe video device indices and return a list of available cameras.

        Each entry contains:
            - index: int  (V4L2 device index)
            - name:  str  (human-readable label)
            - backend: str

        Args:
            max_index: Highest device index to probe (exclusive).

        Returns:
            List of camera info dicts, sorted by index.
        """
        cameras: List[Dict] = []
        is_linux = platform.system() == "Linux"

        for idx in range(max_index):
            try:
                cap = cv2.VideoCapture(idx, cv2.CAP_V4L2 if is_linux else cv2.CAP_ANY)
                if cap.isOpened():
                    backend = cap.getBackendName() if hasattr(cap, "getBackendName") else "unknown"
                    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    name = f"Camera {idx} ({backend} {w}x{h})"

                    # On Linux, try to read /sys for a friendlier name
                    if is_linux:
                        try:
                            with open(f"/sys/class/video4linux/video{idx}/name") as f:
                                hw_name = f.read().strip()
                            if hw_name:
                                name = f"{hw_name} (index {idx})"
                        except Exception:
                            pass

                    cameras.append({
                        "index": idx,
                        "name": name,
                        "backend": backend,
                    })
                    cap.release()
            except Exception:
                continue

        logger.info(f"Enumerated {len(cameras)} camera(s): {[c['name'] for c in cameras]}")
        return cameras

    def switch_camera(self, new_index: int) -> bool:
        """
        Safely release the current camera and re-initialise on *new_index*.

        Thread-safe: uses the internal lock so the streaming loop won't
        read half-initialised state.

        Args:
            new_index: V4L2 device index to switch to.

        Returns:
            True if the new camera opened successfully, False otherwise
            (in which case the old camera is also closed).
        """
        logger.info(f"Switching camera from index {self.camera_index} → {new_index}")

        # Release current device
        self.release()

        # Update index and re-open
        self.camera_index = new_index
        success = self.open()

        if success:
            logger.info(f"Camera switched successfully to index {new_index}")
        else:
            logger.error(f"Failed to switch to camera index {new_index}")

        return success

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.release()

