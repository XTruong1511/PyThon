# views/login_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
from views.main_view import MainView

class LoginView(ttk.Frame):
    """
    Giao diện đăng nhập
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.auth_controller = AuthController()
        
        # Thiết lập giao diện
        self.setup_ui()
    
    def setup_ui(self):
        """
        Thiết lập các thành phần giao diện
        """
        # Frame chính
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        title_label = ttk.Label(main_frame, text="ĐĂNG NHẬP HỆ THỐNG RẠP CHIẾU PHIM", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Frame chứa form đăng nhập
        login_frame = ttk.Frame(main_frame, padding="10")
        login_frame.pack(pady=10)
        
        # Username
        ttk.Label(login_frame, text="Tên đăng nhập:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.username_var, width=30).grid(row=0, column=1, pady=5)
        
        # Password
        ttk.Label(login_frame, text="Mật khẩu:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(login_frame, textvariable=self.password_var, width=30, show="*")
        password_entry.grid(row=1, column=1, pady=5)
        
        # Nút đăng nhập
        login_button = ttk.Button(login_frame, text="Đăng nhập", command=self.login)
        login_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Bind Enter key
        password_entry.bind("<Return>", lambda event: self.login())
        
        # Thông tin hướng dẫn
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(pady=20)
        
        ttk.Label(info_frame, text="Tài khoản mặc định:", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(info_frame, text="- Admin: admin / admin123").pack(anchor="w")
        ttk.Label(info_frame, text="- Nhân viên: staff / staff123").pack(anchor="w")
        ttk.Label(info_frame, text="- Khách hàng: customer / customer123").pack(anchor="w")
    
    def login(self):
        """
        Xử lý đăng nhập
        """
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!")
            return
        
        # Kiểm tra đăng nhập
        user = self.auth_controller.login(username, password)
        
        if user:
            messagebox.showinfo("Thành công", f"Đăng nhập thành công! Xin chào {user['name']}!")
            
            # Ẩn giao diện đăng nhập
            self.pack_forget()
            
            # Hiển thị giao diện chính
            main_view = MainView(self.parent, user)
            main_view.pack(fill=tk.BOTH, expand=True)
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng!")
            
    