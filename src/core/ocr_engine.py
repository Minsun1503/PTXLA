import cv2
import easyocr
import re
import numpy as np
from typing import Dict, List
from config import Config


class OCREngine:
    """
    Handles the core Optical Character Recognition (OCR) logic.
    Includes Post-processing (Regex Validation) to clean data.
    """

    def __init__(self, ocr_config: Config.OCRConfig):
        """
        Initializes the OCR engine and EasyOCR model.
        """
        print("Initializing EasyOCR reader... (This may take a moment)")
        # GPU=False để chạy ổn định trên mọi máy, nếu có GPU mạnh thì set True
        self.reader = easyocr.Reader(ocr_config.OCR_LANGUAGES, gpu=False)
        self.cfg = ocr_config
        print("EasyOCR reader initialized.")

    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Tiền xử lý ảnh trước khi đưa vào OCR:
        - Chuyển xám
        - Khử nhiễu
        - Phân ngưỡng (Threshold) để chữ đen rõ ràng trên nền trắng
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Dùng Otsu Threshold để tự động tách chữ khỏi nền giấy
        # Thresh Binary: Chữ đen (0), Nền trắng (255)
        # Lưu ý: EasyOCR thích nền trắng chữ đen hoặc ngược lại đều được, 
        # nhưng ảnh sạch sẽ tốt hơn.
        processed_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # (Tuỳ chọn) Dilation nhẹ nếu chữ quá mảnh
        # kernel = np.ones((2,2), np.uint8)
        # processed_image = cv2.erode(processed_image, kernel, iterations=1)

        return processed_image

    def _post_process_text(self, key_name: str, raw_text: str) -> str:
        """
        [NÂNG CẤP] Hàm hậu xử lý (Validation/Cleaning)
        Dựa vào tên trường (key_name) để áp dụng Regex phù hợp.
        """
        text = raw_text.strip()

        # 1. Nếu là SBD hoặc ID -> Chỉ giữ lại số
        if "sbd" in key_name.lower() or "id" in key_name.lower() or "code" in key_name.lower():
            # Regex: \D nghĩa là "non-digit". Thay thế tất cả ký tự không phải số bằng ""
            clean_text = re.sub(r'\D', '', text)
            return clean_text

        # 2. Nếu là Tên (Name) -> Chuẩn hoá viết hoa chữ cái đầu (Title Case)
        if "name" in key_name.lower() or "ten" in key_name.lower():
            # Xoá ký tự đặc biệt, chỉ giữ chữ và khoảng trắng
            clean_text = re.sub(r'[^\w\s]', '', text) 
            return clean_text.title() # Ví dụ: "nguyen VAN a" -> "Nguyen Van A"

        # 3. Mặc định -> Chỉ xoá khoảng trắng thừa
        return re.sub(r'\s+', ' ', text)

    def extract_text_from_regions(self, image: np.ndarray, ocr_regions: Dict[str, List[int]]) -> Dict[str, str]:
        """
        Cắt ảnh theo toạ độ và đọc chữ.
        """
        if not ocr_regions:
            return {}

        extracted_data = {}

        for region_name, coords in ocr_regions.items():
            if len(coords) != 4:
                continue

            x, y, w, h = coords
            # Cắt vùng ảnh (ROI)
            roi = image[y:y+h, x:x+w]

            if roi.size == 0:
                extracted_data[region_name] = ""
                continue

            # 1. Tiền xử lý ảnh
            processed_roi = self._preprocess_for_ocr(roi)

            # 2. Đọc bằng EasyOCR
            # paragraph=True giúp gộp các từ lại thành dòng
            ocr_result = self.reader.readtext(
                processed_roi,
                detail=0,
                paragraph=True
                # allowlist=self.cfg.ALLOW_LIST # Có thể dùng hoặc không
            )

            # 3. Gộp kết quả
            raw_text = ' '.join(ocr_result) if ocr_result else ""

            # 4. Hậu xử lý (Validate & Clean) - "Vũ khí" để báo cáo
            final_text = self._post_process_text(region_name, raw_text)

            extracted_data[region_name] = final_text

            # Debug log
            print(f"  > OCR '{region_name}': Raw='{raw_text}' -> Clean='{final_text}'")

        return extracted_data
