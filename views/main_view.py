# views/main_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
from views.movie_view import MovieManagementView
from views.theater_view import TheaterManagementView
from views.schedule_view import ScheduleManagementView
from views.booking_view import BookingView

class MainView(ttk.Frame):
    """
    Giao diện chính của ứng dụng
    """
    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.auth_controller = AuthController()
        self.auth_controller.current_user = user
        
        # Thiết lập giao diện
        self.setup_ui()
        
        # Mặc định hiển thị màn hình chào mừng
        self.show_welcome_screen()
    
    def setup_ui(self):
        """
        Thiết lập các thành phần giao diện
        """
        # Frame chính chia làm 2 phần: sidebar và content
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar - Menu trái
        self.sidebar_frame = ttk.Frame(self.main_paned, width=200)
        self.main_paned.add(self.sidebar_frame, weight=1)
        
        # Content - Nội dung chính
        self.content_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.content_frame, weight=4)
        
        # Thiết lập sidebar
        self.setup_sidebar()
        
        # Frame đệm để giữ lại nội dung content_frame không bị xóa
        self.content_holder = ttk.Frame(self.content_frame)
        self.content_holder.pack(fill=tk.BOTH, expand=True)
    
    def setup_sidebar(self):
        """
        Thiết lập menu sidebar
        """
        # Thông tin người dùng
        user_frame = ttk.LabelFrame(self.sidebar_frame, text="Thông tin người dùng")
        user_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(user_frame, text=f"Tên: {self.user['name']}").pack(anchor="w", padx=5, pady=2)
        ttk.Label(user_frame, text=f"Vai trò: {self.get_role_display(self.user['role'])}").pack(anchor="w", padx=5, pady=2)
        
        # Nút đăng xuất
        ttk.Button(user_frame, text="Đăng xuất", command=self.logout).pack(pady=5)
        
        # Menu chức năng
        menu_frame = ttk.LabelFrame(self.sidebar_frame, text="Menu chức năng")
        menu_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Nút màn hình chính
        ttk.Button(menu_frame, text="Màn hình chính", 
                command=self.show_welcome_screen).pack(fill=tk.X, padx=5, pady=5)
        
        # Menu quản lý phim - CHỈ HIỂN THỊ CHO ADMIN VÀ STAFF
        if self.auth_controller.check_permission("staff"):
            ttk.Button(menu_frame, text="Quản lý phim", 
                    command=self.show_movie_management).pack(fill=tk.X, padx=5, pady=5)
        
        # Menu quản lý phòng chiếu - Chỉ admin và staff mới xem được
        if self.auth_controller.check_permission("staff"):
            ttk.Button(menu_frame, text="Quản lý phòng chiếu", 
                    command=self.show_theater_management).pack(fill=tk.X, padx=5, pady=5)
        
        # Menu quản lý lịch chiếu - Chỉ admin và staff mới xem được
        if self.auth_controller.check_permission("staff"):
            ttk.Button(menu_frame, text="Quản lý lịch chiếu", 
                    command=self.show_schedule_management).pack(fill=tk.X, padx=5, pady=5)
        
        # Menu đặt vé - Tất cả đều xem được
        ttk.Button(menu_frame, text="Đặt vé xem phim", 
                command=self.show_booking).pack(fill=tk.X, padx=5, pady=5)
        
        # Menu quản lý người dùng - Chỉ admin mới xem được
        if self.auth_controller.check_permission("admin"):
            ttk.Button(menu_frame, text="Quản lý người dùng", 
                    command=self.show_user_management).pack(fill=tk.X, padx=5, pady=5)

    def get_role_display(self, role):
        """
        Hiển thị tên vai trò dễ đọc
        """
        roles = {
            "admin": "Quản trị viên",
            "staff": "Nhân viên",
            "customer": "Khách hàng"
        }
        return roles.get(role, role)
    
    def clear_content(self):
        """
        Xóa nội dung hiện tại trong content_frame
        """
        for widget in self.content_holder.winfo_children():
            widget.destroy()
    
    def show_welcome_screen(self):
        """
        Hiển thị màn hình chào mừng
        """
        self.clear_content()
        
        welcome_frame = ttk.Frame(self.content_holder)
        welcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Tiêu đề
        title_label = ttk.Label(welcome_frame, 
                               text="HỆ THỐNG QUẢN LÝ RẠP CHIẾU PHIM", 
                               font=("Arial", 20, "bold"))
        title_label.pack(pady=30)
        
        # Thông tin chào mừng
        welcome_text = f"Chào mừng {self.user['name']} đến với hệ thống quản lý rạp chiếu phim.\n\n"
        welcome_text += "Hãy sử dụng menu bên trái để truy cập các chức năng của hệ thống."
        
        welcome_label = ttk.Label(welcome_frame, 
                                 text=welcome_text,
                                 font=("Arial", 12),
                                 justify=tk.CENTER)
        welcome_label.pack(pady=20)
        
        # Hướng dẫn sử dụng
        guide_frame = ttk.LabelFrame(welcome_frame, text="Hướng dẫn sử dụng")
        guide_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        guide_text = """
        1. Quản lý phim: Xem danh sách phim, thêm, sửa, xóa phim
        2. Quản lý phòng chiếu: Quản lý các phòng chiếu phim
        3. Quản lý lịch chiếu: Lập lịch chiếu cho các phim
        4. Đặt vé xem phim: Đặt vé xem phim theo lịch chiếu
        5. Quản lý người dùng: Quản lý tài khoản người dùng
        """
        
        ttk.Label(guide_frame, text=guide_text, justify=tk.LEFT).pack(padx=10, pady=10)
    
    def show_movie_management(self):
        """
        Hiển thị giao diện quản lý phim
        """
        self.clear_content()
        movie_view = MovieManagementView(self.content_holder, self.user)
        movie_view.pack(fill=tk.BOTH, expand=True)
    
    def show_theater_management(self):
        """
        Hiển thị giao diện quản lý phòng chiếu
        """
        self.clear_content()
        theater_view = TheaterManagementView(self.content_holder, self.user)
        theater_view.pack(fill=tk.BOTH, expand=True)
    
    def show_schedule_management(self):
        """
        Hiển thị giao diện quản lý lịch chiếu
        """
        print("Attempting to show schedule management view")  # Debug
        self.clear_content()
        try:
            print("Initializing ScheduleManagementView")  # Debug
            schedule_view = ScheduleManagementView(self.content_holder, self.user)
            print("ScheduleManagementView initialized, packing...")  # Debug
            schedule_view.pack(fill=tk.BOTH, expand=True)
            print("ScheduleManagementView packed successfully")  # Debug
        except Exception as e:
            print(f"Error showing schedule view: {str(e)}")  # Debug
            messagebox.showerror("Lỗi", f"Không thể hiển thị giao diện quản lý lịch chiếu: {str(e)}")
    
    def show_booking(self):
        """
        Hiển thị giao diện đặt vé
        """
        self.clear_content()
        booking_view = BookingView(self.content_holder, self.user)
        booking_view.pack(fill=tk.BOTH, expand=True)
    
    def show_user_management(self):
        """
        Hiển thị giao diện quản lý người dùng
        """
        self.clear_content()
        
        # Import tại đây để tránh circular import
        from views.user_view import UserManagementView
        user_view = UserManagementView(self.content_holder, self.user)
        user_view.pack(fill=tk.BOTH, expand=True)
    
    def logout(self):
        """
        Đăng xuất
        """
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc chắn muốn đăng xuất?"):
            self.auth_controller.logout()
            
            # Xóa giao diện hiện tại
            self.destroy()
            
            # Hiển thị lại giao diện đăng nhập
            from views.login_view import LoginView
            login_view = LoginView(self.parent)
            login_view.pack(fill=tk.BOTH, expand=True)
            
        
