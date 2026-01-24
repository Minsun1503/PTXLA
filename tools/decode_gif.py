from PIL import Image
import os

def extract_gif_frames(gif_path, output_dir="extracted_frames"):
    # Kiểm tra file đầu vào
    if not os.path.exists(gif_path):
        print(f"Lỗi: Không tìm thấy file '{gif_path}'")
        return

    # Tạo thư mục đầu ra nếu chưa có
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with Image.open(gif_path) as im:
            # Lấy tổng số khung hình
            n_frames = im.n_frames
            print(f"Tìm thấy {n_frames} khung hình trong GIF.")

            # Chúng ta sẽ chọn ra 4 mốc thời gian quan trọng để minh họa quy trình
            # Ví dụ: Đầu, Giữa 1, Giữa 2, Cuối
            selected_indices = [
                0,                          # Frame đầu tiên (Ảnh gốc)
                int(n_frames * 0.3),        # Frame khoảng 30% (Đang hiện Heatmap)
                int(n_frames * 0.6),        # Frame khoảng 60% (Đang nối Affinity)
                n_frames - 1                # Frame cuối cùng (Kết quả Polygon hoàn thiện)
            ]

            filenames = []
            for i, idx in enumerate(selected_indices):
                im.seek(idx) # Di chuyển đến frame chỉ định
                # Lưu thành file PNG
                outfile = os.path.join(output_dir, f"craft_step_{i+1}.png")
                im.save(outfile)
                filenames.append(outfile)
                print(f"Đã lưu: {outfile}")
            
            print("\n--- HOÀN TẤT ---")
            print(f"Hãy copy 4 file ảnh trong thư mục '{output_dir}' vào thư mục 'images/' của báo cáo LaTeX.")

    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

# --- CHẠY SCRIPT ---
if __name__ == "__main__":
    # Đổi tên file GIF của bạn ở đây nếu khác
    gif_filename = "craft_example.gif" 
    extract_gif_frames(gif_filename)