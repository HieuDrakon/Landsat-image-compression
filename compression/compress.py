import os
import time
import io
from PIL import Image
import rasterio
from rasterio.io import MemoryFile
from tkinter import messagebox
import psycopg2
import matplotlib.pyplot as plt
from connect import con

def compress_and_store_image(image_path):  
    conn, cursor = con()
    # Tạo bảng compressed_images nếu chưa tồn tại
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compressed_images (
        id SERIAL PRIMARY KEY,
        name TEXT,
        data BYTEA
    )
    """)
    # Lấy tên tệp
    image_name = os.path.basename(image_path)
    # Lấy dung lượng ảnh trước khi nén
    original_size = os.path.getsize(image_path)
    
    # Khởi tạo các biến lưu trữ thông tin
    img_byte_arr_jpeg = None
    img_byte_arr_lzw = None
    img_byte_arr_png = None
    compressed_size = []
    compression_time = []
    data = []
    name = []

    # Nén JPEG 2000 và PNG bằng Pillow
    try:
        with Image.open(image_path) as img:
            # JPEG 2000
            start_time_1 = time.time()
            img_byte_arr_jpeg = io.BytesIO()
            new_image_name_jp2 = image_name.rsplit('.', 1)[0] + '.jp2'
            img.save(img_byte_arr_jpeg, format='JPEG2000')
            img_byte_arr_jpeg = img_byte_arr_jpeg.getvalue()
            end_time_1 = time.time()

            # PNG
            start_time_2 = time.time()
            img_byte_arr_png = io.BytesIO()
            new_image_name_png = image_name.rsplit('.', 1)[0] + '.png'
            img.save(img_byte_arr_png, format='PNG')
            img_byte_arr_png = img_byte_arr_png.getvalue()
            end_time_2 = time.time()

    except Exception as e:
        messagebox.showinfo("ERROR", f"Lỗi khi xử lý ảnh {image_name} với Pillow: {e}")
        cursor.close()
        conn.close()
        return

    # Nén TIFF với LZW bằng Rasterio
    try:
        with rasterio.open(image_path, 'r') as src:
            profile = src.profile
            profile.update(compression='LZW')  # Thiết lập nén LZW

            start_time_3 = time.time()
            with MemoryFile() as memfile:
                with memfile.open(**profile) as dst:
                    dst.write(src.read())  # Ghi dữ liệu từ ảnh gốc
                img_byte_arr_lzw = memfile.read()  # Đọc dữ liệu nén từ MemoryFile
            end_time_3 = time.time()

    except Exception as e:
        messagebox.showinfo("ERROR", f"Lỗi khi xử lý ảnh {image_name} với Rasterio: {e}")
        cursor.close()
        conn.close()
        return

    # Kiểm tra xem các biến có giá trị không trước khi tiếp tục
    if img_byte_arr_jpeg is None or img_byte_arr_lzw is None or img_byte_arr_png is None:
        messagebox.showinfo("ERROR", "Không thể nén ảnh. Vui lòng kiểm tra định dạng ảnh.")
        cursor.close()
        conn.close()
        return

    # Lấy dung lượng sau khi nén      
    compressed_size = [len(img_byte_arr_jpeg), len(img_byte_arr_lzw), len(img_byte_arr_png)]
    
    # Tính thời gian nén
    compression_time = [end_time_1 - start_time_1, end_time_3 - start_time_3, end_time_2 - start_time_2]
    
    # Lưu ảnh nén vào database
    data = [img_byte_arr_jpeg, img_byte_arr_lzw, img_byte_arr_png]
    name = [new_image_name_jp2, image_name.rsplit('.', 1)[0] + '.tiff', new_image_name_png]

    for x, y in zip(name, data):
        cursor.execute("""
        INSERT INTO compressed_images (name, data)
        VALUES (%s, %s)        
        """, (x, psycopg2.Binary(y)))    
    conn.commit()

    # In thông tin        
    print(f"Image name before compression: {image_name}\n",
            f"Original Size: {original_size / (1024 ** 2):.2f} MB\n"                           
            f"JPEG 2000\n"
            f"Image name after compression: {new_image_name_jp2}\n"
            f"Compressed Size: {compressed_size[0] / (1024 ** 2):.2f} MB\n"
            f"Compression Time : {compression_time[0]:.2f} seconds\n"  
            f"LZW (TIFF)\n" 
            f"Image name after compression: {name[1]}\n"                     
            f"Compressed Size: {compressed_size[1] / (1024 ** 2):.2f} MB\n"
            f"Compression Time: {compression_time[1]:.2f} seconds\n"
            f"PNG\n"
            f"Image name after compression: {new_image_name_png}\n"
            f"Compressed Size: {compressed_size[2] / (1024 ** 2):.2f} MB\n"
            f"Compression Time: {compression_time[2]:.2f} seconds")

    # Vẽ biểu đồ so sánh dung lượng nén với dung lượng ban đầu
    compression_methods = ['JPEG 2000', 'LZW (TIFF)', 'PNG']
    compressed_size_mb = [size / (1024 ** 2) for size in compressed_size]  # Dung lượng nén (MB)
    original_size_mb = original_size / (1024 ** 2)  # Dung lượng ban đầu (MB)

    plt.figure(figsize=(16, 8))

    # Biểu đồ dung lượng nén so với dung lượng ban đầu
    plt.subplot(1, 2, 1)
    plt.bar(compression_methods, compressed_size_mb, color=['blue', 'green', 'orange'])
    plt.axhline(y=original_size_mb, color='red', linestyle='-', label='Original Size (MB)')
    plt.title('Comparison of Compressed Sizes and Original Size')
    plt.ylabel('Size (MB)')   
    plt.legend()

    # Biểu đồ thời gian nén
    plt.subplot(1, 2, 2)
    plt.bar(compression_methods, compression_time, color=['blue', 'green', 'orange'])
    plt.title('Compression Time Comparison')
    plt.ylabel('Time (seconds)')

    # Hiển thị biểu đồ
    plt.tight_layout()
    plt.show()
