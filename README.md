# Vision-Based Biscuit Sorting Robot

This project implements a vision-based sorting system for biscuits using the WLKATA Mirobot robotic arm and ZED 2i stereo camera. The system can detect and sort biscuits based on defects such as breaks, burns, and shape distortions.

## Hardware Requirements

- WLKATA Mirobot Professional Kit - 6 Axis Robotic Arm
- Conveyor belt Set For Wlkata Mirobot (MS4220)
- ZED 2i Stereo Camera
- Multifunctional Extender Box (Firmware version 20230710 or later)

## Software Requirements

- Python 3.9 or later
- OpenCV for image processing
- WLKATA Python SDK
- ZED SDK
- PySerial

## Installation

1. Install project dependencies using `uv`:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

2. Connect hardware components:
   - Connect WLKATA Mirobot to multifunctional extender box
   - Connect ZED 2i camera via USB
   - Setup conveyor belt system
   - Position camera to view conveyor belt workspace

3. Configure system:
   - Adjust camera position and focus
   - Calibrate robot coordinates with camera coordinates
   - Set drop zones for different defect categories

## Usage

1. Start the system:
```bash
python main.py
```

2. The system will:
   - Initialize robot and camera
   - Begin monitoring conveyor belt for biscuits
   - Detect defects using computer vision
   - Sort biscuits into appropriate zones

3. Press 'q' to quit the program

## Features

- Real-time defect detection
- Multiple defect categories:
  - Good condition
  - Broken/Shadow
  - Semi-burned
  - Fully-burned
- Intelligent conveyor control:
  - Automatic speed control (30% default)
  - Pick zone detection (±50px from center)
  - Auto-stop for precise picking
  - Auto-resume after sorting
- Continuous operation:
  - Real-time object tracking
  - Dynamic pick timing
  - Synchronized robot-conveyor movement
- Safety checks and error handling

## Architecture

The system consists of three main components:

1. **BiscuitDefectDetector**: Handles image processing and defect detection using:
   - Grayscale intensity analysis
   - Shape analysis
   - Contour detection

2. **RobotController**: Manages robot and conveyor operations including:
   - Robot initialization and homing
   - Pick and place movements
   - Pneumatic control
   - Conveyor belt speed control (-100 to 100)

3. **VisionBasedSorter**: Coordinates between vision and robot systems:
   - Camera frame capture
   - Coordinate mapping
   - Sorting logic
   - Real-time defect classification

## Operation

1. The system operates continuously:
   - Conveyor moves at 30% speed
   - Camera tracks biscuit positions
   - When biscuit reaches pick zone:
     * Conveyor stops automatically
     * Vision system analyzes defects
     * Robot picks and sorts biscuit
     * Conveyor resumes movement

2. Conveyor Control:
   - Speed range: -100 to 100
   - Default speed: 30 (controllable)
   - Auto-stops in pick zone
   - Auto-resumes after sorting

3. Pick Zone:
   - Located at center of camera view
   - ±50 pixel tolerance
   - Ensures precise picking
   - Reduces motion blur for analysis

## Safety Notes

- Ensure proper clearance around robot workspace
- Monitor system during operation
- Use emergency stop when needed
- Keep hands clear of conveyor and robot

## Troubleshooting

- Check camera connection if frame capture fails
- Verify robot connection and initialization
- Ensure proper lighting conditions
- Calibrate camera-robot coordinates if sorting is inaccurate

## License

© La Fondation Dassault Systèmes | Confidential Information
