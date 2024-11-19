import tkinter as tk
from tkinter import messagebox, filedialog
from compress import compress_and_store_image
from connect import con
from uncompress import un

# Kết nối tới cơ sở dữ liệu
conn, cursor = con()

def main_menu(id):
    if id == 1:
        # Cho phép chọn nhiều file
        image_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.tiff;*.tif")])
        if image_paths:  # Kiểm tra xem người dùng đã chọn file chưa
            for image_path in image_paths:
                compress_and_store_image(image_path)
        else:
            messagebox.showinfo("Thông báo", "Không có tệp nào được chọn.")
            root.mainloop()
    elif id == 2:
        # Chọn dữ liệu trong database 
        cursor.execute("SELECT id, name FROM compressed_images")
        results = cursor.fetchall()  # Lấy tất cả các dòng kết quả

        if not results:
            messagebox.showinfo("Thông báo", "Data name is empty")
            root.mainloop()
        else:
            menu.pack_forget()
            frame.pack_forget()
            frame.pack(padx=10, pady=10)

            # Xóa các checkbox cũ
            for widget in frame.winfo_children():
                widget.destroy()

            # Tạo một danh sách để lưu trạng thái checkbox
            checkboxes = []

            # Sử dụng Listbox để chứa checkbox
            listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE)
            for row in results:
                # Tạo một checkbox cho mỗi tên file
                var = tk.IntVar()
                checkbox = tk.Checkbutton(listbox, text=row[1], variable=var)
                checkbox.pack(anchor='w')
                listbox.insert(tk.END, checkbox)  # Thêm checkbox vào Listbox
                checkboxes.append((var, row[0], row[1]))  # Lưu trạng thái và tên file
            listbox.pack()

            # Thêm một nút để xử lý dữ liệu đã chọn
            process_button = tk.Button(frame, text="Selected", command=lambda: un(checkboxes))
            process_button.pack(pady=10)

            # Nút trở về
            return_button = tk.Button(frame, text="return", command=show_main_menu)
            return_button.pack(pady=10)

    elif id == 3:
        cursor.close()
        conn.close()
        root.destroy()

def show_main_menu():
    frame.pack_forget()
    menu.pack_forget()  # Ẩn frame và hiện lại menu chính
    menu.pack(padx=100, pady=10)

# Tạo giao diện chính
root = tk.Tk()
root.title("Image Compression Tool")

# Tạo menu chọn
menu = tk.Frame(root)
menu.pack(padx=100, pady=10)

# Tạo một frame để chứa các checkbox
frame = tk.Frame(root)
frame.pack_forget()
frame.pack(padx=10, pady=10)

# Tạo nút để tải hình ảnh
select_button = tk.Button(menu, text="Select Image", command=lambda: main_menu(1))
select_button.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

# Nút để hiển thị tên ảnh đã nén
decompressed_button = tk.Button(menu, text="Decompressed Image", command=lambda: main_menu(2))
decompressed_button.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

# Nút thoát chương trình
close_button = tk.Button(menu, text="Exit", command=lambda: main_menu(3))
close_button.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

root.pack_propagate(True)
root.mainloop()
