#!/usr/bin/env python3
"""
server.py - Central WebSocket Server for YOLOv8 Video Streaming

This FastAPI server receives video frames from multiple Raspberry Pi clients
and broadcasts them to web browser viewers in real-time.

Usage:
    uvicorn server:app --host 0.0.0.0 --port 8000
"""

import asyncio
import logging
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="YOLOv8 Video Streaming Server")

# Store active WebSocket connections
class ConnectionManager:
    """Manages WebSocket connections for viewers and publishers."""
    
    def __init__(self):
        # Set of viewer connections (browsers watching the streams)
        self.viewers: Set[WebSocket] = set()
        
        # Dictionary of publisher connections (Raspberry Pis sending streams)
        # Key: camera_id, Value: WebSocket connection
        self.publishers: dict = {}
    
    async def connect_viewer(self, websocket: WebSocket):
        """Add a new viewer connection."""
        await websocket.accept()
        self.viewers.add(websocket)
        logger.info(f"New viewer connected. Total viewers: {len(self.viewers)}")
    
    def disconnect_viewer(self, websocket: WebSocket):
        """Remove a viewer connection."""
        self.viewers.discard(websocket)
        logger.info(f"Viewer disconnected. Total viewers: {len(self.viewers)}")
    
    async def connect_publisher(self, camera_id: str, websocket: WebSocket):
        """Add or update a publisher connection."""
        await websocket.accept()
        
        # Close existing connection if camera_id already exists
        if camera_id in self.publishers:
            old_ws = self.publishers[camera_id]
            try:
                await old_ws.close()
            except:
                pass
        
        self.publishers[camera_id] = websocket
        logger.info(f"Publisher '{camera_id}' connected. Total publishers: {len(self.publishers)}")
    
    def disconnect_publisher(self, camera_id: str):
        """Remove a publisher connection."""
        if camera_id in self.publishers:
            del self.publishers[camera_id]
            logger.info(f"Publisher '{camera_id}' disconnected. Total publishers: {len(self.publishers)}")
    
    async def broadcast_to_viewers(self, message: str):
        """Broadcast a message to all connected viewers."""
        if not self.viewers:
            return
        
        # Send to all viewers, removing any that fail
        disconnected = set()
        
        for viewer in self.viewers:
            try:
                await viewer.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to viewer: {e}")
                disconnected.add(viewer)
        
        # Remove disconnected viewers
        for viewer in disconnected:
            self.disconnect_viewer(viewer)


# Create connection manager instance
manager = ConnectionManager()


@app.get("/")
async def get_homepage():
    """Serve the frontend HTML page."""
    html_path = Path("index.html")
    
    if not html_path.exists():
        return HTMLResponse(
            content="<h1>Error: index.html not found</h1>",
            status_code=404
        )
    
    with open(html_path, "r") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content)


@app.websocket("/ws/broadcast")
async def websocket_broadcast_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for viewers (web browsers).
    Viewers connect here to receive video streams from all cameras.
    """
    await manager.connect_viewer(websocket)
    
    try:
        # Keep the connection alive and listen for any messages
        while True:
            # We don't expect messages from viewers, but we need to keep the loop running
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        manager.disconnect_viewer(websocket)
    except Exception as e:
        logger.error(f"Error in viewer connection: {e}")
        manager.disconnect_viewer(websocket)


@app.websocket("/ws/publish/{camera_id}")
async def websocket_publish_endpoint(websocket: WebSocket, camera_id: str):
    """
    WebSocket endpoint for publishers (Raspberry Pis).
    Each Raspberry Pi connects here to send its video stream.
    
    Args:
        camera_id: Unique identifier for the camera (e.g., cam1, cam2, cam3, cam4)
    """
    await manager.connect_publisher(camera_id, websocket)
    
    try:
        while True:
            # Receive frame data from the Raspberry Pi
            frame_data = await websocket.receive_text()
            
            # Broadcast the frame to all connected viewers
            await manager.broadcast_to_viewers(frame_data)
            
    except WebSocketDisconnect:
        manager.disconnect_publisher(camera_id)
    except Exception as e:
        logger.error(f"Error in publisher '{camera_id}': {e}")
        manager.disconnect_publisher(camera_id)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "viewers": len(manager.viewers),
        "publishers": len(manager.publishers),
        "active_cameras": list(manager.publishers.keys())
    }


@app.on_event("startup")
async def startup_event():
    """Run when the server starts."""
    logger.info("=" * 60)
    logger.info("YOLOv8 Video Streaming Server started!")
    logger.info("=" * 60)
    logger.info("Viewer endpoint:    /ws/broadcast")
    logger.info("Publisher endpoint: /ws/publish/{camera_id}")
    logger.info("Homepage:           /")
    logger.info("Health check:       /health")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run when the server shuts down."""
    logger.info("Server shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

