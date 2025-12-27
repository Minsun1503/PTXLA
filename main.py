import os
import json
import sys

# Import project modules
from src import config
from src import pre_processing
from src import measure_tool
from src import omr_logic
from src import ocr_logic
from src import ui
from src import utils


def run_grading_process(answer_block_anchors, ocr_regions, warped_image, outside_image, output_dir):
    """
    Orchestrates the full grading process, including OMR and OCR.

    Args:
        answer_block_anchors (list): A list containing the two anchor coordinates.
        ocr_regions (dict): A dictionary of named regions for OCR.
        warped_image (numpy.ndarray): The processed, perspective-corrected image of the sheet.
        outside_image (numpy.ndarray): The image containing the area outside the main document.
        output_dir (str): The directory where output files will be saved.
    """
    if warped_image is None:
        print("--> LỖI: Không có ảnh để xử lý.")
        return None, None, None

    # --- OMR Section ---
    if answer_block_anchors:
        print("--- Bắt đầu chấm điểm trắc nghiệm (OMR) ---")
        answer_coords = omr_logic.generate_column_coordinates(
            start_point=answer_block_anchors[0],
            end_point=answer_block_anchors[1],
            num_questions=config.NUM_QUESTIONS_PER_COLUMN,
            num_choices=config.NUM_CHOICES_PER_QUESTION
        )
        all_coords = [answer_coords]
        student_answers, _ = omr_logic.grade_with_coordinates(warped_image, all_coords)
        correct_answers = omr_logic.load_answer_key(config.ANSWER_KEY_PATH)

        if not correct_answers:
            print("Cảnh báo: Không tìm thấy hoặc file đáp án trống!")
            final_score, num_correct, results = 0, 0, [False] * len(student_answers)
        else:
            final_score, num_correct, results = omr_logic.calculate_score(student_answers, correct_answers)
            print(f"   KẾT QUẢ OMR: {final_score:.2f} / 10 - {num_correct} / {len(correct_answers)} câu đúng.")
        
        result_image = ui.draw_results_on_image(warped_image, student_answers, correct_answers, results, all_coords)
        score_image = ui.create_score_display(final_score, num_correct, len(correct_answers))
    else:
        print("--> Không có tọa độ trắc nghiệm, bỏ qua phần chấm OMR.")
        result_image = warped_image.copy()
        score_image = ui.create_score_display(0, 0, 0)

    # --- OCR Section ---
    ocr_data = ocr_logic.extract_text_from_regions(outside_image, ocr_regions)

    # --- Finalization ---
    ui.save_output_files(result_image, score_image, ocr_data, outside_image, output_dir=output_dir)

    # Return the results for potential UI display later
    return result_image, score_image, ocr_data


def process_single_file(file_path, output_dir, anchors, regions):
    """
    Processes a single file (PDF or image) from path to result.

    Args:
        file_path (str): Path to the input file.
        output_dir (str): Path to the directory to save results.
        anchors (list): Coordinates for the OMR answer block.
        regions (dict): Coordinates for OCR regions.
    """
    print(f"\n--- Bắt đầu xử lý file: {os.path.basename(file_path)} ---")
    
    file_type = utils.get_file_type(file_path)
    
    if file_type == 'pdf':
        warped_img, outside_img = pre_processing.get_warped_image_from_pdf(file_path, config.STANDARD_SIZE)
    elif file_type in ['png', 'jpg', 'jpeg']:
        warped_img, outside_img = pre_processing.get_warped_image_from_image(file_path, config.STANDARD_SIZE)
    else:
        print(f"Lỗi: Định dạng file không được hỗ trợ: {file_type}. Bỏ qua.")
        return None, None, None

    if warped_img is None:
        print(f"Lỗi: Không thể xử lý ảnh từ file: {file_path}. Bỏ qua.")
        return None, None, None

    # Run the main grading process
    return run_grading_process(anchors, regions, warped_img, outside_img, output_dir)


if __name__ == "__main__":
    """
    Main entry point of the application.
    Handles initial setup and runs the grading process in single or batch mode.
    """
    # Ensure the base output directory exists
    if not os.path.exists(config.OUTPUT_PATH):
        os.makedirs(config.OUTPUT_PATH)

    anchors = []
    regions = {}

    # Coordinate setup is a one-time step, required for both modes
    if not os.path.exists(config.COORDINATES_PATH):
        if ui.prompt_coordinate_setup():
            # Use the single PDF path for the initial setup
            _, _, _, _ = measure_tool.get_coordinates_from_user_selection(
                pdf_path=config.PDF_PATH,
                coord_save_path=config.COORDINATES_PATH
            )
        else:
            print("Chương trình không thể tiếp tục nếu không có tọa độ. Đang thoát...")
            sys.exit()

    # Load the essential coordinates and regions
    try:
        print(f"--> Đang tải tọa độ từ: {config.COORDINATES_PATH}")
        with open(config.COORDINATES_PATH, 'r') as f:
            data = json.load(f)
        anchors = data.get(config.KEY_BUBBLE_ANCHORS, [])
        regions = data.get(config.KEY_OCR_REGIONS, {})
        if not anchors:
            raise ValueError(f"File tọa độ không hợp lệ: thiếu '{config.KEY_BUBBLE_ANCHORS}'.")
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Lỗi nghiêm trọng khi đọc file tọa độ: {e}")
        print(f"Vui lòng xóa file '{config.COORDINATES_PATH}' và chạy lại để thiết lập từ đầu.")
        sys.exit()

    # --- Mode Selection ---
    if config.BATCH_MODE:
        print("\n--- CHẾ ĐỘ XỬ LÝ HÀNG LOẠT ĐƯỢỢC KÍCH HOẠT ---")
        # Ensure batch input and output directories exist
        if not os.path.isdir(config.BATCH_INPUT_DIR):
            print(f"Lỗi: Thư mục đầu vào cho xử lý hàng loạt '{config.BATCH_INPUT_DIR}' không tồn tại.")
            sys.exit()
        if not os.path.exists(config.BATCH_OUTPUT_DIR):
            os.makedirs(config.BATCH_OUTPUT_DIR)

        # Get all supported files from the batch input directory
        supported_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
        files_to_process = [f for f in os.listdir(config.BATCH_INPUT_DIR) if f.lower().endswith(tuple(supported_extensions))]
        
        if not files_to_process:
            print(f"Không tìm thấy file nào được hỗ trợ trong '{config.BATCH_INPUT_DIR}'.")
        else:
            print(f"Tìm thấy {len(files_to_process)} file để xử lý.")
            for filename in files_to_process:
                file_path = os.path.join(config.BATCH_INPUT_DIR, filename)
                # Create a unique output directory for each file
                file_basename = os.path.splitext(filename)[0]
                specific_output_dir = os.path.join(config.BATCH_OUTPUT_DIR, file_basename)
                
                process_single_file(file_path, specific_output_dir, anchors, regions)
            print("\n--- XỬ LÝ HÀNG LOẠT HOÀN TẤT ---")

    else:
        print("\n--- CHẾ ĐỘ XỬ LÝ MỘT FILE ---")
        # Process the single file specified in the config
        result_img, score_img, ocr_data = process_single_file(
            config.PDF_PATH, 
            config.OUTPUT_PATH, 
            anchors, 
            regions
        )

        # Show results only in single file mode
        if result_img is not None and score_img is not None:
            ui.show_final_results(result_img, score_img, ocr_data)
