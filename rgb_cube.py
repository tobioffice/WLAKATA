# -*- coding: utf-8 -*-
import cv2
import numpy as np


def create_color_mask(img, color_values, tolerance=15):
    """Create a mask for specific RGB values with tolerance"""
    mask = None
    for rgb in color_values:
        # Convert RGBA to BGR (OpenCV format)
        bgr = (rgb[2], rgb[1], rgb[0])

        # Create range with tolerance
        lower = np.array([max(0, val - tolerance) for val in bgr])
        upper = np.array([min(255, val + tolerance) for val in bgr])

        # Create mask for this color value
        current_mask = cv2.inRange(img, lower, upper)

        # Combine masks
        if mask is None:
            mask = current_mask
        else:
            mask = cv2.bitwise_or(mask, current_mask)

    return mask


def filter_color(image_path, color):
    # Read the image
    img = cv2.imread(image_path)

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

    if color.lower() not in color_values:
        raise ValueError("Color must be 'red', 'green', or 'blue'")

    # Create mask for the selected color using exact values
    mask = create_color_mask(img, color_values[color.lower()])

    # Convert mask to 3 channels
    mask_3channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Create inverted mask for non-selected regions
    inv_mask = cv2.bitwise_not(mask_3channel)

    # Convert masks to float32 for multiplication
    mask_3channel = mask_3channel.astype(np.float32) / 255.0
    inv_mask = inv_mask.astype(np.float32) / 255.0

    # Create the result by combining original and darkened parts
    selected_region = img.astype(np.float32) * mask_3channel
    darkened_region = img.astype(np.float32) * inv_mask * 0.1

    # Combine the regions
    result = selected_region + darkened_region

    # Convert back to uint8
    result = result.astype(np.uint8)

    return result


def main():
    image_path = 'rgb_cubes.jpg'

    # Get color input from user
    print("Enter color to preserve (red/green/blue):")
    color = input().strip().lower()

    try:
        # Process the image
        result = filter_color(image_path, color)

        # Show original image
        cv2.imshow('Original', cv2.imread(image_path))

        # Show filtered image
        cv2.imshow(f'Filtered - {color}', result)

        # Wait for key press and close windows
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Save the result
        output_path = f'filtered_{color}.jpg'
        cv2.imwrite(output_path, result)
        print(f"Result saved as {output_path}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
