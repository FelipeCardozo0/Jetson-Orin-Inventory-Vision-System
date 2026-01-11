#!/usr/bin/env python3
"""
Poke Bowl Inventory System - Main Entry Point
Production-ready computer vision system for Jetson Orin Nano
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from typing import Optional

import yaml

# Import local modules
from camera import USBCamera
from detector import YOLODetector
from inventory import InventoryTracker
from inventory_persistent import PersistentInventoryTracker
from server import VideoStreamServer, StreamManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/pokebowl_inventory.log')
    ]
)

logger = logging.getLogger(__name__)


class InventorySystem:
    """
    Main application class
    Coordinates all components and manages lifecycle
    """
    
    def __init__(self, config_path: Path):
        """
        Initialize inventory system
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path
        self.config = self.load_config()
        
        # Components
        self.camera: Optional[USBCamera] = None
        self.detector: Optional[YOLODetector] = None
        self.inventory_tracker: Optional[InventoryTracker] = None
        self.server: Optional[VideoStreamServer] = None
        self.stream_manager: Optional[StreamManager] = None
        
        # Shutdown flag
        self.shutdown_event = asyncio.Event()
        
    def load_config(self) -> dict:
        """
        Load configuration from YAML file
        
        Returns:
            Configuration dictionary
        """
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            logger.info("Using default configuration")
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        """
        Get default configuration
        
        Returns:
            Default configuration dictionary
        """
        return {
            'camera': {
                'index': 0,
                'width': 1280,
                'height': 720,
                'fps': 30
            },
            'detector': {
                'model_path': 'best.pt',
                'conf_threshold': 0.25,
                'iou_threshold': 0.45,
                'imgsz': 640,
                'device': '0',
                'half': True
            },
            'inventory': {
                'smoothing_window': 10,
                'smoothing_method': 'median',
                'enable_persistence': True,
                'snapshot_interval': 5.0,
                'expiration_days': 5,
                'sales_confirm_intervals': 2,
                'sales_min_delta': 1,
                'sales_cooldown_seconds': 10.0
            },
            'alerts': {
                'enable_alerts': True,
                'alert_confirm_intervals': 2,
                'alert_cooldown_seconds': 3600.0,
                'low_stock_thresholds': {
                    'mango': 3,
                    'watermelon': 2,
                    'pineapple': 2,
                    'passion fruit': 2,
                    'maui custard': 2,
                    'lemon cake': 2
                }
            },
            'server': {
                'host': '0.0.0.0',
                'port': 8080
            },
            'stream': {
                'target_fps': 30
            }
        }
    
    def initialize_components(self) -> bool:
        """
        Initialize all system components
        
        Returns:
            True if all components initialized successfully
        """
        try:
            # Initialize camera
            logger.info("Initializing camera...")
            camera_config = self.config.get('camera', {})
            self.camera = USBCamera(
                camera_index=camera_config.get('index', 0),
                width=camera_config.get('width', 1280),
                height=camera_config.get('height', 720),
                fps=camera_config.get('fps', 30)
            )
            
            if not self.camera.open():
                logger.error("Failed to open camera")
                return False
            
            logger.info(f"Camera initialized: {self.camera.get_info()}")
            
            # Initialize detector
            logger.info("Initializing YOLO detector...")
            detector_config = self.config.get('detector', {})
            
            # Resolve model path relative to project root
            model_path = Path(detector_config.get('model_path', 'best.pt'))
            if not model_path.is_absolute():
                project_root = Path(__file__).parent.parent
                model_path = project_root / model_path
            
            self.detector = YOLODetector(
                model_path=str(model_path),
                conf_threshold=detector_config.get('conf_threshold', 0.25),
                iou_threshold=detector_config.get('iou_threshold', 0.45),
                imgsz=detector_config.get('imgsz', 640),
                device=detector_config.get('device', '0'),
                half=detector_config.get('half', True)
            )
            
            if not self.detector.load():
                logger.error("Failed to load YOLO model")
                return False
            
            # Warmup detector
            self.detector.warmup(num_iterations=5)
            
            logger.info(f"Detector initialized: {self.detector.get_info()}")
            
            # Initialize inventory tracker with persistence
            logger.info("Initializing inventory tracker...")
            inventory_config = self.config.get('inventory', {})
            
            # Use persistent tracker if enabled, otherwise use base tracker
            enable_persistence = inventory_config.get('enable_persistence', True)
            
            if enable_persistence:
                # Get alert configuration
                alerts_config = self.config.get('alerts', {})
                
                self.inventory_tracker = PersistentInventoryTracker(
                    smoothing_window=inventory_config.get('smoothing_window', 10),
                    smoothing_method=inventory_config.get('smoothing_method', 'median'),
                    class_names=self.detector.class_names,
                    snapshot_interval=inventory_config.get('snapshot_interval', 5.0),
                    expiration_days=inventory_config.get('expiration_days', 5),
                    enable_persistence=True,
                    sales_confirm_intervals=inventory_config.get('sales_confirm_intervals', 2),
                    sales_min_delta=inventory_config.get('sales_min_delta', 1),
                    sales_cooldown_seconds=inventory_config.get('sales_cooldown_seconds', 10.0),
                    enable_alerts=alerts_config.get('enable_alerts', True),
                    low_stock_thresholds=alerts_config.get('low_stock_thresholds'),
                    alert_confirm_intervals=alerts_config.get('alert_confirm_intervals', 2),
                    alert_cooldown_seconds=alerts_config.get('alert_cooldown_seconds', 3600.0)
                )
                logger.info("Inventory tracker initialized with persistence, sales attribution, and alerts")
            else:
                self.inventory_tracker = InventoryTracker(
                    smoothing_window=inventory_config.get('smoothing_window', 10),
                    smoothing_method=inventory_config.get('smoothing_method', 'median'),
                    class_names=self.detector.class_names
                )
                logger.info("Inventory tracker initialized (persistence disabled)")
            
            # Initialize web server
            logger.info("Initializing web server...")
            server_config = self.config.get('server', {})
            frontend_dir = Path(__file__).parent.parent / 'frontend'
            
            self.server = VideoStreamServer(
                host=server_config.get('host', '0.0.0.0'),
                port=server_config.get('port', 8080),
                frontend_dir=frontend_dir
            )
            
            logger.info(f"Web server initialized at http://{server_config.get('host', '0.0.0.0')}:{server_config.get('port', 8080)}")
            
            # Initialize stream manager
            stream_config = self.config.get('stream', {})
            self.stream_manager = StreamManager(
                camera=self.camera,
                detector=self.detector,
                inventory_tracker=self.inventory_tracker,
                server=self.server,
                target_fps=stream_config.get('target_fps', 30)
            )
            
            logger.info("Stream manager initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}", exc_info=True)
            return False
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self):
        """Graceful shutdown of all components"""
        logger.info("Shutting down inventory system...")
        
        # Stop streaming
        if self.stream_manager:
            await self.stream_manager.stop()
        
        # Release camera
        if self.camera:
            self.camera.release()
        
        # Close persistence layer and log final statistics
        if self.inventory_tracker:
            stats = self.inventory_tracker.get_statistics()
            logger.info(f"Final statistics: {stats}")
            
            # Close persistence if available
            if hasattr(self.inventory_tracker, 'close'):
                self.inventory_tracker.close()
        
        self.shutdown_event.set()
        logger.info("Shutdown complete")
    
    async def run(self):
        """
        Main application loop
        """
        logger.info("=" * 60)
        logger.info("Poke Bowl Inventory System")
        logger.info("=" * 60)
        
        # Initialize components
        if not self.initialize_components():
            logger.error("Initialization failed, exiting")
            return
        
        try:
            # Start web server
            logger.info("Starting web server...")
            await self.server.start()
            
            # Start streaming
            logger.info("Starting video stream...")
            self.stream_manager.start()
            
            logger.info("=" * 60)
            logger.info("System ready!")
            logger.info(f"Web interface available at: {self.server.get_url()}")
            logger.info("Press Ctrl+C to stop")
            logger.info("=" * 60)
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"Runtime error: {e}", exc_info=True)
        
        finally:
            await self.shutdown()


