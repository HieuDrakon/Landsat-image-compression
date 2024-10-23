import io
import os
from tkinter import messagebox
from matplotlib import pyplot as plt
from connect import con
from PIL import Image

def un(checkboxes):
    conn, cursor = con()
    output_folder = "uncompress"
    
    # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Lấy danh sách id file đã chọn
    selected_files = [id for var, id, name in checkboxes if var.get() == 1]
    if not selected_files:
        messagebox.showinfo("Error", "No file selected!")
        return
    
    sel = int(selected_files[0])
    cursor.execute("SELECT name, data FROM compressed_images WHERE id = %s", (sel,))
    result = cursor.fetchone()
    
    if result is None:
        print(f"Image with ID {sel} not found.")
        return

    # Lấy tên ảnh và dữ liệu đã nén
    image_name, image_data = result
    
    # Đường dẫn và tên file mới sau khi giải nén
    new_image_name = image_name.rsplit('.', 1)[0] + '.TIF'
    decompressed_image_name = f"decompressed_{new_image_name}"

    # Tạo đối tượng BytesIO từ dữ liệu đã nén
    img_byte_arr = io.BytesIO(image_data)

    # Mở ảnh từ đối tượng BytesIO
    with Image.open(img_byte_arr) as img:
        # Đường dẫn nơi lưu ảnh đã giải nén
        output_path = os.path.join(output_folder, new_image_name)
        
        # Lưu ảnh đã giải nén ra file (có nén bằng LZW)
        img.save(output_path, format='TIFF', compression='tiff_lzw')
        
        # Lấy dung lượng ban đầu (trong cơ sở dữ liệu)
        original_size = len(image_data)
        
        # Lấy dung lượng sau khi giải nén
        decompressed_size = os.path.getsize(output_path)

        # Thông báo hoàn thành
        messagebox.showinfo("Decompressed Image Complete", 
                            f"Image {decompressed_image_name} has been decompressed and saved at {output_path}")

        # In thông tin
        print(f"Original Image Name: {image_name}\n")
        print(f"Original Size: {original_size / (1024 ** 2):.2f} MB\n")
        print(f"Decompressed Image Name: {decompressed_image_name}\n")
        print(f"Decompressed Size: {decompressed_size / (1024 ** 2):.2f} MB\n")

        # # Hiển thị ảnh đã giải nén
        # plt.imshow(img)
        # plt.axis('off')  # Tắt trục tọa độ
        # plt.show()

    cursor.close()
    conn.close()
