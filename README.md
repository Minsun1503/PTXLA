# 🚀 SmartGrader \- Hệ Thống Chấm Thi & Số Hóa Thông Tin Tự Động

PythonOpenCVEasyOCRReportLab

## 📖 Giới thiệu

**SmartGrader** là giải pháp phần mềm mã nguồn mở giải quyết bài toán tự động hóa quy trình chấm thi trắc nghiệm với chi phí thấp 1\. Thay vì phụ thuộc vào các máy chấm thi chuyên dụng đắt tiền, hệ thống tận dụng sức mạnh của **Computer Vision** và **Deep Learning** để xử lý phiếu trả lời từ ảnh chụp điện thoại hoặc máy scan văn phòng.  
Dự án không chỉ dừng lại ở việc chấm điểm (OMR) mà còn tích hợp khả năng nhận dạng chữ viết (OCR) để số hóa thông tin thí sinh, tạo nên một quy trình khép kín từ khâu tạo đề đến xuất báo cáo 2\.

## 🌟 Tính năng nổi bật (Key Features)

Hệ thống được xây dựng dựa trên kiến trúc module hóa (Data-Driven Architecture) với các điểm nhấn kỹ thuật:

### 🛠️ 1\. Auto Sheet Generator (Tạo đề chuẩn xác)

Sử dụng **ReportLab** trong module tools/generate\_sheet.py để sinh ra phiếu thi dưới dạng PDF bằng mã lệnh.

* **Lợi ích:** Tạo ra **Ground Truth** (tọa độ đáp án) chính xác tuyệt đối ngay từ đầu, loại bỏ sai số do thiết kế thủ công, đảm bảo sự đồng bộ hoàn hảo với engine chấm điểm 3, 4\.

### 👁️ 2\. Robust OMR Engine (Chống nhiễu & Bóng đổ)

Thuật toán chấm điểm trong src/core/omr\_engine.py được tối ưu hóa cho các điều kiện thực tế khắc nghiệt.

* **Kỹ thuật:** Sử dụng **Adaptive Thresholding (Gaussian C)** thay vì phân ngưỡng cố định.  
* **Hiệu quả:** Tự động thích nghi với điều kiện ánh sáng không đồng đều, loại bỏ hiện tượng bóng đổ (shadows) hoặc giấy bị ố màu, đảm bảo tách biệt chính xác vết mực tô và nền giấy 5, 6\.

### 📝 3\. Intelligent OCR & Validation (Lọc nhiễu dữ liệu)

Module src/core/ocr\_engine.py kết hợp sức mạnh của **EasyOCR** với quy trình hậu xử lý (Post-processing) nghiêm ngặt.

* **Kỹ thuật:** Tích hợp **Regex Validation**.  
* **Hiệu quả:** Tự động làm sạch dữ liệu sau khi nhận dạng (ví dụ: trường SBD chỉ chấp nhận số, Tên tự động viết hoa chữ cái đầu), giúp loại bỏ các ký tự rác do nhiễu ảnh gây ra 7, 8\.

## ⚙️ Cài đặt (Installation)

### 1\. Cài đặt thư viện

Clone dự án và cài đặt các dependencies cần thiết qua pip:  
git clone https://github.com/your-username/SmartGrader.git  
cd SmartGrader  
pip install \-r requirements.txt

### 2\. Cấu hình Poppler (Quan trọng ⚠️)

Dự án sử dụng thư viện pdf2image để xử lý file PDF, thư viện này yêu cầu **Poppler** phải được cài đặt trong hệ thống 9, 10\.

* **Windows:** Thư mục poppler-25.11.0 đã được đính kèm trong source code.  
* **Bước bắt buộc:** Bạn **PHẢI** thêm đường dẫn .../PTXLA/poppler-25.11.0/Library/bin vào biến môi trường **PATH** của Windows. Nếu không, chương trình sẽ báo lỗi PopplerNotInstalledError 10\.

## 🕹️ Hướng dẫn sử dụng (Usage)

Quy trình vận hành được thiết kế theo luồng 4 bước đơn giản:

### Bước 1: Tạo phiếu thi mẫu

Chạy công cụ Generator để tạo file PDF phiếu thi chuẩn (chứa các marker định vị chính xác):  
python tools/generate\_sheet.py  
*(File kết quả sẽ được lưu, dùng file này để in ra giấy)* 4\.

