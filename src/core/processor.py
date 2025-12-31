import cv2
import numpy as np
from pdf2image import convert_from_path
from typing import Tuple

from src.utils import image_utils
from config import Config

def _preprocess_for_contour_finding(image: np.ndarray, cfg: Config.ImageProcessingConfig) -> np.ndarray:
    """
    Converts an image to a Canny Edge representation for contour detection.
    
    Args:
        image (np.ndarray): The input color image.
        cfg (Config.ImageProcessingConfig): Image processing configuration.

    Returns:
        np.ndarray: The binary image with detected edges.
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 1)
    edges = cv2.Canny(blurred_image, cfg.CANNY_THRESHOLD_1, cfg.CANNY_THRESHOLD_2)
    return edges

def _find_document_contour(edges: np.ndarray, cfg: Config.ImageProcessingConfig) -> np.ndarray | None:
    """
    Finds the largest contour with four vertices, assuming it is the document sheet.

    Args:
        edges (np.ndarray): The input edge-detected image.
        cfg (Config.ImageProcessingConfig): Image processing configuration.

    Returns:
        The contour of the document with 4 points, or None if not found.
    """
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    for c in contours:
        perimeter = cv2.arcLength(c, True)
        approx_polygon = cv2.approxPolyDP(c, cfg.CONTOUR_APPROX_EPSILON * perimeter, True)
        if len(approx_polygon) == 4:
            return approx_polygon
    return None

def process_and_warp_image(original_image: np.ndarray, cfg: Config.ImageProcessingConfig) -> Tuple[np.ndarray, np.ndarray] | Tuple[None, None]:
    """
    Finds the document in an image, warps it, and returns the warped doc and the area outside it.

    Args:
        original_image (np.ndarray): The input image to process.
        cfg (Config.ImageProcessingConfig): Image processing configuration.

    Returns:
        A tuple of (warped_image, outside_image), or (None, None) on failure.
    """
    h_orig, w_orig = original_image.shape[:2]
    
    # Resize for faster processing
    process_height = cfg.PROCESSING_RESIZE_HEIGHT
    process_width = int(process_height * w_orig / h_orig)
    processing_image = cv2.resize(original_image, (process_width, process_height))

    edges = _preprocess_for_contour_finding(processing_image, cfg)
    doc_contour = _find_document_contour(edges, cfg)

    if doc_contour is not None:
        # Scale contour points back to the original image size
        scale_x = w_orig / process_width
        scale_y = h_orig / process_height
        scaled_doc_contour = doc_contour.copy().astype(np.float32)
        scaled_doc_contour[:, 0, 0] *= scale_x
        scaled_doc_contour[:, 0, 1] *= scale_y
        scaled_doc_contour = scaled_doc_contour.astype(int)

        outside_image = image_utils.get_outside_of_contour(original_image, scaled_doc_contour)
        warped_image = image_utils.four_point_transform(original_image, scaled_doc_contour.reshape(4, 2))
        warped_standard = cv2.resize(warped_image, cfg.STANDARD_SIZE)
        
        return warped_standard, outside_image
    else:
        print("Could not find the document frame in the image.")
        return None, None

def get_image_from_pdf(pdf_path: str) -> np.ndarray | None:
    """
    Loads the first page of a PDF and converts it to an OpenCV image.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        The image as a numpy array, or None on failure.
    """
    try:
        images = convert_from_path(pdf_path)
        if not images:
            print(f"Error: No images found in PDF: {pdf_path}")
            return None
        return cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None

def get_image_from_file(image_path: str) -> np.ndarray | None:
    """
    Loads an image from a standard image file.

    Args:
        image_path (str): The path to the image file.

    Returns:
        The image as a numpy array, or None on failure.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found or could not be read at {image_path}")
        return image
    except Exception as e:
        print(f"Error reading image {image_path}: {e}")
        return None
