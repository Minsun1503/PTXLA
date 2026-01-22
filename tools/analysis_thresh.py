import sys
import os
import matplotlib.pyplot as plt
import numpy as np

# Thêm đường dẫn để import được các module trong src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config
from src.core.processor import Processor
from src.utils import file_io

def run_tuning():
    print("--- BẮT ĐẦU TỐI ƯU HÓA NGƯỠNG PIXEL (TUNING) ---")
    
    # 1. Cấu hình
    cfg = Config()
    processor = Processor(cfg)
    
    # [SỬA LỖI TẠI ĐÂY] Thêm tham số thứ 2: cfg.OMR.ANSWER_MAP
    answers = file_io.load_answer_key_from_csv(cfg.Paths.ANSWER_KEY_PATH, cfg.OMR.ANSWER_MAP)
    
    # Danh sách các ngưỡng muốn test
    thresholds = [120, 140, 160, 180, 200, 220, 240]
    
    # Chỉ test trên các Case khó
    test_images = ['case_2.jpg', 'case_4.jpg'] 
    
    results = []

    for thresh in thresholds:
        print(f"\n>> Testing with THRESHOLD = {thresh}...")
        
        # Ghi đè cấu hình ngay trong bộ nhớ
        cfg.OMR.PIXEL_THRESHOLD = thresh
        processor.omr_engine.cfg.PIXEL_THRESHOLD = thresh 
        
        total_correct = 0
        total_questions = 0
        
        for img_name in test_images:
            img_path = os.path.join(cfg.Paths.BATCH_INPUT_DIR, img_name)
            if not os.path.exists(img_path):
                continue
                
            # Chạy xử lý
            try:
                grading_result, _ = processor.process_exam_paper(img_path, answers)
                total_correct += grading_result['score_data']['total_correct']
                total_questions += grading_result['score_data']['total_questions']
            except Exception as e:
                print(f"   Lỗi khi xử lý {img_name}: {e}")

        # Tính độ chính xác trung bình
        accuracy = (total_correct / total_questions) * 100 if total_questions > 0 else 0
        results.append(accuracy)
        print(f"   -> Accuracy: {accuracy:.2f}%")

    # 2. Vẽ biểu đồ đường (Line Chart)
    plt.figure(figsize=(10, 6))
    plt.plot(thresholds, results, marker='o', linestyle='-', color='#e67e22', linewidth=2)
    
    plt.title('Ảnh hưởng của ngưỡng Pixel Threshold đến độ chính xác', fontsize=13)
    plt.xlabel('Giá trị ngưỡng (Pixel Threshold)', fontsize=12)
    plt.ylabel('Độ chính xác (%)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(thresholds)
    plt.ylim(0, 105)
    
    # Đánh dấu điểm cao nhất
    if len(results) > 0:
        max_acc = max(results)
        best_thresh = thresholds[results.index(max_acc)]
        plt.annotate(f'Best: {best_thresh} ({max_acc:.1f}%)', 
                     xy=(best_thresh, max_acc), xytext=(best_thresh, max_acc + 5),
                     arrowprops=dict(facecolor='black', shrink=0.05),
                     ha='center')

    # Lưu ảnh
    output_path = os.path.join(os.path.dirname(__file__), '../report/images/threshold_tuning.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    print(f"\n✅ Đã lưu biểu đồ tại: {output_path}")
    
    # Chỉ show nếu có màn hình (tránh lỗi trên server không có GUI)
    try:
        plt.show()
    except:
        pass

if __name__ == "__main__":
    run_tuning()