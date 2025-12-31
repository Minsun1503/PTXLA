# Automatic Test Grading System (OMR & OCR)

This project is a Python application for automatically grading multiple-choice tests from scanned images or PDF files. It uses computer vision techniques to identify the test sheet, perform Optical Mark Recognition (OMR) on the answer grid, and use Optical Character Recognition (OCR) to extract additional information like student IDs.

The codebase has been refactored to a data-driven architecture, separating the core processing engine from data and configuration.

## Features

- **Automatic Document Warping**: Straightens and corrects the perspective of the test sheet.
- **Data-Driven Core Engine**:
  - **OMR (Optical Mark Recognition)**: Detects selected choices in the answer grid.
  - **OCR (Optical Character Recognition)**: Extracts text from predefined regions.
- **Batch Processing**: Can process multiple files from a directory.
- **Flexible Input**: Supports both PDF and common image formats (PNG, JPG, JPEG).
- **Centralized Configuration**: A single `config.py` file manages all settings in a structured way.
- **Interactive Template Setup**: A graphical tool to easily define the layout of a new test sheet.

## Project Structure

The project is organized into a modular structure:

```
PTXLA/
├── main.py                # Main orchestrator script
├── config.py              # Central configuration file
├── requirements.txt
├── data/
│   ├── answer/            # Contains the answer key (e.g., answer_key.csv)
│   ├── raw/               # Raw input files (PDFs, images)
│   └── template/          # Stores the generated coordinates template
├── src/
│   ├── core/
│   │   ├── processor.py   # Image warping and pre-processing
│   │   ├── omr_engine.py  # Core bubble grading logic
│   │   └── ocr_engine.py  # Core text extraction logic
│   ├── utils/
│   │   ├── file_io.py     # JSON/CSV reading/writing
│   │   └── image_utils.py # Geometric image transformations
│   └── view/
│       └── renderer.py    # Drawing results, creating score images
└── tools/
    └── create_template.py # Interactive tool to create the coordinate template
```

## How to Run

### 1. Prerequisites

- Python 3.9+
- Poppler (for PDF processing). Must be accessible from your system's PATH.

### 2. Installation

Clone the repository and install the required Python packages:

```bash
git clone <repository-url>
cd PTXLA
pip install -r requirements.txt
```

### 3. Configuration

All configuration is handled in the `config.py` file.

1.  **Place Input Files**:
    - For **batch processing**, place your test sheets in the `data/raw/batch_input/` directory.
    - For **single file processing**, ensure the `PDF_PATH` in `config.py` points to your file.
2.  **Set Answer Key**: Make sure your answer key is correctly formatted in `data/answer/answer_key.csv`.
3.  **Review Settings**: Open `config.py` and adjust settings as needed. You can toggle `BATCH_MODE` between `True` and `False`.

### 4. Step 1: Create the Exam Template

Before grading, you must teach the application where the answer bubbles and OCR fields are located on your exam sheet.

Run the interactive template creation tool. Make sure to use a clean, unscanned version of your exam sheet (as a PDF or image) as the template.

```bash
python tools/create_template.py
```

The tool will guide you through a two-phase process in a graphical window:
- **Phase 1**: Select the anchor points for the answer bubble grid on the main test sheet.
- **Phase 2**: Select the anchor points for any information block (like a student ID) on the part of the image outside the main sheet.

This will create a `coordinates.json` file in the `data/template/` directory. **This step only needs to be done once for each unique exam layout.**

### 5. Step 2: Run the Grading Process

Once the template is created, run the main application:

```bash
python main.py
```

- If `BATCH_MODE` is `True` in `config.py`, the script will process all files in the batch input directory.
- If `BATCH_MODE` is `False`, it will process the single file specified in the config and display the results in a window.

**Note for Windows Users**: To avoid potential `UnicodeEncodeError` in the console, it is recommended to run the scripts with the `PYTHONIOENCODING` environment variable set to `utf-8`:

```powershell
$env:PYTHONIOENCODING='utf-8'; python main.py
```