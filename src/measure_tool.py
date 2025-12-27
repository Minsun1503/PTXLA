import cv2
import json
import numpy as np
from src import pre_processing
from src import config
from src import utils

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

def get_coordinates_from_user_selection(file_path, coord_save_path):
    """
    Opens an interactive window to guide the user through a two-phase selection process:
    1. Select 2 anchor points for the answer bubble area on the main warped document.
    2. Select 2 anchor points for the OCR information area on the 'outside' image.

    Saves the coordinates to a JSON file.

    Returns:
        tuple: (bubble_anchors, ocr_regions_dict, warped_image, outside_image)
    """
    # --- Step 1: Get the warped image and the outside area from the file ---
    file_type = utils.get_file_type(file_path)
    if file_type == 'pdf':
        warped_standard, outside_image = pre_processing.get_warped_image_from_pdf(file_path, config.STANDARD_SIZE)
    elif file_type in ['png', 'jpg', 'jpeg']:
        warped_standard, outside_image = pre_processing.get_warped_image_from_image(file_path, config.STANDARD_SIZE)
    else:
        print(f"Unsupported file type for coordinate selection: {file_type}")
        return [], {}, None, None

    if warped_standard is None or outside_image is None:
        print("Failed to process the document from the file.")
        return [], {}, None, None

    # --- Phase 1: Select Bubble Sheet Anchor Points on the Warped Image ---
    p1_h, p1_w = warped_standard.shape[:2]
    p1_display_scale = p1_w / config.DISPLAY_WIDTH # Scale width to 1200px for display
    p1_display_w = config.DISPLAY_WIDTH
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
    p2_display_scale = p2_w / config.DISPLAY_WIDTH # Scale width to 1200px for display
    p2_display_w = config.DISPLAY_WIDTH
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
        ocr_regions[config.KEY_INFO_BLOCK] = [x, y, w, h]
        print(f"  > Created OCR region '{config.KEY_INFO_BLOCK}' at [{x}, {y}, {w}, {h}]")

    final_data = {
        config.KEY_BUBBLE_ANCHORS: captured_bubble_anchors,
        config.KEY_OCR_REGIONS: ocr_regions
    }
    print(f"\n--> Saving coordinates to {coord_save_path}")
    try:
        with open(coord_save_path, 'w') as f:
            json.dump(final_data, f, indent=4)
    except Exception as e:
        print(f"Error saving coordinates: {e}")
        return [], {}, None, None

    return captured_bubble_anchors, ocr_regions, warped_standard, outside_image
