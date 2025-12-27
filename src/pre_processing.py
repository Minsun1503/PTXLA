import cv2
import numpy as np
from pdf2image import convert_from_path
from src import utils
from src import config


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
    edges = cv2.Canny(blurred_image, config.CANNY_THRESHOLD_1, config.CANNY_THRESHOLD_2)

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
            approx_polygon = cv2.approxPolyDP(c, config.CONTOUR_APPROX_EPSILON * perimeter, True)

            # If the approximated contour has 4 vertices, we assume it's the rectangular document
            if len(approx_polygon) == 4:
                return approx_polygon

    return None  # Return None if no 4-sided contour is found


def get_warped_image_from_pdf(pdf_path, standard_size):
    """
    Loads an image from a PDF, finds the document, warps it, and returns both
    the warped document and the area outside of it.

    Args:
        pdf_path (str): The path to the PDF file.
        standard_size (tuple): The (width, height) to resize the final warped image to.

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]: A tuple containing:
            - The processed and standardized document image.
            - The image of the area outside the document.
        Returns (None, None) on failure.
    """
    try:
        # Convert PDF to a list of images
        images = convert_from_path(pdf_path)
        # Convert the first page (PIL image) to an OpenCV BGR image
        original_image = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None, None

    # --- IMAGE PRE-PROCESSING ---
    h_orig, w_orig = original_image.shape[:2]
    # Resize for faster processing
    process_height = config.PROCESSING_RESIZE_HEIGHT
    process_width = int(process_height * w_orig / h_orig)
    processing_image = cv2.resize(original_image, (process_width, process_height))

    # Find edges and the document contour using existing functions
    edges = preprocess_image(processing_image)
    doc_contour = find_document_contour(edges)

    if doc_contour is not None:
        # --- SCALING AND WARPING ---
        # Calculate scaling factors to map contour points back to the original image size
        scale_x = w_orig / process_width
        scale_y = h_orig / process_height

        # Scale the contour points
        scaled_doc_contour = doc_contour.copy().astype(np.float32)
        scaled_doc_contour[:, 0, 0] *= scale_x
        scaled_doc_contour[:, 0, 1] *= scale_y

        # Get the area outside the document before warping
        outside_image = utils.get_outside_of_contour(original_image, scaled_doc_contour.astype(int))

        # Apply four-point perspective transform to get the top-down view of the document
        warped_image = utils.four_point_transform(original_image, scaled_doc_contour.reshape(4, 2))
        # Resize the warped image to a standard size for consistency
        warped_standard = cv2.resize(warped_image, standard_size)

        return warped_standard, outside_image
    else:
        print("Could not find the document frame in the PDF.")
        return None, None


def get_warped_image_from_image(image_path, standard_size):
    """
    Loads an image from a file, finds the document, warps it, and returns both
    the warped document and the area outside of it.

    Args:
        image_path (str): The path to the image file.
        standard_size (tuple): The (width, height) to resize the final warped image to.

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]: A tuple containing:
            - The processed and standardized document image.
            - The image of the area outside the document.
        Returns (None, None) on failure.
    """
    try:
        original_image = cv2.imread(image_path)
        if original_image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
    except Exception as e:
        print(f"Error reading image: {e}")
        return None, None

    # --- IMAGE PRE-PROCESSING ---
    h_orig, w_orig = original_image.shape[:2]
    # Resize for faster processing
    process_height = config.PROCESSING_RESIZE_HEIGHT
    process_width = int(process_height * w_orig / h_orig)
    processing_image = cv2.resize(original_image, (process_width, process_height))

    # Find edges and the document contour using existing functions
    edges = preprocess_image(processing_image)
    doc_contour = find_document_contour(edges)

    if doc_contour is not None:
        # --- SCALING AND WARPING ---
        # Calculate scaling factors to map contour points back to the original image size
        scale_x = w_orig / process_width
        scale_y = h_orig / process_height

        # Scale the contour points
        scaled_doc_contour = doc_contour.copy().astype(np.float32)
        scaled_doc_contour[:, 0, 0] *= scale_x
        scaled_doc_contour[:, 0, 1] *= scale_y

        # Get the area outside the document before warping
        outside_image = utils.get_outside_of_contour(original_image, scaled_doc_contour.astype(int))

        # Apply four-point perspective transform to get the top-down view of the document
        warped_image = utils.four_point_transform(original_image, scaled_doc_contour.reshape(4, 2))
        # Resize the warped image to a standard size for consistency
        warped_standard = cv2.resize(warped_image, standard_size)

        return warped_standard, outside_image
    else:
        print("Could not find the document frame in the image.")
        return None, None
