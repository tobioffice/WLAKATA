import cv2
import numpy as np
import serial
import time
import wlkatapython
from typing import Tuple, Dict, List


class BiscuitDefectDetector:
    def __init__(self):
        # Thresholds for different biscuit conditions from project documentation
        self.thresholds = {
            'good': {
                'gray': (68, 180),
                'intensity_range': (100, 180),
                'peak_intensity': 150
            },
            'broken': {
                'gray': (0, 255),
                'intensity_range': (10, 180),
                'peak_intensity': 160
            },
            'semi_burned': {
                'gray': (0, 255),
                'intensity_range': (0, 210),
                'peak_intensity': 100
            },
            'fully_burned': {
                'gray': (1, 255),
                'intensity_range': (0, 150),
                'peak_intensity': 45
            }
        }

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for defect detection"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        return blurred

    def detect_defects(self, image: np.ndarray) -> Dict:
        """Detect defects in biscuit image"""
        processed = self.preprocess_image(image)

        # Calculate intensity histogram
        hist = cv2.calcHist([processed], [0], None, [256], [0, 256])
        peak_intensity = np.argmax(hist)
        intensity_range = (int(processed.min()), int(processed.max()))

        # Analyze shape for breaks
        _, binary = cv2.threshold(processed, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) == 0:
            return {'status': 'no_biscuit_detected'}

        contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(contour)

        # Classify defect based on intensity and shape analysis
        result = {
            'status': 'unknown',
            'confidence': 0.0,
            'metrics': {
                'peak_intensity': peak_intensity,
                'intensity_range': intensity_range,
                'area': area
            }
        }

        # Classification logic based on project thresholds
        if (self.thresholds['good']['intensity_range'][0] <= peak_intensity <=
                self.thresholds['good']['intensity_range'][1]):
            result['status'] = 'good'
            result['confidence'] = 0.9
        elif peak_intensity <= self.thresholds['fully_burned']['peak_intensity']:
            result['status'] = 'fully_burned'
            result['confidence'] = 0.85
        elif peak_intensity <= self.thresholds['semi_burned']['peak_intensity']:
            result['status'] = 'semi_burned'
            result['confidence'] = 0.8
        else:
            result['status'] = 'broken'
            result['confidence'] = 0.75

        return result


class RobotController:
    def __init__(self, port: str = "COM3", baud: int = 38400):
        """Initialize robot controller"""
        self.serial = serial.Serial(port, baud)
        self.robot = wlkatapython.Wlkata_UART()
        self.robot.init(self.serial, -1)  # Initialize with address 1

    def home(self):
        """Home the robot"""
        self.robot.homing()

    def pick(self, x: float, y: float, z: float):
        """Pick object at given coordinates"""
        # Move to position
        self.robot.sendMsg(f"G1 X{x} Y{y} Z{z}")
        time.sleep(0.5)
        # Enable suction
        self.robot.pump(1)
        time.sleep(0.5)

    def place(self, x: float, y: float, z: float):
        """Place object at given coordinates"""
        # Move to position
        self.robot.sendMsg(f"G1 X{x} Y{y} Z{z}")
        time.sleep(0.5)
        # Disable suction
        self.robot.pump(0)
        time.sleep(0.5)

    def cleanup(self):
        """Cleanup robot connection"""
        self.robot.pump(0)  # Ensure pump is off
        self.serial.close()


class VisionBasedSorter:
    def __init__(self):
        """Initialize vision-based sorting system"""
        # Initialize robot and conveyor
        self.serial = serial.Serial("COM3", 38400)
        self.detector = BiscuitDefectDetector()
        self.robot = RobotController()
        self.conveyor = wlkatapython.MS4220_UART()
        self.conveyor.init(self.serial, 1)  # Initialize with address 1

        # Initialize camera
        self.cap = cv2.VideoCapture(0)  # Use ZED camera index
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open camera")

        # Define drop zones for different categories
        self.drop_zones = {
            'good': (200, 0, 50),
            'broken': (200, 100, 50),
            'semi_burned': (200, -100, 50),
            'fully_burned': (200, -200, 50)
        }

    def get_object_position(self, frame: np.ndarray) -> Tuple[float, float, float, bool]:
        """
        Get object position from camera frame and determine if it's in pick zone
        Returns: (x, y, z, is_in_pick_zone)
        """
        # Convert image coordinates to robot coordinates
        height, width = frame.shape[:2]

        # Find objects using contour detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return 0, 0, 0, False

        # Get the largest contour (assuming it's the biscuit)
        contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(contour)

        if M["m00"] == 0:
            return 0, 0, 0, False

        # Get centroid
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])

        # Define pick zone (center of frame +/- margin)
        pick_zone_margin = 50  # pixels
        center_x = width / 2
        is_in_pick_zone = abs(cx - center_x) < pick_zone_margin

        # Map to robot coordinates
        # Assuming conveyor runs along X axis
        robot_x = 200  # Fixed X position for picking
        robot_y = ((cx - center_x) / width) * 400  # Scale to robot workspace
        robot_z = 50  # Fixed height for picking

        return robot_x, robot_y, robot_z, is_in_pick_zone

    def sort(self):
        """Main sorting routine"""
        print("Starting vision-based sorting...")

        try:
            # Home the robot
            self.robot.home()

            # Initialize variables
            conveyor_speed = 30  # 30% speed for controlled movement
            print("Starting conveyor belt...")
            self.conveyor.speed(conveyor_speed)

            while True:
                # Capture frame
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to capture frame")
                    continue

                # Get object position and check if in pick zone
                pick_x, pick_y, pick_z, is_in_pick_zone = self.get_object_position(
                    frame)

                if is_in_pick_zone:
                    # Stop conveyor for picking
                    self.conveyor.speed(0)

                    # Detect defects
                    result = self.detector.detect_defects(frame)
                    if result['status'] == 'no_biscuit_detected':
                        # Restart conveyor and continue
                        self.conveyor.speed(conveyor_speed)
                        continue

                    # Get drop zone for detected condition
                    drop_zone = self.drop_zones[result['status']]

                    # Execute pick and place
                    print(
                        f"Detected {result['status']} with confidence {result['confidence']}")
                    self.robot.pick(pick_x, pick_y, pick_z)
                    self.robot.place(*drop_zone)

                    # Restart conveyor after placing
                    self.conveyor.speed(conveyor_speed)

                # Check for user interrupt
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            # Cleanup
            self.cap.release()
            cv2.destroyAllWindows()
            self.robot.cleanup()
            self.conveyor.speed(0)  # Stop conveyor
            self.serial.close()


def main():
    sorter = VisionBasedSorter()
    try:
        sorter.sort()
    except KeyboardInterrupt:
        print("\nSorting interrupted by user")
    except Exception as e:
        print(f"Error occurred: {e}")
    print("Sorting completed.")


if __name__ == "__main__":
    main()
