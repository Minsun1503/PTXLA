import cv2
import easyocr
import re
import numpy as np
from typing import Dict, List, Tuple

from config import Config

class OCREngine:
    """
    Handles the core Optical Character Recognition (OCR) logic for extracting text.
    """

    def __init__(self, ocr_config: Config.OCRConfig):
        """
        Initializes the OCR engine, which includes loading the EasyOCR model.

        Args:
            ocr_config (Config.OCRConfig): The OCR configuration object.
        """
        print("Initializing EasyOCR reader... (This may take a moment on first run)")
        self.reader = easyocr.Reader(ocr_config.OCR_LANGUAGES)
        self.cfg = ocr_config
        print("EasyOCR reader initialized.")

    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Applies pre-processing steps to an image ROI to improve OCR accuracy.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Using Otsu's thresholding can be very effective for OCR.
        processed_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        return processed_image

    def extract_text_from_regions(self, image: np.ndarray, ocr_regions: Dict[str, List[int]]) -> Dict[str, str]:
        """
        Extracts text from specified regions of an image.

        Args:
            image (np.ndarray): The image to extract text from (e.g., the 'outside' image).
            ocr_regions (Dict): A dictionary where keys are region names and values
                                are [x, y, w, h] coordinates for the ROIs.

        Returns:
            A dictionary where keys are region names and values are extracted text.
        """
        if not ocr_regions:
            print("--> No OCR regions defined. Skipping text extraction.")
            return {}

        print("\n--> Starting OCR text extraction...")
        extracted_data = {}

        for region_name, coords in ocr_regions.items():
            if len(coords) != 4:
                print(f"  - Warning: Invalid coordinates for region '{region_name}'. Skipping.")
                continue

            x, y, w, h = coords
            roi = image[y:y+h, x:x+w]

            if roi.size == 0:
                print(f"  - Warning: Region '{region_name}' is empty. Skipping.")
                extracted_data[region_name] = ""
                continue

            processed_roi = self._preprocess_for_ocr(roi)
            
            ocr_result = self.reader.readtext(
                processed_roi,
                detail=0,
                paragraph=True,
                allowlist=self.cfg.ALLOW_LIST
            )

            if ocr_result:
                full_text = ' '.join(ocr_result)
                full_text = re.sub(r'\s+', ' ', full_text).strip()
                extracted_data[region_name] = full_text
                print(f"  - Region '{region_name}': Extracted text = '{full_text}'")
            else:
                extracted_data[region_name] = ""
                print(f"  - Region '{region_name}': No text found.")
        
        return extracted_data
