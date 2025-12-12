# OMR (Optical Mark Recognition) Scoring Machine

This project demonstrates the capabilities of OpenCV and image processing to automatically grade multiple-choice answer sheets.

## Key Features

- **Multi-format Input**: Processes input from both PDF files and common image formats.
- **Automatic Document Detection and Warping**: Automatically finds the answer sheet in an image and applies a perspective warp to straighten it for accurate processing.
- **Interactive Anchor Point Selection**: An interactive window allows the user to define the answer area on a new or unrecognized sheet format.
- **Accurate Scoring**: Grades sheets with a structure of 20 questions and 4 choices (A, B, C, D).
- **Visual Feedback**: Draws circles around the recognized answers and displays the final graded sheet in a window.
- **Dedicated Score Display**: Shows the final score, and number of correct answers in a separate, clean window.
- **Saves Results**: Automatically saves the graded sheet image and the score card to the `output/` directory.

## Project Structure

- `main.py`: The main executable file. Run this file to start the grading process.
- `requirements.txt`: A list of the required Python libraries.
- `output/`: The directory where the final graded image and score card are saved.
- `src/`: The directory containing the core processing source code.
  - `pre_processing.py`: Functions for image pre-processing (blur, Canny edge detection, etc.).
  - `utils.py`: Utility functions (perspective transform, point ordering, etc.).
  - `omr_logic.py`: The main logic for generating coordinates and grading.
  - `measure_tool.py`: The interactive tool for selecting answer block coordinates.
- `data/`:
  - `raw/`: Contains the input answer sheet (PDF or image).
  - `answer/`: Contains the answer key file.
- `poppler-25.11.0/`: The Poppler library, required for handling PDF files on Windows.

## Setup

1.  **Python 3**: Ensure you have Python 3.8 or newer installed.
2.  **Poppler Library (for PDF support on Windows)**:
    - This project requires Poppler to read PDF files. The `poppler-25.11.0` directory is already included.
    - You must add the path to the `poppler-25.11.0/Library/bin` folder to your system's **Environment Variables (`Path`)** so the program can find it.
3.  **Install Python Libraries**:
    Open a terminal or command prompt and run the following command to install the necessary libraries from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## How to Use

1.  **Prepare the Answer Key**:
    - Place your answer key in `data/answer/answer_key.csv`.
    - The file must be a CSV with two columns: the question number and the correct choice. For example:
      ```csv
      1,A
      2,B
      3,C
      4,D
      ```
2.  **Place the Answer Sheet**:
    - Put your scanned answer sheet (e.g., `OMR_Sample.pdf`) into the `data/raw/` directory.
    - Update the `PDF_PATH` variable in `main.py` to point to your file if it's named differently.
    ```python
    PDF_PATH = "data/raw/your_file_name.pdf"
    ```
3.  **Run the Program**:
    ```bash
    python main.py
    ```
4.  **Select Anchor Points (First-time run or new template)**:
    - An interactive window titled "Coordinate Selection" will appear.
    - As instructed in the console, click on the center of the **top-left answer bubble** (e.g., for Question 1, Choice A).
    - Next, click on the center of the **bottom-right answer bubble** (e.g., for Question 20, Choice D).
    - The window will close automatically after you select the two points.
5.  **View the Results**:
    - Two windows will appear:
        - **"Scoring Result"**: Shows the original sheet with the student's answers circled (green for correct, red for incorrect) and the correct answers marked with a small dot if the student's choice was wrong.
        - **"Score"**: A separate, clean window displaying the final score and the count of correct answers.
    - The same two images are saved as `scoring_result.png` and `score.png` in the `output/` directory for your records.
    - Press any key to close the result windows.
    
## Troubleshooting

- **Poppler Error**: If you see an error related to `pdf2image` or Poppler not being found, it's almost certainly because the Poppler `bin` directory is not in your system's `Path`. Double-check your environment variables setup.
- **"Could not find the document frame"**: This error means the script was unable to detect a rectangular shape that looks like a sheet of paper. Ensure the input image has a clear, high-contrast background behind the paper.
- **Incorrect Anchor Point Selection**: If you click the wrong points, simply press `q` or `ESC` to close the selection window and run the program again.

## Limitations

- **Fixed Format**: The current logic is hard-coded for a specific layout (one block of 20 questions with 4 choices each). To adapt to other layouts (e.g., more questions, multiple columns), you would need to modify the coordinate generation logic in `main.py` and `omr_logic.py`.
- **Single Page Only**: The script only processes the first page of a multi-page PDF.
- **Sensitivity**: The accuracy of bubble detection depends on the `scan_radius` and `max_pixel_value` thresholds in `src/omr_logic.py`. You may need to tune these values for different image resolutions or lighting conditions.
