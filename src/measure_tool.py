import cv2
import numpy as np
import time
from src import utils, pre_processing
from pdf2image import convert_from_path

# --- Constants ---
# The standard size for the warped image, for consistent coordinate systems.
STANDARD_SIZE = (1000, 1400)
# The height of the display window for the interactive coordinate selection.
DISPLAY_HEIGHT = 700


def mouse_click_callback(event, x, y, flags, param):
    """
    Callback function to handle mouse click events for coordinate selection.

    Args:
        event (int): The type of mouse event (e.g., cv2.EVENT_LBUTTONDOWN).
        x (int): The x-coordinate of the mouse click in the display window.
        y (int): The y-coordinate of the mouse click in the display window.
        flags (int): Additional flags from OpenCV.
        param (dict): A dictionary containing data passed to the callback,
                      including the display image, scaling factor, and coordinate list.
    """
    # The dictionary passed from setMouseCallback
    data = param

    # If the left mouse button is clicked
    if event == cv2.EVENT_LBUTTONDOWN:
        # Scale the clicked (x, y) coordinates back to the original image size
        real_x = int(x * data['scale'])
        real_y = int(y * data['scale'])

        print(f"👉 Point selected: ({real_x}, {real_y})")

        # Append the real coordinates to the results list
        data['coords'].append((real_x, real_y))

        # Draw a circle and number on the display image to give feedback to the user
        cv2.circle(data['img'], (x, y), 5, (0, 0, 255), -1)
        cv2.putText(data['img'], str(len(data['coords'])), (x + 10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Refresh the display window to show the new point
        cv2.imshow("Coordinate Selection", data['img'])


def get_coordinates_from_image(pdf_path):
    """
    Opens an interactive window to let the user click and select two anchor points.

    This function performs the following steps:
    1. Converts the first page of a PDF to an image.
    2. Pre-processes the image to find the document contour.
    3. Warps and standardizes the document image.
    4. Displays the image and waits for the user to select two points.
    5. Automatically closes the window 3 seconds after two points are selected.

    Returns:
        tuple: A tuple containing:
            - list: The list of selected (x, y) coordinates.
            - numpy.ndarray: The warped and standardized image.
    """
    try:
        # Convert PDF to a list of images
        images = convert_from_path(pdf_path)
        # Convert the first page (PIL image) to an OpenCV BGR image
        original_image = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return [], None

    # --- IMAGE PRE-PROCESSING ---
    h_orig, w_orig = original_image.shape[:2]
    # Resize for faster processing
    process_height = 800
    process_width = int(process_height * w_orig / h_orig)
    processing_image = cv2.resize(original_image, (process_width, process_height))

    # Find edges and the document contour
    edges = pre_processing.preprocess_image(processing_image)
    doc_contour = pre_processing.find_document_contour(edges)

    captured_coords = []
    warped_standard = None  # Initialize to None

    if doc_contour is not None:
        # --- SCALING AND WARPING ---
        # Calculate scaling factors to map contour points back to the original image size
        scale_x = w_orig / process_width
        scale_y = h_orig / process_height

        # Scale the contour points
        scaled_doc_contour = doc_contour.copy().astype(np.float32)
        scaled_doc_contour[:, 0, 0] *= scale_x
        scaled_doc_contour[:, 0, 1] *= scale_y

        # Apply four-point perspective transform to get the top-down view of the document
        warped_image = utils.four_point_transform(original_image, scaled_doc_contour.reshape(4, 2))
        # Resize the warped image to a standard size for consistency
        warped_standard = cv2.resize(warped_image, STANDARD_SIZE)

        # --- SETUP INTERACTIVE DISPLAY ---
        # Calculate scaling for the display window
        display_scale = STANDARD_SIZE[1] / DISPLAY_HEIGHT
        display_width = int(STANDARD_SIZE[0] / display_scale)
        # Resize the standard warped image for display
        display_image = cv2.resize(warped_standard, (display_width, DISPLAY_HEIGHT))

        print("\n--- PLEASE CLICK TO SELECT 2 POINTS (e.g., bubble 1A and 20D) ---")

        cv2.imshow("Coordinate Selection", display_image)

        # Data to be passed to the mouse callback function
        callback_data = {
            'img': display_image,
            'scale': display_scale,
            'coords': captured_coords
        }

        # Set the mouse callback function for the window
        cv2.setMouseCallback("Coordinate Selection", mouse_click_callback, callback_data)

        # --- WAIT LOOP for user input ---
        start_wait_time = None
        while True:
            # Refresh the display window (to show drawn points)
            cv2.imshow("Coordinate Selection", display_image)
            key = cv2.waitKey(100) & 0xFF  # Wait 100ms for a key press

            # If two points have been selected
            if len(captured_coords) >= 2:
                if start_wait_time is None:
                    print("--> 2 points selected. Closing automatically in 3 seconds...")
                    start_wait_time = time.time()

                # Check if 3 seconds have passed
                if time.time() - start_wait_time >= 3:
                    break

            # Allow manual exit with 'q' or ESC key
            if key == ord('q') or key == 27:
                print("--> Manual exit.")
                break

        cv2.destroyAllWindows()
    else:
        print("Could not find the document frame.")
        return [], None

    # Return the captured coordinates and the standardized warped image
    return captured_coords, warped_standard

