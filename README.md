# Automatic OMR & OCR Grading System

This project provides a comprehensive solution for automatically grading multiple-choice answer sheets (Optical Mark Recognition - OMR) and extracting text from specified regions (Optical Character Recognition - OCR) directly from a PDF file.

The system automatically identifies the main answer sheet, isolates it, and then intelligently uses the surrounding areas of the page to find and read textual information like student name, ID, or exam code.

## Key Features

- **PDF Input**: Processes scanned documents directly from PDF files.
- **Automatic Document Detection**: Finds the document within the scanned image and applies a perspective warp to correct its orientation.
- **Hybrid Coordinate Setup**:
    - **Manual OMR Anchors**: A simple, one-time interactive tool to select the boundaries of the multiple-choice answer block.
    - **Automatic OCR Region Detection**: Intelligently identifies all separate text blocks in the area outside the main answer sheet, creating OCR regions automatically.
- **OMR Scoring**: Accurately grades multiple-choice questions based on a provided answer key.
- **OCR Text Extraction**: Extracts and records text from the automatically detected regions.
- **Rich Visual Feedback**: Generates and displays result images showing the graded answers and the final score.
- **Persistent Results**: Saves all outputs, including result images and extracted data (OMR and OCR), to the `output/` directory.

## Project Structure

- `main.py`: The main executable file to run the entire process.
- `requirements.txt`: A list of the required Python libraries.
- `src/`: Contains the core source code.
  - `config.py`: **Important configuration file** for setting up paths and parameters.
  - `pre_processing.py`: Handles image preparation (edge detection, warping).
  - `omr_logic.py`: Contains the logic for grading bubble sheets.
  - `ocr_logic.py`: Manages text extraction from image regions.
  - `measure_tool.py`: The interactive tool for the first-time setup.
  - `utils.py`: Helper functions for transformations and coordinate manipulation.
  - `ui.py`: Manages user interface elements like dialogs and result display.
- `data/`:
  - `raw/`: Place your input PDF file here.
  - `answer/`: Contains the answer key for the OMR section.
  - `template/`: Stores the saved coordinates template.
- `output/`: All results and artifacts are saved here.
- `poppler-25.11.0/`: The Poppler library, required for PDF processing on Windows.

## Setup

1.  **Python**: Ensure you have Python 3.8 or newer installed.
2.  **Poppler (for PDF support)**:
    - This project uses `pdf2image`, which requires the Poppler utility.
    - The `poppler-25.11.0` directory is included for Windows users.
    - **You must add the full path** to the `poppler-25.11.0\Library\bin` folder to your system's **Environment Variables (`Path`)** for the program to work.
3.  **Install Python Libraries**:
    Open a terminal or command prompt and run the following command:
    ```bash
    pip install -r requirements.txt
    ```
    _Note: The first time you run the program, the `easyocr` library may need to download pre-trained models. This is a one-time process._

## How to Use

1.  **Configuration**:
    - Place your scanned answer sheet PDF into the `data/raw/` folder.
    - Place your answer key in `data/answer/answer_key.csv`.
    - Open `src/config.py` and verify that the paths (`PDF_PATH`, `ANSWER_KEY_PATH`) and parameters match your setup.

2.  **Run the Program**:
    ```bash
    python main.py
    ```

3.  **First-Time Configuration**:
    - If no coordinate template is found, a dialog box will ask for permission to start the setup process.
    - An interactive window will open for you to perform **Phase 1**:
        - **Select OMR Anchors**: Click on the center of the **top-left answer bubble** (e.g., Question 1, Choice A) and then on the center of the **bottom-right answer bubble** of the main answer block.
    - After you select two points, the window will close. **Phase 2 (OCR Region Detection)** runs automatically in the background.
    - A template file (`coordinates.json`) will be saved in the location specified by `COORDINATES_PATH` in the config.

4.  **Subsequent Runs**:
    - On future runs, the program will automatically use the saved `coordinates.json` template to process the PDF without any interaction.
    - To re-run the configuration, simply delete the `coordinates.json` file.

5.  **View the Results**:
    - The extracted OCR information will be printed to the console.
    - Two windows will appear:
        - **"Scoring Result"**: The graded answer sheet with corrections.
        - **"Score"**: The final OMR score.
    - Check the `output/` directory for all saved artifacts:
        - `scoring_result.png`: The graded sheet image.
        - `score.png`: The score card image.
        - `outside_area.png`: The "leftover" part of the page used for OCR.
        - `ocr_results.json`: A JSON file containing the extracted text from each auto-detected region.

## Troubleshooting

- **Poppler Error**: If you see an error like `PDFInfoNotInstalledError` or `PopplerNotInstalledError`, it means the Poppler `bin` directory is not correctly added to your system's `Path`.
- **"Could not find the document frame"**: The script could not detect the main paper sheet. Ensure your scanned image has good contrast between the paper and the background.