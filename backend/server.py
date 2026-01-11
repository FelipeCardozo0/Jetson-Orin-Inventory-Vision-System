"""
Web Server with Frame Streaming
Serves frontend and streams video + inventory data via WebSockets
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Optional, Set
import base64

import cv2
import numpy as np
from aiohttp import web
import aiohttp

# Import authentication module
try:
    from auth import load_auth_config, AuthManager
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    logger.warning("Authentication module not available")

logger = logging.getLogger(__name__)


class VideoStreamServer:
    """
    Lightweight async web server for streaming video and inventory data
    Uses WebSockets for low-latency bidirectional communication
    """
    
    def __init__(
        self,
        host: str = '0.0.0.0',
        port: int = 8080,
        frontend_dir: Optional[Path] = None,
        enable_auth: bool = True
    ):
        """
        Initialize web server
        
        Args:
            host: Server host address
            port: Server port
            frontend_dir: Path to frontend files
            enable_auth: Enable authentication (default: True)
        """
        self.host = host
        self.port = port
        self.frontend_dir = frontend_dir or Path(__file__).parent.parent / 'frontend'
        
        # Initialize authentication
        self.auth_enabled = False
        self.auth_manager: Optional[AuthManager] = None
        self.cookie_name = 'pb_session'
        
        if enable_auth and AUTH_AVAILABLE:
            auth_enabled, auth_manager = load_auth_config()
            if auth_enabled and auth_manager:
                self.auth_enabled = True
                self.auth_manager = auth_manager
                logger.info("Authentication enabled")
            elif auth_enabled and not auth_manager:
                # Auth enabled but not configured = deny access
                self.auth_enabled = True
                self.auth_manager = None
                logger.warning("Authentication enabled but not configured - access will be denied")
            else:
                logger.info("Authentication disabled")
        elif enable_auth and not AUTH_AVAILABLE:
            logger.warning("Authentication requested but module not available")
        
        self.app = web.Application()
        self.setup_routes()
        
        # Active WebSocket connections
        self.websockets: Set[web.WebSocketResponse] = set()
        
        # Latest frame and inventory data
        self.latest_frame: Optional[np.ndarray] = None
        self.latest_inventory: dict = {}
        self.latest_stats: dict = {}
        self.latest_freshness: dict = {}
        self.latest_sales: list = []
        self.latest_alerts: list = []
        
        # Server statistics
        self.frames_streamed = 0
        self.start_time = time.time()
        
    def setup_routes(self):
        """Setup HTTP and WebSocket routes"""
        # Public routes (no authentication required)
        self.app.router.add_get('/login', self.handle_login_page)
        self.app.router.add_post('/api/login', self.handle_login)
        self.app.router.add_post('/api/logout', self.handle_logout)
        self.app.router.add_get('/health', self.handle_health)
        
        # Protected routes (authentication required)
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/ws', self.handle_websocket)
        self.app.router.add_get('/api/stats', self.handle_stats)
        self.app.router.add_get('/api/freshness', self.handle_freshness)
        self.app.router.add_get('/api/sales', self.handle_sales)
        self.app.router.add_get('/api/alerts', self.handle_alerts)
        
    async def handle_index(self, request: web.Request) -> web.Response:
        """Serve main HTML page"""
        # Check authentication
        if not await self.check_auth(request):
            return web.HTTPFound('/login')
        
        index_path = self.frontend_dir / 'index.html'
        
        if not index_path.exists():
            return web.Response(
                text="Frontend not found. Please ensure frontend/index.html exists.",
                status=404
            )
        
        return web.FileResponse(index_path)
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        uptime = time.time() - self.start_time
        
        health_data = {
            'status': 'healthy',
            'uptime_seconds': uptime,
            'active_connections': len(self.websockets),
            'frames_streamed': self.frames_streamed
        }
        
        return web.json_response(health_data)
    
    async def handle_stats(self, request: web.Request) -> web.Response:
        """Return current statistics"""
        # Check authentication
        if not await self.check_auth(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        return web.json_response(self.latest_stats)
    
    async def handle_freshness(self, request: web.Request) -> web.Response:
        """Return current freshness data"""
        # Check authentication
        if not await self.check_auth(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        return web.json_response(self.latest_freshness)
    
    async def handle_sales(self, request: web.Request) -> web.Response:
        """Return sales log"""
        # Check authentication
        if not await self.check_auth(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        limit = int(request.query.get('limit', 100))
        return web.json_response(self.latest_sales[:limit])
    
    async def handle_alerts(self, request: web.Request) -> web.Response:
        """Return alerts log"""
        # Check authentication
        if not await self.check_auth(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        limit = int(request.query.get('limit', 20))
        return web.json_response(self.latest_alerts[:limit])
    
    async def handle_login_page(self, request: web.Request) -> web.Response:
        """Serve login page"""
        login_path = self.frontend_dir / 'login.html'
        
        if not login_path.exists():
            return web.Response(
                text="Login page not found.",
                status=404
            )
        
        return web.FileResponse(login_path)
    
    async def handle_login(self, request: web.Request) -> web.Response:
        """Handle login POST request"""
        if not self.auth_enabled:
            return web.json_response({'success': True, 'message': 'Authentication disabled'})
        
        if not self.auth_manager:
            return web.json_response({'success': False, 'message': 'Authentication not configured'}, status=503)
        
        try:
            data = await request.json()
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or not password:
                return web.json_response({'success': False, 'message': 'Username and password required'}, status=400)
            
            # Authenticate user
            session_token = self.auth_manager.authenticate(username, password)
            
            if session_token:
                # Create response with session cookie
                response = web.json_response({'success': True, 'message': 'Login successful'})
                
                # Determine if we're behind HTTPS
                is_secure = request.headers.get('X-Forwarded-Proto', '').lower() == 'https'
                
                # Set session cookie
                response.set_cookie(
                    self.cookie_name,
                    session_token,
                    max_age=86400,  # 24 hours
                    httponly=True,
                    samesite='Lax',
                    secure=is_secure,
                    path='/'
                )
                
                return response
            else:
                return web.json_response({'success': False, 'message': 'Invalid username or password'}, status=401)
        
        except Exception as e:
            logger.error(f"Login error: {e}")
            return web.json_response({'success': False, 'message': 'Login failed'}, status=500)
    
    async def handle_logout(self, request: web.Request) -> web.Response:
        """Handle logout POST request"""
        response = web.json_response({'success': True, 'message': 'Logged out'})
        
        # Clear session cookie
        response.del_cookie(self.cookie_name, path='/')
        
        return response
    
    async def check_auth(self, request: web.Request) -> bool:
        """
        Check if request is authenticated
        
        Args:
            request: HTTP request
            
        Returns:
            True if authenticated or auth disabled, False otherwise
        """
        if not self.auth_enabled:
            return True
        
        if not self.auth_manager:
            # Auth enabled but not configured = deny access
            return False
        
        # Get session cookie
        session_token = request.cookies.get(self.cookie_name)
        if not session_token:
            return False
        
        # Verify session
        username = self.auth_manager.verify_session(session_token)
        if username:
            # Store username in request for potential future use
            request['username'] = username
            return True
        
        return False
    
    async def handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """
        Handle WebSocket connection for streaming
        Sends frames and inventory updates to client
        """
        # Check authentication
        if not await self.check_auth(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            await ws.send_json({'error': 'Unauthorized', 'type': 'error'})
            await ws.close()
            return ws
        
        ws = web.WebSocketResponse(
            heartbeat=30,  # Send ping every 30s
            compress=False  # Disable compression for lower latency
        )
        await ws.prepare(request)
        
        self.websockets.add(ws)
        client_addr = request.remote
        logger.info(f"WebSocket connected: {client_addr} (total: {len(self.websockets)})")
        
        try:
            # Send initial data
            await self.send_to_client(ws, {
                'type': 'inventory',
                'data': self.latest_inventory
            })
            
            await self.send_to_client(ws, {
                'type': 'freshness',
                'data': self.latest_freshness
            })
            
            await self.send_to_client(ws, {
                'type': 'sales',
                'data': self.latest_sales
            })
            
            await self.send_to_client(ws, {
                'type': 'alerts',
                'data': self.latest_alerts
            })
            
            # Handle incoming messages (if any)
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self.handle_client_message(ws, data)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON from {client_addr}")
                
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
        
        except asyncio.CancelledError:
            logger.info(f"WebSocket cancelled: {client_addr}")
        
        except Exception as e:
            logger.error(f"WebSocket error for {client_addr}: {e}")
        
        finally:
            self.websockets.discard(ws)
            logger.info(f"WebSocket disconnected: {client_addr} (remaining: {len(self.websockets)})")
        
        return ws
    
    async def handle_client_message(self, ws: web.WebSocketResponse, data: dict):
        """
        Handle incoming message from client
        
        Args:
            ws: WebSocket connection
            data: Parsed JSON data
        """
        msg_type = data.get('type')
        
        if msg_type == 'ping':
            await self.send_to_client(ws, {'type': 'pong'})
        
        elif msg_type == 'request_frame':
            # Client requesting latest frame
            if self.latest_frame is not None:
                await self.send_frame_to_client(ws, self.latest_frame)
    
    async def send_to_client(self, ws: web.WebSocketResponse, data: dict):
        """
        Send JSON data to a single client
        
        Args:
            ws: WebSocket connection
            data: Data to send
        """
        try:
            await ws.send_json(data)
        except Exception as e:
            logger.error(f"Failed to send to client: {e}")
    
    async def send_frame_to_client(self, ws: web.WebSocketResponse, frame: np.ndarray):
        """
        Encode and send frame to a single client
        
        Args:
            ws: WebSocket connection
            frame: Frame to send
        """
        try:
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            # Convert to base64
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send with timestamp
            await ws.send_json({
                'type': 'frame',
                'data': frame_b64,
                'timestamp': time.time()
            })
        
        except Exception as e:
            logger.error(f"Failed to send frame: {e}")
    
    async def broadcast_frame(self, frame: np.ndarray):
        """
        Broadcast frame to all connected clients
        
        Args:
            frame: Frame to broadcast
        """
        if not self.websockets:
            return
        
        self.latest_frame = frame.copy()
        self.frames_streamed += 1
        
        # Encode once, send to all
        try:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            
            message = {
                'type': 'frame',
                'data': frame_b64,
                'timestamp': time.time()
            }
            
            # Send to all clients concurrently
            if self.websockets:
                await asyncio.gather(
                    *[ws.send_json(message) for ws in self.websockets],
                    return_exceptions=True
                )
        
        except Exception as e:
            logger.error(f"Failed to broadcast frame: {e}")
    
    async def broadcast_inventory(self, inventory: dict):
        """
        Broadcast inventory update to all clients
        
        Args:
            inventory: Inventory dictionary
        """
        if not self.websockets:
            self.latest_inventory = inventory
            return
        
        self.latest_inventory = inventory
        
        message = {
            'type': 'inventory',
            'data': inventory,
            'timestamp': time.time()
        }
        
        # Send to all clients
        if self.websockets:
            await asyncio.gather(
                *[ws.send_json(message) for ws in self.websockets],
                return_exceptions=True
            )
    
    async def broadcast_stats(self, stats: dict):
        """
        Broadcast statistics to all clients
        
        Args:
            stats: Statistics dictionary
        """
        self.latest_stats = stats
        
        if not self.websockets:
            return
        
        message = {
            'type': 'stats',
            'data': stats,
            'timestamp': time.time()
        }
        
        if self.websockets:
            await asyncio.gather(
                *[ws.send_json(message) for ws in self.websockets],
                return_exceptions=True
            )
    
    def update_frame(self, frame: np.ndarray):
        """
        Update latest frame (synchronous wrapper)
        
        Args:
            frame: New frame
        """
        self.latest_frame = frame.copy()
    
    def update_inventory(self, inventory: dict):
        """
        Update latest inventory (synchronous wrapper)
        
        Args:
            inventory: New inventory
        """
        self.latest_inventory = inventory
    
    def update_stats(self, stats: dict):
        """
        Update latest stats (synchronous wrapper)
        
        Args:
            stats: New statistics
        """
        self.latest_stats = stats
    
    def update_freshness(self, freshness: dict):
        """
        Update latest freshness data (synchronous wrapper)
        
        Args:
            freshness: New freshness data
        """
        self.latest_freshness = freshness
    
    def update_sales(self, sales: list):
        """
        Update latest sales log (synchronous wrapper)
        
        Args:
            sales: New sales log entries
        """
        self.latest_sales = sales
    
    def update_alerts(self, alerts: list):
        """
        Update latest alerts (synchronous wrapper)
        
        Args:
            alerts: New alerts list
        """
        self.latest_alerts = alerts
    
    async def broadcast_freshness(self, freshness: dict):
        """
        Broadcast freshness update to all clients
        
        Args:
            freshness: Freshness dictionary
        """
        self.latest_freshness = freshness
        
        if not self.websockets:
            return
        
        message = {
            'type': 'freshness',
            'data': freshness,
            'timestamp': time.time()
        }
        
        if self.websockets:
            await asyncio.gather(
                *[ws.send_json(message) for ws in self.websockets],
                return_exceptions=True
            )
    
    async def broadcast_sales(self, sales: list):
        """
        Broadcast sales log update to all clients
        
        Args:
            sales: Sales log entries list
        """
        self.latest_sales = sales
        
        if not self.websockets:
            return
        
        message = {
            'type': 'sales',
            'data': sales,
            'timestamp': time.time()
        }
        
        if self.websockets:
            await asyncio.gather(
                *[ws.send_json(message) for ws in self.websockets],
                return_exceptions=True
            )
    
    async def broadcast_alerts(self, alerts: list):
        """
        Broadcast alerts update to all clients
        
        Args:
            alerts: Alerts list
        """
        self.latest_alerts = alerts
        
        if not self.websockets:
            return
        
        message = {
            'type': 'alerts',
            'data': alerts,
            'timestamp': time.time()
        }
        
        if self.websockets:
            await asyncio.gather(
                *[ws.send_json(message) for ws in self.websockets],
                return_exceptions=True
            )
    
    async def start(self):
        """Start the web server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"Server started at http://{self.host}:{self.port}")
        logger.info(f"Frontend directory: {self.frontend_dir}")
    
    def run(self):
        """Run the server (blocking)"""
        web.run_app(
            self.app,
            host=self.host,
            port=self.port,
            print=None,  # Disable aiohttp's startup message
            access_log=None  # Disable access logs for performance
        )
    
    def get_url(self) -> str:
        """
        Get server URL
        
        Returns:
            Server URL string
        """
        return f"http://{self.host}:{self.port}"


