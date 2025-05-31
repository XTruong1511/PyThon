# main.py
import os
import tkinter as tk
from tkinter import messagebox
from views.login_view import LoginView
from utils.config import setup_config

def main():
    # Đảm bảo các thư mục cần thiết đã được tạo
    os.makedirs('data', exist_ok=True)
    
    # Khởi tạo cấu hình
    setup_config()
    
    # Tạo cửa sổ ứng dụng chính
    root = tk.Tk()
    root.title("Ứng dụng Quản lý Rạp Chiếu Phim")
    root.geometry("1024x768")
    
    # Thiết lập biểu tượng nếu có
    try:
        root.iconbitmap("assets/cinema_icon.ico")
    except:
        pass
    
    # Tạo và hiển thị giao diện đăng nhập
    login_view = LoginView(root)
    login_view.pack(fill=tk.BOTH, expand=True)
    
    # Bắt đầu vòng lặp chính của ứng dụng
    root.geometry("1280x800")  # Tăng kích thước cửa sổ
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        messagebox.showerror("Lỗi", f"Ứng dụng gặp lỗi không mong muốn: {str(e)}")