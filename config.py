import os

class Config:
    """
    Centralized configuration class for the OMR/OCR grading application.
    This class holds all parameters, paths, and settings to ensure a single
    source of truth and to avoid magic numbers in the core logic.
    """

    def __init__(self):
        # Define the project root as the directory containing this config file.
        self.PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

        # --- PATHS ---
        self.Paths = self.PathsConfig(self.PROJECT_ROOT)

        # --- BATCH PROCESSING ---
        self.Batch = self.BatchConfig()

        # --- IMAGE PROCESSING ---
        self.ImageProcessing = self.ImageProcessingConfig()

        # --- OMR LOGIC ---
        self.OMR = self.OMRConfig()

        # --- OCR LOGIC ---
        self.OCR = self.OCRConfig()

        # --- UI & DISPLAY ---
        self.UI = self.UIConfig()

        # --- JSON KEYS ---
        self.JSON = self.JSONConfig()

    class PathsConfig:
        """Configuration for all file and directory paths."""
        def __init__(self, root):
            self.PDF_PATH: str = os.path.join(root, "data/raw/Mau_de_thi_co_dap_an.pdf")
            self.OUTPUT_PATH: str = os.path.join(root, "output/")
            self.ANSWER_KEY_PATH: str = os.path.join(root, "data/answer/answer_key.csv")
            self.COORDINATES_PATH: str = os.path.join(root, "data/template/", "coordinates.json")
            self.BATCH_INPUT_DIR: str = os.path.join(root, "data/raw/batch_input/")
            self.BATCH_OUTPUT_DIR: str = os.path.join(root, "output/batch_output/")
            
            self.SCORING_RESULT_IMAGE_NAME: str = "scoring_result.png"
            self.SCORE_IMAGE_NAME: str = "score.png"
            self.OUTSIDE_AREA_IMAGE_NAME: str = "outside_area.png"
            self.OCR_RESULT_JSON_NAME: str = "ocr_results.json"

    class BatchConfig:
        """Configuration for batch processing mode."""
        BATCH_MODE: bool = True

    class ImageProcessingConfig:
        """Parameters for image pre-processing and manipulation."""
        STANDARD_SIZE: tuple[int, int] = (1000, 1400)
        PROCESSING_RESIZE_HEIGHT: int = 800
        CANNY_THRESHOLD_1: int = 75
        CANNY_THRESHOLD_2: int = 200
        CONTOUR_APPROX_EPSILON: float = 0.02

    class OMRConfig:
        """Parameters for the Optical Mark Recognition (OMR) logic."""
        NUM_QUESTIONS_PER_COLUMN: int = 20
        NUM_CHOICES_PER_QUESTION: int = 4
        SCAN_RADIUS: int = 12
        PIXEL_THRESHOLD: int = 150
        ANSWER_MAP: dict[str, int] = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

    class OCRConfig:
        """Parameters for the Optical Character Recognition (OCR) logic."""
        OCR_LANGUAGES: list[str] = ['vi', 'en']
        ALLOW_LIST: str = '0123456789'

    class UIConfig:
        """Parameters for UI elements and display settings."""
        DISPLAY_WIDTH: int = 800
        DISPLAY_HEIGHT: int = 700

    class JSONConfig:
        """Keys used for serialization and deserialization of JSON data."""
        KEY_BUBBLE_ANCHORS: str = "bubble_anchors"
        KEY_OCR_REGIONS: str = "ocr_regions"
        KEY_INFO_BLOCK: str = "info_block"
