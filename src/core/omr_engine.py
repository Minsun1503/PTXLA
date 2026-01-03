import cv2
import numpy as np
from config import Config

class OMREngine:
    def __init__(self, config=None):
        if config:
            self.cfg = config
        else:
            self.cfg = Config()

    def grade_exam(self, warped_img, answers_bubbles, correct_answers=None):
        """
        Chấm điểm phần trắc nghiệm (Answer Section)
        """
        gray = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        user_answers = {}
        score = 0
        total_questions = len(answers_bubbles)
        
        # Duyệt qua từng câu hỏi
        for i, question_bubbles in enumerate(answers_bubbles):
            # Tìm ô được tô trong câu hỏi này
            chosen_idx = self._get_marked_bubble(thresh, question_bubbles)
            
            # Lưu kết quả (0=A, 1=B, 2=C, 3=D, -1=Không tô)
            user_answers[i] = chosen_idx

            # Tính điểm (nếu có đáp án chuẩn)
            if correct_answers and i in correct_answers:
                if chosen_idx == correct_answers[i]:
                    score += 1

        return user_answers, score

    def process_sbd(self, warped_img, sbd_bubbles):
        """
        Đọc Mã Số Sinh Viên (SBD Section)
        sbd_bubbles: List[List[[x,y]]] - Ma trận toạ độ các cột SBD
        """
        gray = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)
        # Nhị phân hoá: Nền đen (0), Nét/Tô trắng (255)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        sbd_str = ""
        
        # Duyệt qua từng CỘT số (Mỗi cột là 1 chữ số của SBD)
        for col_bubbles in sbd_bubbles:
            # col_bubbles chứa 10 toạ độ [0, 1, ..., 9] của cột đó
            chosen_idx = self._get_marked_bubble(thresh, col_bubbles)
            
            if chosen_idx != -1:
                sbd_str += str(chosen_idx)
            else:
                sbd_str += "?" # Không đọc được hoặc không tô

        return sbd_str

    def _get_marked_bubble(self, binary_img, bubbles_coords):
        """
        Hàm phụ trợ: Tìm ô được tô đậm nhất trong một list các ô
        """
        max_pixels = 0
        chosen_idx = -1
        
        # Ngưỡng pixel để xác nhận là "đã tô"
        # Cần tinh chỉnh tuỳ vào độ phân giải ảnh (ví dụ: > 30% diện tích ô)
        MIN_PIXEL_THRESHOLD = 100 

        for idx, (cx, cy) in enumerate(bubbles_coords):
            # Tạo mask cho ô tròn hiện tại
            mask = np.zeros(binary_img.shape, dtype=np.uint8)
            radius = 9 # Bán kính mask (lớn hơn bán kính vẽ một chút để bao trọn)
            cv2.circle(mask, (cx, cy), radius, 255, -1)
            
            # Đếm số pixel trắng (được tô) trong vùng mask
            # bitwise_and giữa ảnh nhị phân và mask
            pixel_count = cv2.countNonZero(cv2.bitwise_and(binary_img, binary_img, mask=mask))
            
            if pixel_count > max_pixels:
                max_pixels = pixel_count
                chosen_idx = idx
        
        # Kiểm tra lại ngưỡng (tránh trường hợp nhiễu nhỏ cũng tính là tô)
        if max_pixels < MIN_PIXEL_THRESHOLD:
            return -1 # Coi như không tô
            
        return chosen_idx