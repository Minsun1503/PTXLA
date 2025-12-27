# Multiple Choice Test Automatic Grading

This project is a Python application for automatically grading multiple-choice tests from scanned or photographed images, as well as PDF files. It uses computer vision techniques to identify the test sheet, extract answers, and compare them against an answer key.

## Features

- **Automatic Document Warping**: Straightens and corrects the perspective of the test sheet from an image.
- **OMR (Optical Mark Recognition)**: Detects selected choices in the answer grid.
- **OCR (Optical Character Recognition)**: Extracts handwritten or printed text, such as student ID or name.
- **Batch Processing**: Can process multiple files from a directory.
- **Flexible Input**: Supports both PDF and common image formats (PNG, JPG, JPEG).
- **Easy Configuration**: Uses a `config.py` file to manage all settings.

## How It Works

1.  **Preprocessing**: The input image or PDF is processed to find the four corners of the test paper. A perspective transform is then applied to get a flat, top-down view of the document.
2.  **Coordinate Setup**: A one-time manual setup is required to define the locations of the answer bubbles and any OCR regions. These coordinates are saved to a JSON file.
3.  **OMR**: Using the predefined coordinates, the application scans the answer grid to determine which bubble is marked for each question.
4.  **Scoring**: The student's answers are compared to the correct answers loaded from a key, and a score is calculated.
5.  **OCR**: Text is extracted from any defined regions on the sheet (e.g., for student identification).
6.  **Output**: The application saves a result image with the grading marked, a score display image, and a JSON file with the OCR results.

## How to Run

### 1. Prerequisites

- Python 3.8+
- Tesseract OCR (must be installed and in the system's PATH)
- Poppler (for PDF processing)

### 2. Installation

Clone the repository and install the required Python packages:

```bash
git clone <repository-url>
cd <repository-name>
pip install -r requirements.txt
```

### 3. Configuration

- Place your test sheet images or PDFs in the `data/raw/batch_input` directory.
- Create an answer key file at `data/answer/answer_key.csv`.
- Edit `src/config.py` to adjust settings like the number of questions, choices, etc.

### 4. Running the Application

To run the application, execute the `main.py` script:

```bash
python main.py
```

On the first run, you will be guided through a coordinate setup process in an interactive window.

To avoid potential `UnicodeEncodeError` on Windows when printing, it's recommended to run the script with the `PYTHONIOENCODING` environment variable set to `utf-8`:

```powershell
$env:PYTHONIOENCODING='utf-8'; python main.py
```

This ensures that any special characters in the console output are displayed correctly.
