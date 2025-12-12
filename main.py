import cv2
import numpy as np
import os

from src import omr_logic
from src import measure_tool

# --- GENERAL CONFIGURATION ---
PDF_PATH = "data/raw/OMR_Sample.pdf"
OUTPUT_PATH = "output/"
# Standard size of the sheet after warping, ALL COORDINATES ARE BASED ON THIS SIZE
STANDARD_SIZE = (1000, 1400)

ANSWER_KEY_PATH = "data/answer/answer_key.csv"
# Get coordinates and the pre-warped image from the measure_tool
# This allows the user to select the region of interest once
ANSWER_BLOCK_ANCHORS, warped_image = measure_tool.get_coordinates_from_image(PDF_PATH)


def main():
    """
    Main function to run the OMR grading process.
    """
    # The entire process of reading and warping the image is already done in measure_tool
    # Now, just check if there is an image to process
    if warped_image is not None and len(ANSWER_BLOCK_ANCHORS) == 2:
        print("--> Successfully retrieved image and coordinates.")
        print(f"    - Anchor point coordinates: {ANSWER_BLOCK_ANCHORS}")
        print(f"    - Image size: {warped_image.shape[:2]}")

        # 3. Generate coordinate grid and grade the sheet
        print("--> Generating coordinates for answer cells...")
        # Generate coordinates for a block of 20 questions
        answer_coords = omr_logic.generate_column_coordinates(
            start_point=ANSWER_BLOCK_ANCHORS[0],
            end_point=ANSWER_BLOCK_ANCHORS[1],
            num_questions=20,
            num_choices=4
        )
        # Wrap it in a list to be compatible with the grading function
        all_coords = [answer_coords]

        # 3. Grade the sheet (Get student's answers)
        print("-> Recognizing the submitted answers...")
        student_answers, thresh_debug = omr_logic.grade_with_coordinates(warped_image, all_coords)

        # --- NEW SECTION: CALCULATE SCORE ---
        print("-> Grading with the answer key...")

        # 1. Load the correct answers
        correct_answers = omr_logic.load_answer_key(ANSWER_KEY_PATH)

        if not correct_answers:
            print("Warning: Answer key file not found or is empty!")
            final_score = 0
            results = [False] * len(student_answers)
        else:
            # 2. Calculate the score
            final_score, num_correct, results = omr_logic.calculate_score(student_answers, correct_answers)
            print("\n==========================")
            print(f"   RESULT: {final_score:.2f} / 10")
            print(f"   Correct answers: {num_correct} / {len(correct_answers)}")
            print("==========================\n")

        # 4. Display the results on the image (UPGRADED)
        display_image = warped_image.copy()

        # Initialize an index for answers
        idx = 0
        # Iterate through each column of answer coordinates
        for col in all_coords:
            # Iterate through each question in the column
            for q_coords in col:
                if idx >= len(student_answers):
                    break  # Stop if we've processed all of the student's answers

                student_choice = student_answers[idx]
                is_correct = results[idx] if idx < len(results) else False

                # Color: Green (Correct) / Red (Incorrect)
                color = (0, 255, 0) if is_correct else (0, 0, 255)

                if student_choice != -1:
                    # Circle the student's chosen answer
                    cx, cy = q_coords[student_choice]
                    cv2.circle(display_image, (cx, cy), 15, color, 2)
                else:
                    # If the question is skipped, mark it with a red question mark
                    cx, cy = q_coords[0]  # Position near the first choice
                    cv2.putText(display_image, "?", (cx - 15, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # If the answer is incorrect, also show the correct answer (Optional)
                if not is_correct and idx < len(correct_answers):
                    correct_idx = correct_answers[idx]
                    if correct_idx != -1:  # If the answer key has a valid answer
                        # Get coordinates of the correct choice
                        cx_corr, cy_corr = q_coords[correct_idx]
                        # Draw a small green dot to indicate the correct answer
                        cv2.circle(display_image, (cx_corr, cy_corr), 5, (0, 255, 0), -1)

                idx += 1

        # Display the result image (with circles)
        cv2.imshow("Scoring Result", cv2.resize(display_image, (600, 800)))

        # --- CREATE A NEW WINDOW JUST TO DISPLAY THE SCORE ---
        # Create a white background image to display text
        score_display = np.ones((300, 450, 3), dtype=np.uint8) * 255

        # "RESULT" text
        cv2.putText(score_display, "RESULT", (100, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)

        # The score
        cv2.putText(score_display, f"{final_score:.2f} / 10", (80, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

        # Number of correct answers
        cv2.putText(score_display, f"Correct: {num_correct} / {len(correct_answers)}",
                    (50, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

        # Display the score window
        cv2.imshow("Score", score_display)
        # --- END OF SCORE WINDOW SECTION ---

        # save output Image and Result in /output
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)

        cv2.imwrite(os.path.join(OUTPUT_PATH, "scoring_result.png"), display_image)
        cv2.imwrite(os.path.join(OUTPUT_PATH, "score.png"), score_display)
        print(f"\n--> Saved results to {OUTPUT_PATH}")

        cv2.waitKey(0)  # Wait for a key press to close the windows
        cv2.destroyAllWindows()  # Close all OpenCV windows
    else:
        print("--> COULD NOT get coordinates or image. Please check the PDF file.")


if __name__ == "__main__":
    # This block ensures the main function is called only when the script is executed directly
    main()
