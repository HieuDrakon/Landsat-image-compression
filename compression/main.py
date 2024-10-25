import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from compress import compress_and_store_image
from connect import con
from uncompress import un

def main_menu(id):
    conn, cursor = con()
    if id == 1:
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.tiff;*.tif")])
        if image_path:  # Kiểm tra xem người dùng đã chọn file chưa
            compress_and_store_image(image_path)
        else:
            root.mainloop()      

    if id == 2:
        menu.pack_forget()
        frame.pack_forget()
        frame.pack(padx=10,pady=10)
        # Chọn dữ liệu trong database 
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

            # Nút trở về
            return_button = tk.Button(frame, text="return", command=lambda: show_main_menu())
            return_button.pack(pady=10)

    if id == 3:
        cursor.close()
        conn.close()
        root.destroy()

def show_main_menu():
    frame.pack_forget()
    menu.pack_forget() # Hiện lại menu chính
    menu.pack(padx=100,pady=10)
# Tạo giao diện chính
root = tk.Tk()
root.title("Image Compression Tool")

# Tạo menu chọn
menu = tk.Frame(root)
menu.pack(padx=100,pady=10)

 # Tạo một frame để chứa các checkbox
frame = tk.Frame(root)
frame.pack_forget()
frame.pack(padx=10,pady=10)

# Tạo nút để tải hình ảnh
Select_button = tk.Button(menu, text="Select Image", command=lambda: main_menu(1))
Select_button.pack(side=tk.TOP, fill=tk.X, padx=10,pady=10)

# Nút để hiển thị tên ảnh đã nén
decompressed_button = tk.Button(menu, text="Decompressed Image", command=lambda: main_menu(2))
decompressed_button.pack(side=tk.TOP, fill=tk.X,padx=10,pady=10)

# Nút thoát chương trình
close_button = tk.Button(menu, text="Exit", command=lambda: main_menu(3))
close_button.pack(side=tk.TOP, fill=tk.X,padx=10,pady=10)

root.pack_propagate(True)
root.mainloop()
