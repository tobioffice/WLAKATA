import cv2
import numpy as np


def detect_color_cube(img, color_values, tolerance=15):
    """Detect if a specific colored cube is present in the image"""
    for rgb in color_values:
        # Convert RGBA to BGR (OpenCV format)
        bgr = (rgb[2], rgb[1], rgb[0])
        print(bgr)

        # Create range with tolerance
        lower = np.array([max(0, val - tolerance) for val in bgr])
        upper = np.array([min(255, val + tolerance) for val in bgr])
        print(lower, upper)

        # Create mask for this color value
        mask = cv2.inRange(img, lower, upper)

        # If we find enough pixels of this color, consider it detected
        if cv2.countNonZero(mask) > 100:  # Threshold for minimum pixels
            return True

    return False


def detect_cubes(image_path):
    # Read the image
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError(f"Could not read image at {image_path}")

    # Define exact color values (R,G,B,A)
    color_values = {
        'red': [
            (143, 36, 38, 255),
            (153, 43, 44, 255)
        ],
        'green': [
            (17, 124, 84, 255),
            (30, 128, 89, 255)
        ],
        'blue': [
            (35, 74, 134, 255),
            (35, 75, 134, 255)
        ]
    }

    # Detect each color
    detected_colors = []
    for color, values in color_values.items():
        if detect_color_cube(img, values):
            detected_colors.append(color)

    return detected_colors


def main():
    image_path = "croped_rgb.jpg"

    try:
        # Detect cubes
        detected_colors = detect_cubes(image_path)

        # Print results with better formatting
        print("\nAnalyzing image:", image_path)
        print("-" * 40)
        if detected_colors:
            print("Detected cubes:")
            for color in detected_colors:
                print(f"- {color}")
        else:
            print("No colored cubes detected")
        print("-" * 40)

        # Display the image
        img = cv2.imread(image_path)
        cv2.imshow('Analyzed Image', img)
        print("Press any key to close the image window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
