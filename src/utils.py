import cv2
import numpy as np


def order_points(points):
    """
    Sorts 4 coordinate points into a consistent order:
    [Top-Left, Top-Right, Bottom-Right, Bottom-Left].

    This is crucial for applying perspective transforms correctly.

    Args:
        points (numpy.ndarray): An array of 4 points, each with (x, y) coordinates.

    Returns:
        numpy.ndarray: The sorted array of 4 points.
    """
    # Initialize a 4x2 array to store the sorted points
    rect = np.zeros((4, 2), dtype="float32")

    # The sum of (x + y) is smallest for the top-left point and largest for the bottom-right point.
    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]  # Top-Left
    rect[2] = points[np.argmax(s)]  # Bottom-Right

    # The difference (y - x) is smallest for the top-right and largest for the bottom-left.
    # Note: np.diff calculates the difference between adjacent elements.
    # Here, we calculate y - x for each point.
    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]  # Top-Right
    rect[3] = points[np.argmax(diff)]  # Bottom-Left

    return rect


def four_point_transform(image, points):
    """
    Performs a perspective warp: crops the region defined by 4 points and straightens it.

    This function takes an image and a set of four points defining a quadrilateral,
    then transforms the perspective to make that quadrilateral a rectangle.

    Args:
        image (numpy.ndarray): The source image.
        points (numpy.ndarray): The 4 points defining the quadrilateral to be warped.

    Returns:
        numpy.ndarray: The warped, rectangular image.
    """
    # Sort the points into a consistent order
    rect = order_points(points)
    (tl, tr, br, bl) = rect

    # Calculate the width of the new image (the maximum of the top and bottom edges)
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width_a), int(width_b))

    # Calculate the height of the new image (the maximum of the left and right edges)
    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(height_a), int(height_b))

    # Define the 4 destination points for the new, rectangular image
    destination_points = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]], dtype="float32")

    # Compute the perspective transform matrix and apply it
    transform_matrix = cv2.getPerspectiveTransform(rect, destination_points)
    warped_image = cv2.warpPerspective(image, transform_matrix, (max_width, max_height))

    return warped_image


def scale_contour(contour, scale):
    """
    Scales a contour by a given factor.

    The scale factor can be a single float (uniform scaling) or a tuple (non-uniform scaling).

    Args:
        contour (numpy.ndarray): The contour to be scaled.
        scale (float or tuple): The scaling factor(s) for x and y axes.

    Returns:
        numpy.ndarray: The scaled contour.
    """
    # Determine if the scale is uniform or non-uniform
    if isinstance(scale, (int, float)):
        scale_x, scale_y = scale, scale
    else:
        scale_x, scale_y = scale

    # Create a copy of the contour to avoid modifying the original
    scaled_contour = contour.copy().astype(np.float32)

    # Apply the scaling factors to the x and y coordinates
    scaled_contour[:, :, 0] *= scale_x
    scaled_contour[:, :, 1] *= scale_y

    # Convert the coordinates back to integers
    return scaled_contour.astype(np.int32)


def get_outside_of_contour(image, contour):
    """
    Extracts the area outside the given contour from an image.

    This function creates a mask from the contour, inverts it, and then applies
    it to the original image to black out the area inside the contour,
    effectively isolating the part of the image outside of it.

    Args:
        image (numpy.ndarray): The source image.
        contour (numpy.ndarray): The contour defining the 'inside' area.

    Returns:
        numpy.ndarray: An image containing only the area outside the contour.
    """
    # Create a black mask with the same dimensions as the image
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    # Draw the filled contour on the mask in white
    cv2.drawContours(mask, [contour], -1, (255), -1)

    # Invert the mask, so the area outside the contour is white and inside is black
    mask_inv = cv2.bitwise_not(mask)

    # Apply the inverted mask to the original image
    # This keeps the pixels where the mask is white (outside) and blacks out the rest
    outside_image = cv2.bitwise_and(image, image, mask=mask_inv)

    return outside_image
