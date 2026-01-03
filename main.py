import os
import cv2
from config import Config
from src.utils import file_io
from src.core.processor import Processor


def main():
    # 1. Khởi tạo
    cfg = Config()
    processor = Processor(cfg)

    # 2. Load Template (Toạ độ JSON)
    template_path = cfg.Paths.COORDINATES_PATH
    if not os.path.exists(template_path):
        print(f"Lỗi: Không tìm thấy file template tại {template_path}")
        print("Hãy chạy 'python tools/generate_sheet.py' trước!")
        return

    template_data = file_io.load_json(template_path)
    print("--> Template loaded successfully.")

    # 3. Load Answer Key
    correct_answers = file_io.load_answer_key_from_csv(
        cfg.Paths.ANSWER_KEY_PATH, cfg.OMR.ANSWER_MAP
    )
    if correct_answers is None:
        print("Error: Could not load answers, please check answer_key.csv")
        return

    # 4. Lấy danh sách ảnh đầu vào
    input_dir = cfg.Paths.BATCH_INPUT_DIR
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    if not image_files:
        print(f"Warning: No images found in directory {input_dir}")
        return

    print(f"--> Found {len(image_files)} exams to grade.")
    print("-" * 50)

    # 5. Vòng lặp xử lý từng bài thi
    output_dir = cfg.Paths.BATCH_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    for img_name in image_files:
        img_path = os.path.join(input_dir, img_name)
        print(f"Processing: {img_name}...")

        try:
            # GỌI PROCESSOR
            results, warped_img = processor.process_exam_paper(
                img_path, template_data, correct_answers
            )

            # --- HIỂN THỊ KẾT QUẢ ---
            sbd = results.get("sbd", "Unknown")
            print(f"   + SBD (Student ID): {sbd}")
            print(f"   + Number of answers: {len(results.get('answers', {}))}")
            print(f"   + Raw score: {results.get('score_raw', 0)}")

            # --- LƯU ẢNH KẾT QUẢ ---
            # 1. Lưu ảnh bài thi đã chấm (Warped)
            base_name = os.path.splitext(img_name)[0]
            save_path = os.path.join(output_dir, f"{base_name}_result.jpg")
            cv2.imwrite(save_path, warped_img)

            # 2. Lưu ảnh cắt các trường thông tin (để kiểm tra chữ viết tay)
            info_dir = os.path.join(output_dir, base_name + "_info")
            os.makedirs(info_dir, exist_ok=True)

            if "info_images" in results:
                for key, roi_img in results["info_images"].items():
                    cv2.imwrite(os.path.join(info_dir, f"{key}.jpg"), roi_img)

            print(f"   --> Results saved at: {output_dir}")

        except Exception as e:
            print(f"   !!! Error processing {img_name}: {str(e)}")
            import traceback
            traceback.print_exc()

    print("-" * 50)
    print("COMPLETE!")


if __name__ == "__main__":
    main()
