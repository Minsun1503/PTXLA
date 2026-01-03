import os
import json
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# Thêm đường dẫn để import config
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config import Config

def generate_exam_sheet(output_pdf_path, output_json_path):
    # --- CẤU HÌNH ---
    cfg = Config()
    
    # 1. Kích thước PDF thực tế (A4)
    A4_WIDTH, A4_HEIGHT = A4
    margin = 30 # Lề giấy (Khoảng cách từ mép giấy đến khung đen)

    # Kích thước của KHUNG VIỀN ĐEN (Đây mới là vùng ảnh sau khi Warp)
    FRAME_W_PDF = A4_WIDTH - 2 * margin
    FRAME_H_PDF = A4_HEIGHT - 2 * margin
    
    # 2. Kích thước mục tiêu (Pixel) của ảnh sau khi Warp
    TARGET_WIDTH, TARGET_HEIGHT = cfg.ImageProcessing.STANDARD_SIZE
    
    # 3. Tỷ lệ quy đổi (Dựa trên KHUNG chứ không phải khổ giấy A4)
    # Vì ảnh sau khi warp chính là cái khung đen
    SCALE_X = TARGET_WIDTH / FRAME_W_PDF
    SCALE_Y = TARGET_HEIGHT / FRAME_H_PDF

    print(f"--- Đang tạo phiếu thi (FIXED COORDINATES) ---")
    print(f"PDF Frame Size: {FRAME_W_PDF:.2f} x {FRAME_H_PDF:.2f}")
    print(f"Scale X: {SCALE_X:.4f}, Scale Y: {SCALE_Y:.4f}")

    # --- HÀM CHUYỂN ĐỔI TOẠ ĐỘ MỚI (QUAN TRỌNG) ---
    def to_opencv_point(rx, ry):
        """
        rx, ry: Toạ độ trong ReportLab (Gốc dưới-trái tờ giấy A4)
        """
        # 1. Chuyển về hệ toạ độ tương đối so với KHUNG ĐEN (Gốc là góc trên-trái khung đen)
        # X tương đối = X pdf - Lề trái
        rel_x = rx - margin
        
        # Y tương đối (tính từ đỉnh khung đen xuống) = (Đỉnh khung - Y pdf)
        # Đỉnh khung trong ReportLab là (A4_HEIGHT - margin)
        frame_top_pdf = A4_HEIGHT - margin
        rel_y = frame_top_pdf - ry
        
        # 2. Scale sang Pixel
        ox = int(rel_x * SCALE_X)
        oy = int(rel_y * SCALE_Y)
        return [ox, oy]

    def to_opencv_rect(rx, ry, rw, rh):
        """
        rx, ry: Góc dưới-trái của hình chữ nhật trong ReportLab
        """
        # ReportLab vẽ từ dưới lên, đỉnh trên của HCN là ry + rh
        pdf_top = ry + rh
        
        # Tính điểm Top-Left trong hệ OpenCV (Relative to Frame)
        top_left_pt = to_opencv_point(rx, pdf_top)
        
        ox = top_left_pt[0]
        oy = top_left_pt[1]
        
        # Width/Height cũng phải scale theo tỷ lệ mới
        ow = int(rw * SCALE_X)
        oh = int(rh * SCALE_Y)
        return [ox, oy, ow, oh]

    c = canvas.Canvas(output_pdf_path, pagesize=A4)
    c.setTitle("Phieu Trac Nghiem Chuan")

    # ======================================================
    # 1. VẼ KHUNG VIỀN ĐỊNH VỊ (HOLY FRAME)
    # ======================================================
    
    c.setLineWidth(5) # Khung đậm
    c.rect(margin, margin, FRAME_W_PDF, FRAME_H_PDF)
    
    # Điểm neo phụ
    c.setFillColor(colors.black)
    c.rect(margin + 5, A4_HEIGHT - margin - 15, 10, 10, fill=1) # Top-Left
    c.rect(A4_WIDTH - margin - 15, margin + 5, 10, 10, fill=1)  # Bottom-Right

    # Data container
    coordinates_data = {
        "info_fields": {},
        "mssv_bubbles": [],
        "answer_bubbles": [],
        "anchors": [] 
    }

    # ======================================================
    # 2. HEADER & THÔNG TIN (CĂN GIỮA)
    # ======================================================
    c.setLineWidth(1)
    
    # Tiêu đề
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(A4_WIDTH / 2, A4_HEIGHT - margin - 40, "TEST EXAM")
    
    current_y = A4_HEIGHT - margin - 70
    
    # Vẽ các dòng thông tin
    c.setFont("Helvetica", 11)
    col1_x = margin + 40
    col2_x = A4_WIDTH / 2 + 20
    line_h = 25
    
    def draw_text_field(label, x, y, w_line, key):
        c.drawString(x, y, label)
        line_start = x + c.stringWidth(label) + 5
        c.line(line_start, y-2, line_start + w_line, y-2)
        # Lưu toạ độ (Dùng hàm mới đã fix)
        coordinates_data["info_fields"][key] = to_opencv_rect(line_start, y-5, w_line, 20)

    draw_text_field("School:", col1_x, current_y, 180, "school")
    draw_text_field("Class:", col2_x, current_y, 100, "class")

    draw_text_field("Name:", col1_x, current_y - line_h, 180, "name")
    draw_text_field("Subject:", col2_x, current_y - line_h, 100, "subject")
    
    # ======================================================
    # 3. VÙNG TÔ SBD / MSSV
    # ======================================================
    mssv_digits = 6 
    mssv_rows = 10 
    bubble_r = 7 
    col_gap = 22 
    row_gap = 16 
    
    mssv_block_width = (mssv_digits * col_gap) 
    mssv_start_x = (A4_WIDTH - mssv_block_width) / 2
    
    mssv_start_y = current_y - line_h * 2 - 50 
    
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(A4_WIDTH/2, mssv_start_y + 40, "Student ID")
    
    rect_top = mssv_start_y + 30
    rect_bottom = mssv_start_y - (9*row_gap) - 15
    rect_height = rect_top - rect_bottom
    
    c.setLineWidth(1)
    c.rect(mssv_start_x - 15, rect_bottom, mssv_block_width + 10, rect_height)

    c.setFont("Helvetica", 9)
    mssv_coords = [] 
    
    for d in range(mssv_digits):
        col_list = []
        cx = mssv_start_x + (d * col_gap)
        
        c.rect(cx - 8, mssv_start_y + 10, 16, 16)
        
        for r in range(mssv_rows):
            cy = mssv_start_y - (r * row_gap)
            c.circle(cx, cy, bubble_r, stroke=1, fill=0)
            c.drawCentredString(cx, cy - 3, str(r))
            col_list.append(to_opencv_point(cx, cy))
            
        mssv_coords.append(col_list)
        
    coordinates_data["mssv_bubbles"] = mssv_coords

    # ======================================================
    # 4. VÙNG TRẢ LỜI
    # ======================================================
    total_questions = cfg.OMR.NUM_QUESTIONS_PER_COLUMN 
    num_cols = 2 
    q_per_col = (total_questions + num_cols - 1) // num_cols
    
    ans_label_w = 25
    ans_bubble_gap = 25
    ans_col_gap = 80 
    
    single_col_w = ans_label_w + (3 * ans_bubble_gap) + (2 * bubble_r)
    total_ans_w = (num_cols * single_col_w) + ((num_cols - 1) * ans_col_gap)
    
    ans_start_x = (A4_WIDTH - total_ans_w) / 2 
    ans_start_y = mssv_start_y - (10 * row_gap) - 60 
    ans_row_gap = 18
    
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(A4_WIDTH/2, ans_start_y + 25, "ANSWERS")
    
    c.setFont("Helvetica", 10)
    choices = ['A', 'B', 'C', 'D']
    
    ans_coords_flat = [] 
    anchor_tl = None
    anchor_br = None
    
    q_count = 0
    for col in range(num_cols):
        col_x = ans_start_x + (col * (single_col_w + ans_col_gap))
        
        for row in range(q_per_col):
            if q_count >= total_questions: break
            
            cy = ans_start_y - (row * ans_row_gap)
            
            c.drawString(col_x, cy - 3, f"{q_count + 1}.")
            
            q_bubbles = []
            for i, choice in enumerate(choices):
                cx = col_x + ans_label_w + (i * ans_bubble_gap)
                c.circle(cx, cy, bubble_r, stroke=1, fill=0)
                c.drawCentredString(cx, cy - 3, choice)
                
                pt = to_opencv_point(cx, cy)
                q_bubbles.append(pt)
                
                if q_count == 0 and i == 0:
                    anchor_tl = pt
                anchor_br = pt 
                
            ans_coords_flat.append(q_bubbles)
            q_count += 1
            
    coordinates_data["answer_bubbles"] = ans_coords_flat
    coordinates_data["anchors"] = [anchor_tl, anchor_br]

    # ======================================================
    # 5. LƯU FILE
    # ======================================================
    c.save()
    print(f"--> Đã tạo file PDF: {output_pdf_path}")
    
    with open(output_json_path, 'w') as f:
        json.dump(coordinates_data, f, indent=4)
    print(f"--> Đã tạo JSON chuẩn: {output_json_path}")

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/template", exist_ok=True)
    
    generate_exam_sheet("data/raw/De_thi_chuan_Final.pdf", "data/template/coordinates.json")