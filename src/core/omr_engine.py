import cv2
import numpy as np
from typing import List, Tuple, Dict
from config import Config

class OMREngine:
    """
    Handles the core Optical Mark Recognition (OMR) logic for grading bubble sheets.
    """

    def __init__(self, omr_config: Config.OMRConfig):
        """
        Initializes the OMR engine with specific configuration.

        Args:
            omr_config (Config.OMRConfig): The OMR configuration object.
        """
        self.cfg = omr_config

    def grade_student_answers(self, warped_image: np.ndarray, all_columns_coords: List[List[List[int]]]) -> List[int]:
        """
        Identifies the marked answers from the warped image based on bubble coordinates.

        Args:
            warped_image (np.ndarray): The standardized and warped image of the answer sheet.
            all_columns_coords (List): A list containing coordinate lists for each answer column.

        Returns:
            A list of student's answers, where each element is the index of the
            chosen answer (0-based) or -1 if unanswered.
        """
        gray_image = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
        threshold_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        student_answers = []
        for column_coords in all_columns_coords:
            for question_coords in column_coords:
                pixel_counts = []
                for (cx, cy) in question_coords:
                    mask = np.zeros(threshold_image.shape, dtype="uint8")
                    cv2.circle(mask, (cx, cy), self.cfg.SCAN_RADIUS, 255, -1)
                    count = cv2.countNonZero(cv2.bitwise_and(threshold_image, threshold_image, mask=mask))
                    pixel_counts.append(count)

                max_pixel_value = max(pixel_counts) if pixel_counts else 0
                if max_pixel_value > self.cfg.PIXEL_THRESHOLD:
                    answer_index = pixel_counts.index(max_pixel_value)
                    student_answers.append(answer_index)
                else:
                    student_answers.append(-1)
        
        return student_answers

    @staticmethod
    def generate_answer_coordinates(start_point: Tuple[int, int], end_point: Tuple[int, int], num_questions: int, num_choices: int) -> List[List[Tuple[int, int]]]:
        """
        Generates interpolated coordinates for a single column of answer bubbles.

        Args:
            start_point: The (x, y) coordinate of the top-left bubble.
            end_point: The (x, y) coordinate of the bottom-right bubble.
            num_questions: The number of questions in the column.
            num_choices: The number of choices per question.

        Returns:
            A nested list of (x, y) coordinates for each answer bubble.
        """
        coordinates = []
        # Prevent division by zero if there's only one question or choice
        y_step = (end_point[1] - start_point[1]) / (num_questions - 1) if num_questions > 1 else 0
        x_step = (end_point[0] - start_point[0]) / (num_choices - 1) if num_choices > 1 else 0

        for q in range(num_questions):
            question_row_coords = []
            current_y = start_point[1] + (q * y_step)
            for c in range(num_choices):
                current_x = start_point[0] + (c * x_step)
                question_row_coords.append((int(current_x), int(current_y)))
            coordinates.append(question_row_coords)
        return coordinates

    @staticmethod
    def calculate_score(student_answers: List[int], correct_answers: List[int]) -> Tuple[float, int, List[bool]]:
        """
        Compares student's answers with the correct answers and calculates the score.

        Args:
            student_answers: A list of the student's answers (as indices).
            correct_answers: A list of the correct answers (as indices).

        Returns:
            A tuple containing (final score, number of correct answers, list of results).
        """
        if not correct_answers:
            return 0.0, 0, [False] * len(student_answers)

        correct_count = 0
        results = []
        num_to_grade = min(len(student_answers), len(correct_answers))

        for i in range(num_to_grade):
            if student_answers[i] == correct_answers[i] and student_answers[i] != -1:
                correct_count += 1
                results.append(True)
            else:
                results.append(False)

        # Ensure results list matches the length of student answers
        while len(results) < len(student_answers):
            results.append(False)
        
        score = (correct_count / len(correct_answers)) * 10.0
        return score, correct_count, results
