# Quick Command Reference

## Camera Setup Commands

### Use PC Built-in Webcam

```bash
python3 run_pc_webcam.py
```

**What it does:**
- Uses camera index 0 (built-in webcam)
- Config: `pc_config.yaml`
- Best for: Testing on Mac/PC without external devices

**Troubleshooting:**
- If camera not found, check permissions: System Preferences → Security & Privacy → Camera
- Test camera: `python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"`

---

### Use Phone Camera (iPhone via USB)

```bash
python3 run_phone_camera.py
```

**What it does:**
- Uses camera index 1 (default, configurable)
- Config: `phone_config.yaml`
- Best for: Using iPhone camera connected via USB

**Setup Steps:**
1. Connect iPhone via USB cable
2. Unlock iPhone
3. Tap "Trust This Computer" when prompted
4. Run the command

**Troubleshooting:**
- If phone camera not detected:
 - Check USB connection
 - Verify iPhone is unlocked and trusted
 - Check System Preferences → Camera → iPhone should appear
 - Try different camera index in `phone_config.yaml`:
 - Open `phone_config.yaml`
 - Change `camera.index: 1` to `camera.index: 2` (or 3, etc.)
 - List available cameras: Run the script and it will show all cameras

---

## Finding Your Camera Index

Both scripts will automatically list available cameras. Look for output like:

```
Scanning for available cameras...
 Camera 0: 1280x720 (PC Webcam)
 Camera 1: 1920x1080 (iPhone Camera)
```

The script will indicate which camera it's using.

---

## Configuration Files

### PC Webcam Configuration
**File**: `pc_config.yaml`
- `camera.index: 0` - PC built-in webcam

### Phone Camera Configuration
**File**: `phone_config.yaml`
- `camera.index: 1` - Phone camera (adjust if needed)

To change camera index, edit the respective config file.

---

## Common Issues

### "Cannot open camera at index X"

1. **Check camera permissions** (Mac):
 - System Preferences → Security & Privacy → Camera
 - Enable camera access for Terminal/Python

2. **List available cameras**:
 ```bash
 python3 -c "import cv2; [print(f'Camera {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(5)]"
 ```

3. **Try different index**:
 - Edit `pc_config.yaml` or `phone_config.yaml`
 - Change `camera.index` to the working camera number

### Phone Camera Not Appearing

1. **Check iPhone connection**:
 - USB cable connected
 - iPhone unlocked
 - "Trust This Computer" tapped

2. **Check System Preferences**:
 - System Preferences → Camera
 - iPhone should appear in the list

3. **Try different USB port**:
 - Some ports may not support camera access

### Port 8080 Already in Use

```bash
# Kill existing process
lsof -ti:8080 | xargs kill -9

# Or change port in config file
```

---

## Quick Test

Test camera access quickly:

```bash
# Test PC webcam (index 0)
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('PC Webcam OK' if cap.isOpened() else 'Failed'); cap.release()"

# Test phone camera (index 1)
python3 -c "import cv2; cap = cv2.VideoCapture(1); print('Phone Camera OK' if cap.isOpened() else 'Failed'); cap.release()"
```

---

## Summary

| Command | Camera | Config File | Use Case |
|---------|--------|-------------|----------|
| `python3 run_pc_webcam.py` | Built-in webcam (index 0) | `pc_config.yaml` | Quick testing, no external devices |
| `python3 run_phone_camera.py` | iPhone via USB (index 1+) | `phone_config.yaml` | Higher quality, mobile camera |
