import os
import cv2
from config import Config
from src.utils import file_io
from src.core.processor import Processor
from src.view import renderer  # Bổ sung import module renderer

# Map ngược từ số sang chữ để in log cho dễ đọc (0->A, 1->B...)
INDEX_TO_CHAR = {0: 'A', 1: 'B', 2: 'C', 3: 'D', -1: 'N/A'}

def main():
    # 1. Khởi tạo
    cfg = Config()
    processor = Processor(cfg)

    # 2. Load Template
    template_path = cfg.Paths.COORDINATES_PATH
    if not os.path.exists(template_path):
        print(f"Lỗi: Không tìm thấy file template tại {template_path}")
        return
    template_data = file_io.load_json(template_path)
    print("--> Template loaded successfully.")

    # 3. Load Answer Key
    correct_answers = file_io.load_answer_key_from_csv(
        cfg.Paths.ANSWER_KEY_PATH, cfg.OMR.ANSWER_MAP
    )
    if correct_answers is None:
        print("Error: Could not load answers.")
        return

    # 4. Lấy ảnh input
    input_dir = cfg.Paths.BATCH_INPUT_DIR
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not image_files:
        print(f"Warning: No images found in {input_dir}")
        return

    print(f"--> Found {len(image_files)} exams.")
    print("-" * 50)

    # 5. Xử lý
    output_dir = cfg.Paths.BATCH_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    for img_name in image_files:
        img_path = os.path.join(input_dir, img_name)
        print(f"\nProcessing: {img_name}...")
        
        try:
            # Gọi Processor để xử lý logic chấm điểm và OCR
            results, warped_img = processor.process_exam_paper(
                img_path, template_data, correct_answers
            )

            # --- CHUẨN BỊ DỮ LIỆU ĐỂ VẼ (RENDER) ---
            user_ans_dict = results.get('answers', {})
            user_ans_list = []
            results_bool_list = []
            
            print("\n [DETAILED REPORT]")
            for i, correct_idx in enumerate(correct_answers):
                user_idx = user_ans_dict.get(i, -1)
                user_ans_list.append(user_idx)
                
                # Kiểm tra đúng sai
                is_correct = (user_idx == correct_idx)
                results_bool_list.append(is_correct)
                
                user_char = INDEX_TO_CHAR.get(user_idx, '?')
                correct_char = INDEX_TO_CHAR.get(correct_idx, '?')
                status = "✅" if is_correct else f"❌ (Expected: {correct_char})"
                if user_idx == -1: status = "⚪ BLANK"
                print(f" Q{i+1:02}: You: {user_char} | Key: {correct_char} -> {status}")

            sbd = results.get("sbd", "Unknown")
            raw_score = results.get('score_raw', 0)
            final_score = (raw_score / len(correct_answers)) * 10 # Tính thang điểm 10

            print(f"\n + SBD: {sbd}")
            print(f" + Raw Score: {raw_score} / {len(correct_answers)}")
            print(f" + Final Score: {final_score:.2f} / 10")

            # --- BƯỚC VẼ KẾT QUẢ (RENDER VIEW) ---
            # 1. Vẽ vòng tròn xanh/đỏ lên ảnh phiếu thi
            marked_img = renderer.draw_results_on_image(
                warped_img,
                user_ans_list,
                correct_answers,
                results_bool_list,
                template_data.get('answer_bubbles', []),
                cfg.OMR
            )

            # 2. Tạo ảnh bảng điểm (score.png)
            score_card = renderer.create_score_display(
                final_score, raw_score, len(correct_answers)
            )

            # --- LƯU KẾT QUẢ THEO ĐÚNG CẤU HÌNH BÁO CÁO ---
            base_name = os.path.splitext(img_name)
            
            # Lưu ảnh phiếu thi đã chấm (scoring_result.png)
            res_name = f"{base_name}_{cfg.Paths.SCORING_RESULT_IMAGE_NAME}"
            cv2.imwrite(os.path.join(output_dir, res_name), marked_img)
            
            # Lưu bảng điểm (score.png)
            score_name = f"{base_name}_{cfg.Paths.SCORE_IMAGE_NAME}"
            cv2.imwrite(os.path.join(output_dir, score_name), score_card)

            # Lưu các ảnh ROI thông tin (Name, Class...)
            info_dir = os.path.join(output_dir, base_name + "_info")
            os.makedirs(info_dir, exist_ok=True)
            if "info_images" in results:
                for key, roi_img in results["info_images"].items():
                    cv2.imwrite(os.path.join(info_dir, f"{key}.jpg"), roi_img)

            print(f" --> Saved results to {output_dir}")

        except Exception as e:
            print(f" !!! Error: {str(e)}")
            import traceback
            traceback.print_exc()

    print("-" * 50)
    print("COMPLETE!")

if __name__ == "__main__":
    main()