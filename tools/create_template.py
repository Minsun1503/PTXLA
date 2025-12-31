import cv2
import json
import numpy as np
import os
import sys

# Add the project root directory to the Python path
# This allows us to import modules from the 'src' and 'config' directories
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.core import processor
from src.utils import image_utils, file_io
import config


def anchor_point_callback(event, x, y, flags, param):
    """
    Callback to capture up to two anchor points from a mouse click.
    Draws a circle and number for each selected point.
    """
    data = param
    max_points = data.get("max_points", 2)
    
    if event == cv2.EVENT_LBUTTONDOWN and len(data['coords']) < max_points:
        # Convert display coordinates back to real image coordinates
        real_x, real_y = int(x * data['scale']), int(y * data['scale'])
        print(f"👉 Anchor point {len(data['coords']) + 1} selected: ({real_x}, {real_y})")
        
        # Store the real coordinates
        data['coords'].append((real_x, real_y))
        
        # Draw feedback on the display image
        cv2.circle(data['img'], (x, y), 5, (0, 0, 255), -1)
        cv2.putText(data['img'], str(len(data['coords'])), (x + 10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imshow(data["window_name"], data['img'])

def get_coordinates_from_user_selection(file_path: str, coord_save_path: str, cfg: config.Config):
    """
    Opens an interactive window to guide the user through a two-phase selection process:
    1. Select 2 anchor points for the answer bubble area on the main warped document.
    2. Select 2 anchor points for the OCR information area on the 'outside' image.

    Saves the coordinates to a JSON file.

    Args:
        file_path (str): The path to the template file (PDF or image).
        coord_save_path (str): The path to save the output JSON file.
        cfg (config.Config): The application configuration object.

    Returns:
        tuple: (bubble_anchors, ocr_regions_dict, warped_image, outside_image)
    """
    # --- Step 1: Get the warped image and the outside area from the file ---
    file_type = file_io.get_file_type(file_path)
    if file_type == 'pdf':
        original_image = processor.get_image_from_pdf(file_path)
    elif file_type in ['png', 'jpg', 'jpeg']:
        original_image = processor.get_image_from_file(file_path)
    else:
        print(f"Unsupported file type for coordinate selection: {file_type}")
        return [], {}, None, None

    if original_image is None:
        print(f"Failed to load image from {file_path}.")
        return [], {}, None, None

    warped_standard, outside_image = processor.process_and_warp_image(original_image, cfg.ImageProcessing)

    if warped_standard is None or outside_image is None:
        print("Failed to process the document from the file.")
        return [], {}, None, None

    # --- Phase 1: Select Bubble Sheet Anchor Points on the Warped Image ---
    p1_h, p1_w = warped_standard.shape[:2]
    p1_display_w = cfg.UI.DISPLAY_WIDTH
    p1_display_scale = p1_w / p1_display_w
    p1_display_h = int(p1_h / p1_display_scale)
    
    display_image_phase1 = cv2.resize(warped_standard, (p1_display_w, p1_display_h))
    window_name_p1 = "Phase 1: Select Answer Area Anchors"
    cv2.imshow(window_name_p1, display_image_phase1)
    cv2.setWindowTitle(window_name_p1, "Phase 1: Select 2 anchors for the ANSWER BUBBLE area (e.g., top-left and bottom-right bubble)")
    
    captured_bubble_anchors = []
    callback_data_p1 = {
        'img': display_image_phase1,
        'scale': p1_display_scale,
        'coords': captured_bubble_anchors,
        "window_name": window_name_p1
    }
    cv2.setMouseCallback(window_name_p1, anchor_point_callback, callback_data_p1)

    print("\n--- PHASE 1: ANSWER AREA ANCHORS ---")
    print("Please click to select 2 anchor points for the bubble sheet area (e.g., bubble 1A and the last bubble).")
    while len(captured_bubble_anchors) < 2:
        cv2.waitKey(1)
    
    print("--> Answer area anchors selected.")
    cv2.destroyWindow(window_name_p1)

    # --- Phase 2: Select OCR Information Area Anchors on the Outside Image ---
    p2_h, p2_w = outside_image.shape[:2]
    p2_display_w = cfg.UI.DISPLAY_WIDTH
    p2_display_scale = p2_w / p2_display_w
    p2_display_h = int(p2_h / p2_display_scale)

    display_image_phase2 = cv2.resize(outside_image, (p2_display_w, p2_display_h))
    window_name_p2 = "Phase 2: Select Info Area Anchors"
    cv2.imshow(window_name_p2, display_image_phase2)
    cv2.setWindowTitle(window_name_p2, "Phase 2: Select 2 anchors on the OUTSIDE IMAGE for the info area (e.g., top-left and bottom-right)")
    
    captured_ocr_anchors = []
    callback_data_p2 = {
        'img': display_image_phase2,
        'scale': p2_display_scale,
        'coords': captured_ocr_anchors,
        "window_name": window_name_p2
    }
    cv2.setMouseCallback(window_name_p2, anchor_point_callback, callback_data_p2)
    
    print("\n--- PHASE 2: OCR INFORMATION AREA (ON OUTSIDE IMAGE) ---")
    print("Please click to select 2 anchor points to define the OCR region (top-left and bottom-right corners).")
    while len(captured_ocr_anchors) < 2:
        cv2.waitKey(1)
        
    print("--> OCR area anchors selected.")
    cv2.destroyWindow(window_name_p2)

    # --- Step 3: Process OCR anchors and Save Data ---
    ocr_regions = {}
    if len(captured_ocr_anchors) == 2:
        p1, p2 = captured_ocr_anchors
        x = min(p1[0], p2[0])
        y = min(p1[1], p2[1])
        w = abs(p1[0] - p2[0])
        h = abs(p1[1] - p2[1])
        ocr_regions[cfg.JSON.KEY_INFO_BLOCK] = [x, y, w, h]
        print(f"  > Created OCR region '{cfg.JSON.KEY_INFO_BLOCK}' at [{x}, {y}, {w}, {h}]")

    final_data = {
        cfg.JSON.KEY_BUBBLE_ANCHORS: captured_bubble_anchors,
        cfg.JSON.KEY_OCR_REGIONS: ocr_regions
    }
    
    file_io.save_json(final_data, coord_save_path)

    return captured_bubble_anchors, ocr_regions, warped_standard, outside_image

if __name__ == '__main__':
    """
    Main entry point for the template creation tool.
    """
    print("--- Starting Coordinate and Region Definition Tool ---")
    
    # Load configuration
    cfg = config.Config()
    
    # Define the path to the template file. You can change this to point to your template.
    template_file = cfg.Paths.PDF_PATH 
    
    print(f"Using template file: {template_file}")
    
    # Run the interactive selection process
    get_coordinates_from_user_selection(
        file_path=template_file,
        coord_save_path=cfg.Paths.COORDINATES_PATH,
        cfg=cfg
    )
    
    print("\n--- Coordinate setup complete! ---")
    print(f"Data saved to: {cfg.Paths.COORDINATES_PATH}")
