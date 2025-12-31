import cv2
import numpy as np
from typing import List, Dict, Tuple

from config import Config

def draw_results_on_image(
    image: np.ndarray,
    student_answers: List[int],
    correct_answers: List[int],
    results: List[bool],
    all_coords: List[List[List[int]]],
    omr_cfg: Config.OMRConfig
) -> np.ndarray:
    """
    Draws the grading results (circles, marks) on the provided image.

    Args:
        image: The warped image to draw on.
        student_answers: The list of student's answers (indices).
        correct_answers: The list of correct answers from the key (indices).
        results: A list of booleans indicating correctness for each question.
        all_coords: A nested list of coordinates for all answer bubbles.
        omr_cfg: The OMR configuration object.

    Returns:
        The image with the results drawn on it.
    """
    display_image = image.copy()
    idx = 0

    for col in all_coords:
        for q_coords in col:
            if idx >= len(student_answers):
                break

            student_choice = student_answers[idx]
            is_correct = results[idx] if idx < len(results) else False
            color = (0, 255, 0) if is_correct else (0, 0, 255)

            # Mark the student's choice
            if student_choice != -1:
                cx, cy = q_coords[student_choice]
                cv2.circle(display_image, (cx, cy), omr_cfg.SCAN_RADIUS + 3, color, 2)
            else:
                # Mark skipped questions
                cx, cy = q_coords[0]
                cv2.putText(display_image, "?", (cx - 15, cy + 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # If incorrect, mark the correct answer
            if not is_correct and idx < len(correct_answers):
                correct_idx = correct_answers[idx]
                if correct_idx != -1:
                    cx_corr, cy_corr = q_coords[correct_idx]
                    cv2.circle(display_image, (cx_corr, cy_corr), 5, (0, 255, 0), -1)
            
            idx += 1

    return display_image

def create_score_display(final_score: float, num_correct: int, total_questions: int) -> np.ndarray:
    """
    Creates a new image to display the final score.

    Args:
        final_score: The final score (e.g., out of 10).
        num_correct: The number of correctly answered questions.
        total_questions: The total number of questions.

    Returns:
        The image created to display the score.
    """
    score_display = np.ones((300, 450, 3), dtype=np.uint8) * 255
    cv2.putText(score_display, "RESULT", (100, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
    cv2.putText(score_display, f"{final_score:.2f} / 10", (80, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
    cv2.putText(score_display, f"Correct: {num_correct} / {total_questions}", (50, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    return score_display

def show_final_results(result_image: np.ndarray, score_image: np.ndarray, ocr_data: Dict, ui_cfg: Config.UIConfig):
    """
    Displays the final result images and prints OCR data.

    Args:
        result_image: The image with grading details.
        score_image: The image showing the final score.
        ocr_data: Dictionary containing the extracted text.
        ui_cfg: The UI configuration object.
    """
    if ocr_data:
        print("\n--- OCR Extracted Information ---")
        for key, value in ocr_data.items():
            print(f"  - {key.replace('_', ' ').title()}: {value}")
        print("---------------------------------")

    print("\n--> Displaying results. Press any key to close all windows.")
    
    # Calculate aspect ratio for display
    h, w = result_image.shape[:2]
    display_h = ui_cfg.DISPLAY_HEIGHT
    display_w = int(w * (display_h / h))

    cv2.imshow("Scoring Result", cv2.resize(result_image, (display_w, display_h)))
    cv2.imshow("Score", score_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
