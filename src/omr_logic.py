import cv2
import numpy as np
import csv


def generate_column_coordinates(start_point, end_point, num_questions=20, num_choices=4):
    """
    Generates interpolated coordinates for a single column of answers.

    This function calculates the positions of each answer bubble by linearly
    interpolating between a start and end point for a given number of questions
    and choices.

    Args:
        start_point (tuple): The (x, y) coordinate of the top-left bubble (e.g., 1A).
        end_point (tuple): The (x, y) coordinate of the bottom-right bubble (e.g., 20D).
        num_questions (int): The number of questions in the column.
        num_choices (int): The number of choices per question.

    Returns:
        list: A nested list where each inner list contains the (x, y) coordinates
              for the choices of a single question.
    """
    coordinates = []
    # Calculate the vertical distance between consecutive questions
    y_step = (end_point[1] - start_point[1]) / (num_questions - 1)
    # Calculate the horizontal distance between consecutive choices
    x_step = (end_point[0] - start_point[0]) / (num_choices - 1)

    # Iterate through each question
    for q in range(num_questions):
        question_row_coords = []
        # Calculate the y-coordinate for the current question row
        current_y = start_point[1] + (q * y_step)
        # Iterate through each choice in the question
        for c in range(num_choices):
            # Calculate the x-coordinate for the current choice
            current_x = start_point[0] + (c * x_step)
            question_row_coords.append((int(current_x), int(current_y)))
        coordinates.append(question_row_coords)
    return coordinates


def grade_with_coordinates(warped_image, all_columns_coords):
    """
    Grades the OMR sheet based on provided coordinates.

    This function takes a pre-processed (warped) image and the coordinates of
    all answer bubbles, identifies the marked answers, and returns the list of
    choices made by the student.

    Args:
        warped_image (numpy.ndarray): The standardized and warped image (e.g., 1000x1400).
        all_columns_coords (list): A list containing the coordinate lists for each column.

    Returns:
        tuple: A tuple containing:
            - list: The student's answers, where each element is the index of the
                    chosen answer (0 for A, 1 for B, etc.) or -1 if not answered.
            - numpy.ndarray: The thresholded image used for debugging.
    """
    # 1. Pre-process the image for grading logic
    gray_image = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding: Use Otsu's method for automatic thresholding.
    # This separates the dark ink from the light background.
    # cv2.THRESH_BINARY_INV makes the ink marks white (255) and the background black (0).
    threshold_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    student_answers = []
    scan_radius = 12  # Radius of the circular area to scan for each bubble (tune as needed)

    # Iterate through each column of answers
    for column_coords in all_columns_coords:
        # Iterate through each question (which has 4 choice coordinates)
        for question_coords in column_coords:
            pixel_counts = []

            # Iterate through choices A, B, C, D for the current question
            for (cx, cy) in question_coords:
                # Create a circular mask at the center of the bubble
                mask = np.zeros(threshold_image.shape, dtype="uint8")
                cv2.circle(mask, (cx, cy), scan_radius, 255, -1)

                # Count the number of white pixels (ink marks) within the mask
                count = cv2.countNonZero(cv2.bitwise_and(threshold_image, threshold_image, mask=mask))
                pixel_counts.append(count)

            # --- Answer selection logic ---
            # Find the bubble with the most ink
            max_pixel_value = max(pixel_counts)

            # Noise threshold: If the max pixel count is below a certain value,
            # consider it an empty/unmarked bubble.
            if max_pixel_value > 150:
                # The chosen answer is the one with the maximum pixel count
                answer_index = pixel_counts.index(max_pixel_value)
                student_answers.append(answer_index)  # 0=A, 1=B, 2=C, 3=D
            else:
                student_answers.append(-1)  # -1 means the question was skipped

    return student_answers, threshold_image


def load_answer_key(csv_path):
    """
    Reads the answer key from a CSV file and converts it to index format (0, 1, 2, 3).

    Args:
        csv_path (str): The path to the CSV file (Format: 1,A \n 2,B ...).

    Returns:
        list: A list of correct answers as integer indices [0, 1, 3, 2, ...].
    """
    answers = []
    # Map character answers to integer indices
    mapper = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    char_ans = row[1].strip().upper()
                    if char_ans in mapper:
                        answers.append(mapper[char_ans])
                    else:
                        answers.append(-1)  # Represents an invalid or missing answer
        print(f"--> Loaded {len(answers)} answers from the key.")
        return answers
    except FileNotFoundError:
        print(f"Error: The answer key file was not found at {csv_path}")
        return []
    except Exception as e:
        print(f"Error reading the answer key file: {e}")
        return []


def calculate_score(student_answers, correct_answers):
    """
    Compares student's answers with the correct answers and calculates the score.

    Args:
        student_answers (list): A list of the student's answers (as indices).
        correct_answers (list): A list of the correct answers (as indices).

    Returns:
        tuple: A tuple containing:
            - float: The final score on a scale of 10.
            - int: The total number of correct answers.
            - list: A list of boolean results (True for correct, False for incorrect).
    """
    correct_count = 0
    results = []  # To store True/False for each question to color-code later

    # Compare only up to the number of questions available in the answer key
    num_questions_to_grade = min(len(student_answers), len(correct_answers))
    if len(correct_answers) == 0:
        return 0, 0, [False]*len(student_answers)


    for i in range(num_questions_to_grade):
        if student_answers[i] == correct_answers[i]:
            correct_count += 1
            results.append(True)
        else:
            results.append(False)
    
    # Pad results if student answered more questions than in the key
    while len(results) < len(student_answers):
        results.append(False)


    # Calculate score on a scale of 10
    score = (correct_count / len(correct_answers)) * 10

    return score, correct_count, results

