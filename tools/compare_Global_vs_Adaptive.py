import cv2
import matplotlib.pyplot as plt
import numpy as np
import os

def process_real_image(image_path):
    # Kiểm tra xem file có tồn tại không
    if not os.path.exists(image_path):
        print(f"LỖI: Không tìm thấy file ảnh tại: {image_path}")
        print("Vui lòng thay đổi đường dẫn ảnh trong biến 'IMAGE_PATH' ở cuối code.")
        return

    # 1. Đọc ảnh từ đường dẫn
    # Đọc ảnh màu để hiển thị cho đẹp ở bước 1
    img_bgr = cv2.imread(image_path)
    
    # Chuyển sang ảnh xám (Grayscale) - Bắt buộc cho Thresholding
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # --- CÁCH 1: GLOBAL THRESHOLDING (OTSU) ---
    # Thuật toán tự tìm 1 ngưỡng duy nhất cho toàn bộ ảnh
    ret_otsu, global_thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # --- CÁCH 2: ADAPTIVE GAUSSIAN THRESHOLDING (CÁCH CỦA BẠN) ---
    # Block Size = 51 (Kích thước vùng lân cận để tính trung bình)
    # C = 10 (Hằng số trừ đi để lọc nhiễu)
    # Các thông số này khớp với báo cáo của bạn
    adaptive_thresh = cv2.adaptiveThreshold(
        img_gray, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        51, 10
    )

    # --- HIỂN THỊ KẾT QUẢ ---
    plt.figure(figsize=(15, 6))

    # 1. Ảnh gốc
    plt.subplot(1, 3, 1)
    # Matplotlib dùng RGB, OpenCV dùng BGR nên phải chuyển đổi để hiển thị đúng màu
    plt.imshow(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    plt.title("1. Ảnh gốc (Input Real Image)")
    plt.axis('off')

    # 2. Kết quả Global
    plt.subplot(1, 3, 2)
    plt.imshow(global_thresh, cmap='gray')
    plt.title(f"2. Global Otsu (Threshold = {int(ret_otsu)})\n(Thất bại ở vùng bóng đổ)")
    plt.axis('off')

    # 3. Kết quả Adaptive
    plt.subplot(1, 3, 3)
    plt.imshow(adaptive_thresh, cmap='gray')
    plt.title("3. Adaptive Threshold\n(Giữ lại nét chữ, lọc sạch bóng)")
    plt.axis('off')

    plt.tight_layout()
    plt.show()

    # Lưu ảnh kết quả ra file để chèn báo cáo
    # Để ghép ảnh lại lưu cho dễ, ta cần chuyển các ảnh về cùng định dạng
    # Chuyển 2 ảnh kết quả nhị phân (1 kênh) thành 3 kênh để ghép với ảnh gốc
    global_bgr = cv2.cvtColor(global_thresh, cv2.COLOR_GRAY2BGR)
    adaptive_bgr = cv2.cvtColor(adaptive_thresh, cv2.COLOR_GRAY2BGR)
    
    # Ghép ngang 3 ảnh: Gốc - Global - Adaptive
    combined_result = np.hstack((img_bgr, global_bgr, adaptive_bgr))
    cv2.imwrite("shadow_comparison_result.jpg", combined_result)
    print("Đã lưu ảnh so sánh vào file 'shadow_comparison_result.jpg'")

# ==========================================
# CẤU HÌNH ĐƯỜNG DẪN ẢNH TẠI ĐÂY
# ==========================================
if __name__ == "__main__":
    # Thay 'input_shadow.jpg' bằng tên file ảnh của bạn
    # Ví dụ: 'C:/Users/Admin/Desktop/test_image.jpg'
    IMAGE_PATH = 'input_shadow.jpg' 
    
    process_real_image(IMAGE_PATH)