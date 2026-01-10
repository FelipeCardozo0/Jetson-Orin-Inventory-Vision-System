# Testing On PC - Development Environment

This folder provides a PC-compatible testing environment for the Jetson Orin Inventory Vision System. It allows you to run and test the system on a standard desktop/laptop using a built-in or USB webcam.

## Purpose

- Test the inventory system on PC before deploying to Jetson
- Use built-in webcam (FaceTime camera on Mac, etc.)
- Debug and iterate quickly without Jetson hardware
- **Does NOT modify any original project files**

## Quick Start

### 1. Install PC Dependencies

```bash
cd "Testing On Pc"
bash install_pc_dependencies.sh
```

### 2. Run the System

```bash
python3 run_pc_test.py
```

The system will:
- Use your PC's default webcam (camera index 0)
- Run YOLO inference on CPU (or GPU if available)
- Start the web interface at http://localhost:8080
- Display live detection and inventory counts

### 3. Access Web Interface

Open your browser to: **http://localhost:8080**

### 4. Stop the System

Press `Ctrl+C` in the terminal

## What This Does

### Files in This Folder

- **install_pc_dependencies.sh** - Installs PC-compatible Python packages
- **run_pc_test.py** - Main launcher that imports and runs the original project
- **pc_config.yaml** - PC-specific configuration (overrides via environment)
- **requirements_pc.txt** - PC-specific dependencies
- **README.md** - This file

### How It Works

1. **No Original Files Modified**: The launcher imports the original backend modules directly
2. **Configuration Override**: Uses environment variables and config file to set PC-appropriate settings
3. **Dependency Management**: Installs standard PyTorch/OpenCV instead of Jetson-specific versions
4. **Camera Compatibility**: Automatically uses camera index 0 (built-in webcam)

## Configuration

Edit `pc_config.yaml` to customize:

```yaml
camera:
  index: 0              # 0 = built-in webcam, 1 = external USB camera
  width: 1280
  height: 720
  fps: 30

detector:
  device: 'cpu'         # Use 'cpu' or '0' for GPU if available
  half: false           # FP16 not needed on PC
  conf_threshold: 0.25
```

## Troubleshooting

### Camera Not Found

```bash
# List available cameras (Mac)
system_profiler SPCameraDataType

# Test camera access
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera failed')"
```

**Solution**: Change `camera.index` in `pc_config.yaml`

### PyTorch Not Installed

```bash
pip3 install torch torchvision
```

### YOLO Model Not Found

Make sure `best.pt` exists in the parent directory:
```bash
ls -lh ../best.pt
```

### Port 8080 Already in Use

```bash
# Kill existing process
lsof -ti:8080 | xargs kill -9

# Or change port in pc_config.yaml
```

## Performance Expectations

On a typical PC/Mac:
- **FPS**: 10-20 (CPU), 20-30 (GPU)
- **Inference Time**: 50-100ms (CPU), 20-40ms (GPU)
- **Memory**: ~500MB

## Differences from Jetson

| Feature | Jetson | PC Testing |
|---------|--------|------------|
| PyTorch | Jetson wheel | Standard pip |
| Device | GPU (CUDA) | CPU or GPU |
| FP16 | Enabled | Disabled |
| Camera | USB (V4L2) | Built-in webcam |
| Performance | Optimized | Development |

## Development Workflow

1. **Test on PC**: Make changes and test with `run_pc_test.py`
2. **Verify**: Ensure system works with webcam
3. **Deploy to Jetson**: Original code runs unchanged on Jetson
4. **Iterate**: Repeat as needed

## Important Notes

- **Original project files are NEVER modified**
- This folder is for testing only
- Production deployment uses the original backend directly
- Camera index 0 works for most built-in webcams
- GPU acceleration optional (CPU works fine for testing)

## System Requirements

- Python 3.8+
- OpenCV
- PyTorch (CPU version is fine)
- Webcam (built-in or USB)
- 4GB+ RAM

## Support

If you encounter issues:
1. Check camera access permissions
2. Verify dependencies installed correctly
3. Review logs in terminal output
4. Test camera independently with OpenCV
