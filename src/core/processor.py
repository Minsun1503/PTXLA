import cv2
import os
from src.utils.image_utils import ImageUtils
from src.core.omr_engine import OMREngine

class Processor:
    def __init__(self, config):
        self.cfg = config
        self.img_utils = ImageUtils(config)
        self.omr = OMREngine(config)

    def process_exam_paper(self, image_path, template_data, correct_answers=None):
        """
        Quy trình xử lý một bài thi
        """
        # 1. Đọc ảnh
        original_img = cv2.imread(image_path)
        if original_img is None:
            raise ValueError(f"Không thể đọc ảnh: {image_path}")

        # 2. Tiền xử lý & Căn chỉnh (Warping)
        # Lưu ý: Hàm warp_document cần trả về ảnh đã resize về chuẩn (1000x1400)
        warped_img = self.img_utils.warp_document(original_img)
        
        # Debug: Lưu ảnh đã warp để kiểm tra
        # cv2.imwrite("debug_warped.jpg", warped_img)

        results = {}

        # 3. TRÍCH XUẤT THÔNG TIN (Info Fields) - MỚI
        # Cắt các vùng ảnh chứa tên, lớp, trường... để người dùng kiểm tra
        if "info_fields" in template_data:
            results["info_images"] = {}
            for field_name, rect in template_data["info_fields"].items():
                x, y, w, h = rect
                # Cắt ảnh (Crop)
                # Lưu ý kiểm tra biên để không crash
                if y+h <= warped_img.shape[0] and x+w <= warped_img.shape[1]:
                    roi = warped_img[y:y+h, x:x+w]
                    results["info_images"][field_name] = roi
        
        # 4. ĐỌC SỐ BÁO DANH (SBD) - MỚI
        if "mssv_bubbles" in template_data:
            sbd = self.omr.process_sbd(warped_img, template_data["mssv_bubbles"])
            results["sbd"] = sbd
        else:
            results["sbd"] = "N/A"

        # 5. CHẤM ĐIỂM TRẮC NGHIỆM
        if "answer_bubbles" in template_data:

            user_answers, score = self.omr.grade_exam(warped_img, template_data["answer_bubbles"], correct_answers)
            
            results["answers"] = user_answers
            results["score_raw"] = score # Điểm thô (số câu đúng)
        
        return results, warped_img