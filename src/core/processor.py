import cv2
import os
from src.utils.image_utils import ImageUtils
from src.core.omr_engine import OMREngine
# 1. IMPORT OCR ENGINE (Thêm dòng này)
from src.core.ocr_engine import OCREngine 

class Processor:
    def __init__(self, config):
        self.cfg = config
        self.img_utils = ImageUtils(config)
        self.omr = OMREngine(config)
        
        # 2. KHỞI TẠO OCR ENGINE (Thêm dòng này)
        # Lưu ý: OCR Engine sẽ in ra cái bảng "KHỞI TẠO HỆ THỐNG OCR KÉP" lúc này
        self.ocr_engine = OCREngine(config.OCR)

    def process_exam_paper(self, image_path, template_data, correct_answers=None):
        """
        Quy trình xử lý một bài thi
        """
        # 1. Đọc ảnh
        original_img = cv2.imread(image_path)
        if original_img is None:
            raise ValueError(f"Không thể đọc ảnh: {image_path}")

        # 2. Tiền xử lý & Căn chỉnh (Warping)
        warped_img = self.img_utils.warp_document(original_img)
        
        results = {}

        # 3. CHẤM ĐIỂM TRẮC NGHIỆM (Giữ nguyên)
        if "answer_bubbles" in template_data:
            user_answers, score = self.omr.grade_exam(warped_img, template_data["answer_bubbles"], correct_answers)
            results["answers"] = user_answers
            results["score_raw"] = score

        # 4. [NÂNG CẤP] GỌI OCR ENGINE (Thay thế phần cắt ảnh cũ)
        # Lấy vùng cần đọc chữ từ file template (info_regions hoặc info_fields)
        # Lưu ý: Trong file template json của bạn, key nên là "info_fields" hoặc "ocr_regions"
        # Ở đây tôi dùng 'info_fields' cho khớp với code cũ của bạn
        ocr_regions = template_data.get("info_fields", {})

        print(f"DEBUG: Tìm thấy {len(ocr_regions)} vùng để nhận dạng OCR.")

        # Gọi hàm Dual-Mode OCR (Đây là chỗ nó sẽ in ra bảng so sánh)
        extracted_info = self.ocr_engine.extract_text_from_regions(warped_img, ocr_regions)
        
        # Lưu lại ảnh cắt nhỏ để debug (nếu cần)
        results["info_images"] = {}
        for key, text in extracted_info.items():
            if key in ocr_regions:
                x, y, w, h = ocr_regions[key]
                if y+h <= warped_img.shape[0] and x+w <= warped_img.shape[1]:
                    results["info_images"][key] = warped_img[y:y+h, x:x+w]

        # 5. ĐÓNG GÓI KẾT QUẢ
        # Ưu tiên lấy SBD từ OCR (vì model custom của bạn xịn hơn chấm tròn)
        # Nếu OCR đọc ra số, dùng số đó. Nếu không, fallback về logic cũ (omr.process_sbd)
        
        sbd_ocr = extracted_info.get("sbd_box", "") # Thay "sbd_box" bằng tên key trong json của bạn (ví dụ "sbd")
        if not sbd_ocr and "mssv_bubbles" in template_data:
             # Fallback: Nếu OCR tạch thì dùng chấm tròn
            sbd_ocr = self.omr.process_sbd(warped_img, template_data["mssv_bubbles"])
        
        results["sbd"] = sbd_ocr
        results["class_id"] = extracted_info.get("class_box", "Unknown") # Ví dụ
        
        return results, warped_img