import os

# --- PATHS ---
# Input PDF file
PDF_PATH = "data/raw/Mau_de_thi_co_dap_an.pdf"

# Directory to save all output files
OUTPUT_PATH = "output/"

# Path to the CSV file containing the correct answers
ANSWER_KEY_PATH = "data/answer/answer_key.csv"

# Path to the JSON file where anchor coordinates are stored
COORDINATES_PATH = os.path.join("data/template/", "coordinates.json")

# Output file names
SCORING_RESULT_IMAGE_NAME = "scoring_result.png"
SCORE_IMAGE_NAME = "score.png"
OUTSIDE_AREA_IMAGE_NAME = "outside_area.png"
OCR_RESULT_JSON_NAME = "ocr_results.json"


# --- IMAGE PROCESSING ---
# Standard size of the sheet after warping.
# All coordinates are based on this standardized size to ensure consistency.
STANDARD_SIZE = (1000, 1400)


# --- PRE-PROCESSING PARAMETERS ---
# The height to which the image is resized for processing (finding the document contour).
# A smaller size like 800px makes processing faster.
PROCESSING_RESIZE_HEIGHT = 800

# Canny edge detection thresholds.
# Lower values detect more edges, higher values detect stronger edges.
CANNY_THRESHOLD_1 = 75
CANNY_THRESHOLD_2 = 200

# Epsilon value for contour approximation.
# This value is a percentage of the arc length; smaller values give a more precise approximation.
CONTOUR_APPROX_EPSILON = 0.02


# --- OMR LOGIC ---
# Number of questions in each column block
NUM_QUESTIONS_PER_COLUMN = 20

# Number of choices for each question (e.g., A, B, C, D)
NUM_CHOICES_PER_QUESTION = 4

# The radius of the circular area to scan for each bubble.
# This value might need tuning based on the size of the bubbles in the form.
SCAN_RADIUS = 12

# A pixel count threshold. If the number of non-zero pixels in a bubble's
# scan area is below this, it's considered unmarked/empty.
# This helps to filter out noise or faint marks.
PIXEL_THRESHOLD = 150

# Character to index mapping for answers
ANSWER_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

# --- OCR LOGIC ---
# Languages to be used by EasyOCR
OCR_LANGUAGES = ['vi', 'en']


# --- UI & DISPLAY ---
# Width of the display window for the interactive coordinate selection tool.
DISPLAY_WIDTH = 800
# Height of the display window for the interactive coordinate selection tool.
DISPLAY_HEIGHT = 700

# --- JSON KEYS ---
# Keys used in the coordinates.json file
KEY_BUBBLE_ANCHORS = "bubble_anchors"
KEY_OCR_REGIONS = "ocr_regions"
KEY_INFO_BLOCK = "info_block"