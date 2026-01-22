import cv2
import easyocr
import re
import os
import numpy as np
from typing import Dict, List
from config import Config

class OCREngine:
    """
    Engine xử lý nhận dạng chữ (OCR) với chế độ Dual-Mode:
    Kết hợp giữa Model Pre-trained (Gốc) và Model Fine-tuned (Custom).
    """

    def __init__(self, ocr_config: Config.OCRConfig):
        print("="*50)
        print("🛠️  KHỞI TẠO HỆ THỐNG OCR KÉP (DUAL-MODE)")
        print("="*50)

        # --- 1. LOAD MODEL GỐC (DEFAULT) ---
        print("1️⃣  Đang load Model Gốc (Online/Pretrained)...")
        try:
            self.reader_default = easyocr.Reader(['vi'], gpu=False)
            print("   ✅ Model Gốc: Sẵn sàng.")
        except Exception as e:
            print(f"   ❌ Lỗi load Model Gốc: {e}")
            self.reader_default = None

        # --- 2. LOAD MODEL CUSTOM (FINE-TUNED) ---
        print("2️⃣  Đang load Model Custom (Fine-tuned)...")
        current_dir = os.getcwd()
        model_dir = os.path.join(current_dir, "custom_model")
        
        # --- CẤU HÌNH TÊN FILE MODEL Ở ĐÂY ---
        CUSTOM_NAME = 'ckt_79'

        pth_path = os.path.join(model_dir, f"{CUSTOM_NAME}.pth")
        if os.path.exists(pth_path):
            try:
                self.reader_custom = easyocr.Reader(
                    lang_list=['vi'],
                    gpu=False,
                    model_storage_directory=model_dir,
                    user_network_directory=model_dir,
                    recog_network=CUSTOM_NAME
                )
                self.has_custom = True
                print(f"   ✅ Model Custom: Sẵn sàng ({CUSTOM_NAME})")
            except Exception as e:
                print(f"   ❌ Lỗi load Model Custom: {e}")
                self.has_custom = False
        else:
            self.has_custom = False
            print(f"   ⚠️ CẢNH BÁO: Không tìm thấy file {CUSTOM_NAME}.pth tại {model_dir}")

        self.cfg = ocr_config
        print("="*50 + "\n")

    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Chuyển ảnh xám và phân ngưỡng Otsu"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        processed_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        return processed_image

    def _post_process_text(self, key_name: str, raw_text: str) -> str:
        """Làm sạch dữ liệu bằng Regex"""
        text = raw_text.strip()
        # Chỉ giữ số cho SBD và ID
        if "sbd" in key_name.lower() or "id" in key_name.lower():
            return re.sub(r'\D', '', text) 
        # Chuẩn hóa Tên
        if "name" in key_name.lower():
            clean = re.sub(r'[^\w\s]', '', text)
            return clean.title()
        # Mặc định
        return re.sub(r'\s+', ' ', text)

    def extract_text_from_regions(self, image: np.ndarray, ocr_regions: Dict[str, List[int]]) -> Dict[str, str]:
        """
        Trích xuất văn bản từ các vùng ảnh.
        IN RA BẢNG SO SÁNH GIỮA 2 MODEL.
        """
        if not ocr_regions: 
            return {}
        
        extracted_data = {}

        # --- HEADER BẢNG SO SÁNH ---
        print(f"\n--- 🔍 KẾT QUẢ SO SÁNH OCR ({len(ocr_regions)} vùng) ---")
        # Format cột cho thẳng hàng: Vùng (15 ký tự), Gốc (25 ký tự), Custom (25 ký tự)
        print(f"{'VÙNG (ROI)':<15} | {'MODEL GỐC':<25} | {'MODEL CUSTOM (TRAINED)':<25}")
        print("-" * 75)
	
        PADDING_X = 0
        PADDING_Y = 15

        for region_name, coords in ocr_regions.items():
            if len(coords) != 4: continue
            x, y, w, h = coords
            
            # --- 1. TÍNH TỌA ĐỘ MỚI (Nới rộng) ---
            img_h, img_w = image.shape[:2]
            
            x_new = max(0, x - PADDING_X)
            y_new = max(0, y - PADDING_Y)
            w_new = w + (2 * PADDING_X)
            h_new = h + (2 * PADDING_Y)
            
            # Đảm bảo không tràn viền ảnh gốc
            if x_new + w_new > img_w: w_new = img_w - x_new
            if y_new + h_new > img_h: h_new = img_h - y_new
            
            # --- 2. CẮT ẢNH THEO TỌA ĐỘ MỚI ---
            roi = image[y_new:y_new+h_new, x_new:x_new+w_new]
            
            # Kiểm tra an toàn
            if roi.size == 0: continue

            # --- 3. TIẾP TỤC XỬ LÝ ---
            # Tiền xử lý (Quan trọng cho Model Custom)
            processed_roi = self._preprocess_for_ocr(roi)

            # --- 1. CHẠY MODEL GỐC ---
            text_default = "N/A"
            if self.reader_default:
                res_default = self.reader_default.readtext(processed_roi, detail=0, paragraph=True)
                text_default = ' '.join(res_default) if res_default else ""

            # --- 2. CHẠY MODEL CUSTOM ---
            text_custom = "N/A"
            if self.has_custom:
                res_custom = self.reader_custom.readtext(processed_roi, detail=0, paragraph=True)
                text_custom = ' '.join(res_custom) if res_custom else ""

            # --- 3. IN KẾT QUẢ RA MÀN HÌNH ---
            # Cắt ngắn text nếu quá dài để không vỡ bảng
            display_default = (text_default[:22] + '..') if len(text_default) > 22 else text_default
            display_custom = (text_custom[:22] + '..') if len(text_custom) > 22 else text_custom
            
            print(f"{region_name:<15} | {display_default:<25} | {display_custom:<25}  <--")

            # --- 4. CHỌN KẾT QUẢ ĐỂ LƯU ---
            # Ưu tiên Custom Model nếu có, nếu không dùng Default
            raw_text_to_use = text_custom if self.has_custom else text_default
            
            # Hậu xử lý (Regex)
            final_text = self._post_process_text(region_name, raw_text_to_use)
            extracted_data[region_name] = final_text

        print("-" * 75 + "\n")
        return extracted_data