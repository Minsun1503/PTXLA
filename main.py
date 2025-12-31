import os
import sys
import cv2
from typing import Dict, Any

# Import refactored modules
from config import Config
from src.core import processor, omr_engine, ocr_engine
from src.utils import file_io
from src.view import renderer

def run_grading_process(
    warped_image: os.PathLike,
    outside_image: os.PathLike,
    template_data: Dict[str, Any],
    correct_answers: Dict,
    cfg: Config,
    omr_eng: omr_engine.OMREngine,
    ocr_eng: ocr_engine.OCREngine,
) -> tuple:
    """
    Orchestrates the grading process for a single warped image.

    Args:
        warped_image: The perspective-corrected image of the sheet.
        outside_image: The image containing the area outside the main document.
        template_data: Loaded data from the coordinates JSON file.
        correct_answers: Loaded data from the answer key CSV.
        cfg: The main configuration object.
        omr_eng: An instance of the OMREngine.
        ocr_eng: An instance of the OCREngine.

    Returns:
        A tuple containing the result image, score image, and OCR data.
    """
    if warped_image is None:
        print("--> ERROR: Warped image is missing, cannot run grading.")
        return None, None, None

    # --- OMR Section ---
    bubble_anchors = template_data.get(cfg.JSON.KEY_BUBBLE_ANCHORS)
    if bubble_anchors and len(bubble_anchors) == 2:
        print("--- Running OMR ---")
        answer_coords = omr_eng.generate_answer_coordinates(
            start_point=bubble_anchors[0],
            end_point=bubble_anchors[1],
            num_questions=cfg.OMR.NUM_QUESTIONS_PER_COLUMN,
            num_choices=cfg.OMR.NUM_CHOICES_PER_QUESTION,
        )
        all_coords = [answer_coords]
        
        student_answers = omr_eng.grade_student_answers(warped_image, all_coords)

        if not correct_answers:
            print("Warning: Answer key is missing or empty. OMR score will be 0.")
            score, num_correct, results = 0.0, 0, [False] * len(student_answers)
        else:
            score, num_correct, results = omr_eng.calculate_score(student_answers, correct_answers)
            print(f"   OMR Result: {score:.2f}/10 - {num_correct}/{len(correct_answers)} correct.")
        
        result_image = renderer.draw_results_on_image(
            warped_image, student_answers, correct_answers, results, all_coords, cfg.OMR
        )
        score_image = renderer.create_score_display(score, num_correct, len(correct_answers or []))

    else:
        print("--> OMR anchors not found in template. Skipping OMR.")
        result_image = warped_image.copy()
        score_image = renderer.create_score_display(0.0, 0, 0)

    # --- OCR Section ---
    ocr_regions = template_data.get(cfg.JSON.KEY_OCR_REGIONS, {})
    ocr_data = ocr_eng.extract_text_from_regions(outside_image, ocr_regions)

    return result_image, score_image, ocr_data

def process_single_file(file_path: str, output_dir: str, template_data: dict, correct_answers: dict, cfg: Config, omr_eng: omr_engine.OMREngine, ocr_eng: ocr_engine.OCREngine) -> tuple | None:
    """
    Processes a single input file (PDF or image) from path to results.
    """
    print(f"\n--- Processing file: {os.path.basename(file_path)} ---")
    
    # 1. Load Image
    file_type = file_io.get_file_type(file_path)
    if file_type == 'pdf':
        original_image = processor.get_image_from_pdf(file_path)
    elif file_type in ['png', 'jpg', 'jpeg']:
        original_image = processor.get_image_from_file(file_path)
    else:
        print(f"Error: Unsupported file format '{file_type}'. Skipping.")
        return None
        
    if original_image is None:
        print(f"Error: Could not load image from {file_path}. Skipping.")
        return None

    # 2. Process and Warp
    warped_img, outside_img = processor.process_and_warp_image(original_image, cfg.ImageProcessing)
    if warped_img is None:
        print(f"Error: Could not find document frame in {file_path}. Skipping.")
        return None

    # 3. Run Grading
    result_img, score_img, ocr_data = run_grading_process(
        warped_img, outside_img, template_data, correct_answers, cfg, omr_eng, ocr_eng
    )

    # 4. Save Outputs
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    cv2.imwrite(os.path.join(output_dir, cfg.Paths.SCORING_RESULT_IMAGE_NAME), result_img)
    cv2.imwrite(os.path.join(output_dir, cfg.Paths.SCORE_IMAGE_NAME), score_img)
    if outside_img is not None:
        cv2.imwrite(os.path.join(output_dir, cfg.Paths.OUTSIDE_AREA_IMAGE_NAME), outside_img)
    if ocr_data:
        file_io.save_json(ocr_data, os.path.join(output_dir, cfg.Paths.OCR_RESULT_JSON_NAME))

    print(f"--> Saved results to {output_dir}")
    
    return result_img, score_img, ocr_data


def main():
    """
    Main orchestrator for the application.
    """
    # 1. Initialize Configuration and Engines
    cfg = Config()
    omr_eng = omr_engine.OMREngine(cfg.OMR)
    ocr_eng = ocr_engine.OCREngine(cfg.OCR)

    # 2. Load Essential Data (Template and Answer Key)
    template_data = file_io.load_json(cfg.Paths.COORDINATES_PATH)
    if not template_data:
        print(f"FATAL: Could not load coordinate template from '{cfg.Paths.COORDINATES_PATH}'.")
        print("Please run the template creation tool first:")
        print(f"    python tools/create_template.py")
        sys.exit(1)

    correct_answers = file_io.load_answer_key_from_csv(cfg.Paths.ANSWER_KEY_PATH, cfg.OMR.ANSWER_MAP)
    if not correct_answers:
        print(f"Warning: Could not load answer key from '{cfg.Paths.ANSWER_KEY_PATH}'. OMR scores will be 0.")

    # 3. Select Mode (Batch or Single)
    if cfg.Batch.BATCH_MODE:
        print("\n--- BATCH PROCESSING MODE ---")
        input_dir = cfg.Paths.BATCH_INPUT_DIR
        output_dir = cfg.Paths.BATCH_OUTPUT_DIR
        
        if not os.path.isdir(input_dir):
            print(f"Error: Batch input directory not found: '{input_dir}'")
            sys.exit(1)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        supported_extensions = ('.pdf', '.png', '.jpg', '.jpeg')
        files_to_process = [f for f in os.listdir(input_dir) if f.lower().endswith(supported_extensions)]
        
        if not files_to_process:
            print(f"No supported files found in '{input_dir}'.")
            return

        print(f"Found {len(files_to_process)} files to process.")
        for filename in files_to_process:
            file_path = os.path.join(input_dir, filename)
            file_basename = os.path.splitext(filename)[0]
            specific_output_dir = os.path.join(output_dir, file_basename)
            
            process_single_file(file_path, specific_output_dir, template_data, correct_answers, cfg, omr_eng, ocr_eng)
        print("\n--- BATCH PROCESSING COMPLETE ---")

    else:
        print("\n--- SINGLE FILE PROCESSING MODE ---")
        results = process_single_file(
            cfg.Paths.PDF_PATH,
            cfg.Paths.OUTPUT_PATH,
            template_data,
            correct_answers,
            cfg,
            omr_eng,
            ocr_eng
        )
        if results:
            result_img, score_img, ocr_data = results
            renderer.show_final_results(result_img, score_img, ocr_data, cfg.UI)

if __name__ == "__main__":
    main()