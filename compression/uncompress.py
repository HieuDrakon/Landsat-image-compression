import os
import io
from PIL import Image
import rasterio
from tkinter import messagebox
from connect import con

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
    extension = image_name.rsplit('.', 1)[-1].lower()  # Lấy phần mở rộng file

    # Đường dẫn và tên file mới sau khi giải nén
    new_image_name = image_name.rsplit('.', 1)[0] + '_decompressed.TIF'
    output_path = os.path.join(output_folder, new_image_name)

    try:
        if extension in ['jp2', 'jpeg2000']:
            # Giải nén JPEG 2000 bằng Pillow
            img_byte_arr = io.BytesIO(image_data)
            with Image.open(img_byte_arr) as img:
                img.save(output_path, format='TIFF')
        
        elif extension == 'tiff':
            # Giải nén TIFF (LZW) bằng Rasterio
            img_byte_arr = io.BytesIO(image_data)
            with rasterio.open(img_byte_arr) as src:
                profile = src.profile
                data = src.read()

                # Cập nhật profile cho ảnh đã giải nén
                profile.update(driver='GTiff', compress=None)  # Không nén ảnh

                # Lưu ảnh đã giải nén ra file
                with rasterio.open(output_path, 'w', **profile) as dst:
                    dst.write(data)

        elif extension == 'png':
            # Giải nén PNG bằng Pillow
            img_byte_arr = io.BytesIO(image_data)
            with Image.open(img_byte_arr) as img:
                img.save(output_path, format='TIFF')

        else:
            messagebox.showinfo("Error", f"Unsupported file format: {extension}")
            return

        # Lấy dung lượng ban đầu từ cơ sở dữ liệu
        original_size = len(image_data)

        # Lấy dung lượng sau khi giải nén
        decompressed_size = os.path.getsize(output_path)

        # Thông báo hoàn thành
        messagebox.showinfo(
            "Decompressed Image Complete",
            f"Image {new_image_name} has been decompressed and saved at {output_path}"
        )

        # In thông tin
        print(f"Original Image Name: {image_name}\n")
        print(f"Original Size: {original_size / (1024 ** 2):.2f} MB\n")
        print(f"Decompressed Image Name: {new_image_name}\n")
        print(f"Decompressed Size: {decompressed_size / (1024 ** 2):.2f} MB\n")

    except Exception as e:
        messagebox.showinfo("Error", f"Failed to decompress image {image_name}: {e}")
        print(f"Error decompressing image: {e}")
