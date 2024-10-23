import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from compress import compress_and_store_image
from connect import con
from uncompress import un

def menu_handling(id):
    conn, cursor = con()
    if id == 1:
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.tiff;*.tif")])        
        compress_and_store_image(image_path)

    if id == 2:
        
        cursor.execute("SELECT id, name FROM compressed_images")
        results = cursor.fetchall()  # Lấy tất cả các dòng kết quả
        if not results:
            messagebox.showinfo("Thông báo", "Data name is empty")
        else:
            # Xóa các checkbox cũ
            for widget in frame.winfo_children():
                widget.destroy()

            # Tạo một danh sách để lưu trạng thái checkbox
            checkboxes = []

            # Tạo checkbox cho mỗi tên file
            for row in results:
                var = tk.IntVar()  # Biến lưu trạng thái cho checkbox
                checkbox = tk.Checkbutton(frame, text=row[1], variable=var)
                checkbox.pack(anchor='w')  # Đặt checkbox vào frame
                checkboxes.append((var, row[0], row[1]))  # Lưu trạng thái và tên file

            # Thêm một nút để xử lý dữ liệu đã chọn
            process_button = tk.Button(frame, text="Selected", command=lambda: un(checkboxes))
            process_button.pack(pady=10)
    
    if id == 3:
        cursor.close()
        conn.close()
        root.quit()

# Tạo giao diện chính
root = tk.Tk()
root.title("Image Compression Tool")

# Tạo menu chọn
menu = tk.Frame(root)
menu.pack(padx=100,pady=10)

# Tạo một frame để chứa các checkbox
frame = tk.Frame(menu)
frame.pack(padx=10,pady=10)

# Tạo nút để tải hình ảnh
Select_button = tk.Button(menu, text="Select Image", command=lambda: menu_handling(1))
Select_button.pack(side=tk.TOP, fill=tk.X, padx=10,pady=10)

# Nút để hiển thị tên ảnh đã nén
decompressed_button = tk.Button(menu, text="Decompressed Image", command=lambda: menu_handling(2))
decompressed_button.pack(side=tk.TOP, fill=tk.X,padx=10,pady=10)

close_button = tk.Button(menu, text="Exit", command=lambda: menu_handling(3))
close_button.pack(side=tk.TOP, fill=tk.X,padx=10,pady=10)

root.pack_propagate(True)
root.mainloop()