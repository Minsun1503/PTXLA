import matplotlib.pyplot as plt
import os

# --- CẤU HÌNH ĐƯỜNG DẪN ---
# Lấy đường dẫn gốc của dự án (nhảy ra khỏi thư mục 'tools')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Đường dẫn đến thư mục chứa ảnh cho báo cáo: report/images
REPORT_IMG_DIR = os.path.join(BASE_DIR, 'report', 'images')

# Tạo thư mục nếu chưa có
os.makedirs(REPORT_IMG_DIR, exist_ok=True)

def draw_accuracy_chart():
    print(f"--> Đang vẽ biểu đồ độ chính xác...")
    
    # Dữ liệu thực tế từ Log của bạn
    cases = ['Case 0\n(Chuẩn)', 'Case 1\n(Ảnh chụp)', 'Case 2\n(Bóng đổ)', 
             'Case 3\n(Nghiêng)', 'Case 4\n(Tẩy xóa)', 'Case 5\n(Dấu tích)']
    scores = [19, 11, 9, 5, 5, 2]
    percentages = [s/20*100 for s in scores]

    # Màu sắc: Xanh lá (Tốt) -> Xanh dương (Khá) -> Đỏ (Tệ)
    colors = ['#2ecc71'] * 1 + ['#3498db'] * 2 + ['#e74c3c'] * 3

    plt.figure(figsize=(10, 6))
    bars = plt.bar(cases, percentages, color=colors, edgecolor='black', alpha=0.8)

    # Thêm nhãn số liệu lên đầu cột
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.0f}%', 
                 ha='center', va='bottom', fontweight='bold', fontsize=11)

    plt.title('Độ chính xác trên các tập dữ liệu kiểm thử (N=20)', fontsize=14, pad=20)
    plt.ylabel('Độ chính xác (%)', fontsize=12)
    plt.ylim(0, 110) # Để dư một chút phía trên cho đẹp
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Lưu file vào đúng thư mục report/images
    output_path = os.path.join(REPORT_IMG_DIR, 'accuracy_chart.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Đã lưu biểu đồ tại: {output_path}")
    
    # Nếu chạy trên máy cá nhân thì hiện lên xem, trên server thì thôi
    try:
        plt.show()
    except:
        pass

if __name__ == "__main__":
    # Kiểm tra xem đã cài matplotlib chưa
    try:
        import matplotlib
        draw_accuracy_chart()
    except ImportError:
        print("❌ Lỗi: Chưa cài thư viện matplotlib.")
        print("👉 Hãy chạy lệnh: pip install matplotlib")