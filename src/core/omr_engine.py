import cv2
import numpy as np
from config import Config

class OMREngine:
    """
    Handles the core Optical Mark Recognition (OMR) logic for grading bubble sheets.
    Uses Adaptive Thresholding to handle uneven lighting and shadows.
    """

    def __init__(self, config=None):
        if config:
            self.cfg = config
        else:
            self.cfg = Config()

    def _apply_adaptive_threshold(self, img):
        """
        Hàm xử lý ảnh nhị phân thông minh: Chống bóng đổ và ánh sáng không đều.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # ADAPTIVE_THRESH_GAUSSIAN_C: Tính ngưỡng dựa trên vùng lân cận
        # Block Size = 51: Xem xét vùng 51x51 pixel
        # C = 10: Hằng số trừ đi để lọc nhiễu nền
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 51, 10
        )
        return thresh

    def grade_exam(self, warped_img, answers_bubbles, correct_answers=None):
        """
        Chấm điểm phần trắc nghiệm (Answer Section)
        """
        # Sử dụng Adaptive Threshold thay vì Global Threshold
        thresh = self._apply_adaptive_threshold(warped_img)

        user_answers = {}
        score = 0
        
        for i, question_bubbles in enumerate(answers_bubbles):
            chosen_idx = self._get_marked_bubble(thresh, question_bubbles)
            user_answers[i] = chosen_idx

            if correct_answers and i < len(correct_answers):
                if chosen_idx == correct_answers[i]:
                    score += 1

        return user_answers, score

    def process_sbd(self, warped_img, sbd_bubbles):
        """
        Đọc Mã Số Sinh Viên (SBD Section)
        """
        # Cũng dùng Adaptive Threshold cho SBD để đọc chính xác hơn
        thresh = self._apply_adaptive_threshold(warped_img)

        sbd_str = ""
        for col_bubbles in sbd_bubbles:
            chosen_idx = self._get_marked_bubble(thresh, col_bubbles)
            if chosen_idx != -1:
                sbd_str += str(chosen_idx)
            else:
                sbd_str += "?" 

        return sbd_str

    def _get_marked_bubble(self, binary_img, bubbles_coords):
        """
        Tìm ô được tô đậm nhất.
        """
        max_pixels = 0
        chosen_idx = -1
        
        # Lấy tham số từ Config (đã cập nhật)
        min_pixels = self.cfg.OMR.PIXEL_THRESHOLD
        radius = self.cfg.OMR.SCAN_RADIUS

        h, w = binary_img.shape[:2]

        for idx, (cx, cy) in enumerate(bubbles_coords):
            # Kiểm tra biên an toàn (tránh lỗi crash nếu toạ độ sát mép)
            if cx < radius or cx >= w - radius or cy < radius or cy >= h - radius:
                continue

            mask = np.zeros(binary_img.shape, dtype=np.uint8)
            cv2.circle(mask, (cx, cy), radius, 255, -1)
            
            pixel_count = cv2.countNonZero(cv2.bitwise_and(binary_img, binary_img, mask=mask))
            
            if pixel_count > max_pixels:
                max_pixels = pixel_count
                chosen_idx = idx
        
        if max_pixels < min_pixels:
            return -1 
            
        return chosen_idx