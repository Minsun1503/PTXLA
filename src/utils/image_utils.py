import cv2
import numpy as np
from typing import Tuple

def order_points(points: np.ndarray) -> np.ndarray:
    """
    Sorts 4 coordinate points into a consistent order:
    [Top-Left, Top-Right, Bottom-Right, Bottom-Left].

    Args:
        points (np.ndarray): An array of 4 points, each with (x, y) coordinates.

    Returns:
        np.ndarray: The sorted array of 4 points.
    """
    rect = np.zeros((4, 2), dtype="float32")
    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]
    rect[2] = points[np.argmax(s)]
    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]
    rect[3] = points[np.argmax(diff)]
    return rect

def four_point_transform(image: np.ndarray, points: np.ndarray) -> np.ndarray:
    """
    Performs a perspective warp on an image.

    Args:
        image (np.ndarray): The source image.
        points (np.ndarray): The 4 points defining the quadrilateral to be warped.

    Returns:
        np.ndarray: The warped, rectangular image.
    """
    rect = order_points(points)
    (tl, tr, br, bl) = rect
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width_a), int(width_b))
    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(height_a), int(height_b))
    destination_points = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]], dtype="float32")
    transform_matrix = cv2.getPerspectiveTransform(rect, destination_points)
    warped_image = cv2.warpPerspective(image, transform_matrix, (max_width, max_height))
    return warped_image

def scale_contour(contour: np.ndarray, scale: float | Tuple[float, float]) -> np.ndarray:
    """
    Scales a contour by a given factor.

    Args:
        contour (np.ndarray): The contour to be scaled.
        scale (float or tuple): The scaling factor(s) for x and y axes.

    Returns:
        np.ndarray: The scaled contour.
    """
    if isinstance(scale, (int, float)):
        scale_x, scale_y = scale, scale
    else:
        scale_x, scale_y = scale
    scaled_contour = contour.copy().astype(np.float32)
    scaled_contour[:, :, 0] *= scale_x
    scaled_contour[:, :, 1] *= scale_y
    return scaled_contour.astype(np.int32)

def get_outside_of_contour(image: np.ndarray, contour: np.ndarray) -> np.ndarray:
    """
    Extracts the area outside the given contour from an image.

    Args:
        image (np.ndarray): The source image.
        contour (np.ndarray): The contour defining the 'inside' area.

    Returns:
        np.ndarray: An image containing only the area outside the contour.
    """
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, (255), -1)
    mask_inv = cv2.bitwise_not(mask)
    outside_image = cv2.bitwise_and(image, image, mask=mask_inv)
    return outside_image