def create_pid_file():
    """
    Create PID file for single-instance protection
    """
    pid_file = '/tmp/pokebowl.pid'
    
    # Check if already running
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())
            
            # Check if process is still running
            try:
                os.kill(old_pid, 0)
                logger.error(f"Another instance is already running (PID: {old_pid})")
                sys.exit(1)
            except OSError:
                # Process not running, remove stale PID file
                logger.warning(f"Removing stale PID file (PID: {old_pid})")
                os.remove(pid_file)
        except Exception as e:
            logger.warning(f"Error checking PID file: {e}")
    
    # Write current PID
    try:
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f"PID file created: {pid_file}")
    except Exception as e:
        logger.warning(f"Failed to create PID file: {e}")


def remove_pid_file():
    """
    Remove PID file on shutdown
    """
    pid_file = '/tmp/pokebowl.pid'
    try:
        if os.path.exists(pid_file):
            os.remove(pid_file)
            logger.info("PID file removed")
    except Exception as e:
        logger.warning(f"Failed to remove PID file: {e}")


async def main():
    """
    Application entry point
    """
    # Create PID file for single-instance protection
    create_pid_file()
    
    try:
        # Determine config path
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        
        # Create and run system
        system = InventorySystem(config_path)
        
        # Setup signal handlers
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(system.shutdown()))
        
        # Run system
        await system.run()
    
    finally:
        # Always remove PID file
        remove_pid_file()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        remove_pid_file()