class StreamManager:
    """
    Manages streaming loop coordination between camera, detector, and server
    """
    
    def __init__(
        self,
        camera,
        detector,
        inventory_tracker,
        server: VideoStreamServer,
        target_fps: int = 30
    ):
        """
        Initialize stream manager
        
        Args:
            camera: USBCamera instance
            detector: YOLODetector instance
            inventory_tracker: InventoryTracker instance
            server: VideoStreamServer instance
            target_fps: Target streaming FPS
        """
        self.camera = camera
        self.detector = detector
        self.inventory_tracker = inventory_tracker
        self.server = server
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps
        
        self.is_running = False
        self.loop_task = None
    
    async def stream_loop(self):
        """
        Main streaming loop
        Captures frames, runs inference, updates inventory, and broadcasts
        """
        logger.info("Starting stream loop...")
        self.is_running = True
        
        frame_count = 0
        last_stats_time = time.time()
        stats_interval = 1.0  # Update stats every second
        
        while self.is_running:
            loop_start = time.time()
            
            # Capture frame
            success, frame = self.camera.read()
            
            if not success or frame is None:
                logger.warning("Failed to capture frame, attempting reconnection...")
                if not self.camera.reconnect():
                    await asyncio.sleep(1.0)
                    continue
                success, frame = self.camera.read()
                if not success:
                    await asyncio.sleep(1.0)
                    continue
            
            # Run detection
            detections = self.detector.detect(frame)
            
            # Update inventory
            self.inventory_tracker.update(detections)
            inventory = self.inventory_tracker.get_inventory()
            
            # Draw detections on frame
            annotated_frame = self.detector.draw_detections(frame, detections)
            
            # Broadcast frame and inventory
            await self.server.broadcast_frame(annotated_frame)
            await self.server.broadcast_inventory(inventory)
            
            frame_count += 1
            
            # Broadcast stats periodically
            current_time = time.time()
            if current_time - last_stats_time >= stats_interval:
                stats = {
                    'fps': self.detector.get_fps(),
                    'inference_time': self.detector.get_average_inference_time(),
                    'total_items': self.inventory_tracker.get_total_items(),
                    'frame_count': frame_count,
                    'active_connections': len(self.server.websockets)
                }
                await self.server.broadcast_stats(stats)
                
                # Broadcast freshness, sales, and alerts data if available
                if hasattr(self.inventory_tracker, 'get_freshness_state'):
                    freshness = self.inventory_tracker.get_freshness_state()
                    await self.server.broadcast_freshness(freshness)
                
                if hasattr(self.inventory_tracker, 'get_sales_history'):
                    sales = self.inventory_tracker.get_sales_history(limit=100)
                    await self.server.broadcast_sales(sales)
                
                if hasattr(self.inventory_tracker, 'get_recent_alerts'):
                    alerts = self.inventory_tracker.get_recent_alerts(limit=20)
                    await self.server.broadcast_alerts(alerts)
                
                last_stats_time = current_time
            
            # Maintain target FPS
            elapsed = time.time() - loop_start
            sleep_time = max(0, self.frame_interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        logger.info("Stream loop stopped")
    
    def start(self):
        """Start streaming loop"""
        if self.is_running:
            logger.warning("Stream already running")
            return
        
        self.loop_task = asyncio.create_task(self.stream_loop())
    
    async def stop(self):
        """Stop streaming loop"""
        self.is_running = False
        
        if self.loop_task:
            await self.loop_task
            self.loop_task = None

