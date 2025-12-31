import json
import csv
from typing import Any, Dict, List

def get_file_type(file_path: str) -> str:
    """
    Returns the file extension in lowercase.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The file extension (e.g., 'pdf', 'png').
    """
    try:
        return file_path.split('.')[-1].lower()
    except IndexError:
        return ""

def load_json(file_path: str) -> Dict[str, Any] | None:
    """
    Loads data from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        A dictionary with the loaded data, or None on failure.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON from {file_path}: {e}")
        return None

def save_json(data: Dict[str, Any], file_path: str) -> None:
    """
    Saves data to a JSON file.

    Args:
        data (Dict): The dictionary to save.
        file_path (str): The path to the output JSON file.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"--> Saved JSON data to {file_path}")
    except IOError as e:
        print(f"Error saving JSON to {file_path}: {e}")

def load_answer_key_from_csv(file_path: str, answer_map: Dict[str, int]) -> List[int] | None:
    """
    Reads an answer key from a CSV file and converts it to index format.

    Args:
        file_path (str): The path to the CSV file (e.g., "1,A").
        answer_map (Dict[str, int]): A map to convert char answers to indices.

    Returns:
        A list of correct answers as integer indices, or None on failure.
    """
    answers = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    char_ans = row[1].strip().upper()
                    answers.append(answer_map.get(char_ans, -1))
        print(f"--> Loaded {len(answers)} answers from the key.")
        return answers
    except FileNotFoundError:
        print(f"Error: The answer key file was not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading the answer key file: {e}")
        return None