### Bước 2: Làm bài thi

In phiếu thi ra giấy. Tô các ô đáp án và điền thông tin (SBD, Tên) bằng bút màu đậm (đen hoặc xanh).

### Bước 3: Chuẩn bị dữ liệu đầu vào

Chụp ảnh hoặc scan các phiếu đã làm bài. Copy toàn bộ ảnh vào thư mục xử lý theo lô:👉 data/raw/batch\_input/ 11, 12\.

### Bước 4: Chạy hệ thống chấm điểm

Kích hoạt main.py để hệ thống tự động quét, xử lý và xuất điểm:  
python main.py  
*Lưu ý: Hệ thống sẽ tự động load template từ coordinates.json và xử lý hàng loạt các ảnh trong thư mục input* 13\.

## 📂 Cấu trúc dự án (Project Structure)

Cây thư mục được tổ chức theo mô hình **MVC (Model-View-Controller)** tách biệt rõ ràng giữa xử lý logic và dữ liệu 14:  
PTXLA/  
├── main.py                  \# 🚀 Orchestrator: Điều phối luồng chạy chính  
├── config.py                \# ⚙️ Configuration: Quản lý tham số tập trung  
├── requirements.txt         \# 📦 Dependencies  
├── data/                    \# 💾 Data Layer  
│   ├── answer/              \# Chứa đáp án (CSV)  
│   ├── raw/                 \# Dữ liệu thô (PDF gốc, ảnh chụp đầu vào)  
│   │   └── batch\_input/     \# Folder chứa ảnh cần chấm (Bước 3\)  
│   └── template/            \# Chứa coordinates.json (cấu hình tọa độ)  
├── src/                     \# 🧠 Source Code Layer  
│   ├── core/                \# Core Logic  
│   │   ├── omr\_engine.py    \# Engine chấm trắc nghiệm (Adaptive Threshold)  
│   │   ├── ocr\_engine.py    \# Engine đọc chữ (EasyOCR \+ Regex)  
│   │   └── processor.py     \# Xử lý ảnh (Warp, Contour)  
│   ├── utils/               \# Utilities (File I/O, Image transform)  
│   └── view/                \# Presentation Layer  
│       └── renderer.py      \# Vẽ kết quả lên ảnh (Draw results)  
├── tools/                   \# 🛠️ Helper Tools  
│   ├── generate\_sheet.py    \# Tạo phiếu thi PDF (Generator)  
│   └── create\_template.py   \# Tool định nghĩa tọa độ (Interactive)  
└── output/                  \# 📤 Result Layer (Ảnh kết quả, file JSON)

## 🚧 Hạn chế & Hướng phát triển

Dựa trên báo cáo thực nghiệm, hệ thống hiện tại còn một số điểm cần cải thiện trong các phiên bản tiếp theo 15-17:

### Hạn chế (Limitations)

* **Phụ thuộc khung viền (Frame Dependency):** Thuật toán hiện tại dựa vào việc tìm 4 góc của khung hình chữ nhật. Nếu ảnh chụp bị mất góc hoặc khung bị che khuất, quá trình Warp Perspective sẽ thất bại.  
* **OCR chữ viết tay:** Thư viện EasyOCR hoạt động tốt với chữ in nhưng độ chính xác giảm với chữ viết tay tiếng Việt ngoằn ngoèo hoặc viết tắt.  
* **Cấu trúc tĩnh:** Phụ thuộc vào template tọa độ cố định, khó thích nghi nếu mẫu phiếu thay đổi bố cục đột ngột.

### Hướng phát triển (Future Roadmap)

*  **Deep Learning Integration:** Thay thế thuật toán tìm biên Canny bằng mô hình **YOLO** để phát hiện phiếu thi ngay cả khi bị che khuất hoặc biến dạng mạnh.  
*  **Handwriting Improvement:** Fine-tune lại model OCR chuyên biệt cho bộ dữ liệu chữ viết tay tiếng Việt.  
*  **Desktop GUI:** Xây dựng giao diện đồ họa (PyQt/Tkinter) để người dùng không cần thao tác qua dòng lệnh.

*Project by Nguyễn Thế Minh Nhật / Nhóm 10*  
