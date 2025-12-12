import cv2
import numpy as np

def preprocess_image(image):
    """
    Converts the original image to a Canny Edge image.

    This function takes a color image, converts it to grayscale, applies Gaussian blur
    to reduce noise, and then uses the Canny algorithm to detect edges.

    Args:
        image (numpy.ndarray): The input color image (in BGR format).

    Returns:
        numpy.ndarray: The resulting binary image with detected edges.
    """
    # 1. Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 2. Apply Gaussian blur to reduce noise (important for edge detection)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 1)

    # 3. Perform Canny edge detection
    # The thresholds 75-200 are often effective for white paper on a dark background.
    edges = cv2.Canny(blurred_image, 75, 200)

    return edges


def find_document_contour(edges):
    """
    Finds the largest contour with four vertices, assuming it is the document sheet.

    This function searches through all contours found in the edge image, sorts them
    by area in descending order, and identifies the first one that approximates
    to a 4-sided polygon.

    Args:
        edges (numpy.ndarray): The input edge-detected image.

    Returns:
        numpy.ndarray: The contour of the document with 4 points, or None if not found.
    """
    # Find all contours in the edge image
    # cv2.RETR_EXTERNAL retrieves only the extreme outer contours
    # cv2.CHAIN_APPROX_SIMPLE compresses horizontal, vertical, and diagonal segments
    # and leaves only their end points.
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area in descending order (the document is usually the largest object)
    if contours:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        # Iterate through the sorted contours
        for c in contours:
            # Calculate the perimeter of the contour
            perimeter = cv2.arcLength(c, True)

            # Approximate the contour to a polygon
            # This simplifies the contour by reducing the number of vertices
            # The 0.02 * perimeter is a threshold for the approximation accuracy
            approx_polygon = cv2.approxPolyDP(c, 0.02 * perimeter, True)

            # If the approximated contour has 4 vertices, we assume it's the rectangular document
            if len(approx_polygon) == 4:
                return approx_polygon

    return None  # Return None if no 4-sided contour is found

