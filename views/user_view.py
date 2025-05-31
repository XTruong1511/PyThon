# views/user_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
import uuid

class UserManagementView(ttk.Frame):
    """
    Giao diện quản lý người dùng
    """
    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.auth_controller = AuthController()
        self.auth_controller.current_user = user
        
        # Biến lưu trữ thông tin người dùng đang chọn
        self.selected_user = None
        
        # Thiết lập giao diện
        self.setup_ui()
        
        # Load dữ liệu người dùng
        self.load_users()
    
    def setup_ui(self):
        """
        Thiết lập các thành phần giao diện
        """
        # Frame chính chia làm 2 phần: danh sách và form chi tiết
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame danh sách người dùng
        self.list_frame = ttk.LabelFrame(self.main_paned, text="Danh sách người dùng")
        self.main_paned.add(self.list_frame, weight=3)
        
        # Frame chi tiết người dùng
        self.detail_frame = ttk.LabelFrame(self.main_paned, text="Thông tin chi tiết")
        self.main_paned.add(self.detail_frame, weight=2)
        
        # Thiết lập frame danh sách
        self.setup_list_frame()
        
        # Thiết lập frame chi tiết
        self.setup_detail_frame()
    
    def setup_list_frame(self):
        """
        Thiết lập frame danh sách người dùng
        """
        # Frame chứa công cụ
        tools_frame = ttk.Frame(self.list_frame)
        tools_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Ô tìm kiếm
        ttk.Label(tools_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.search_users())
        ttk.Entry(tools_frame, textvariable=self.search_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # Nút làm mới
        ttk.Button(tools_frame, text="Làm mới", command=self.load_users).pack(side=tk.LEFT, padx=5)
        
        # Nút thêm mới
        ttk.Button(tools_frame, text="Thêm mới", command=self.add_user).pack(side=tk.LEFT, padx=5)
        
        # Treeview hiển thị danh sách người dùng
        columns = ('id', 'username', 'name', 'role', 'email', 'phone')
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show='headings')
        
        # Thiết lập các cột
        self.tree.heading('id', text='ID')
        self.tree.heading('username', text='Tên đăng nhập')
        self.tree.heading('name', text='Tên người dùng')
        self.tree.heading('role', text='Vai trò')
        self.tree.heading('email', text='Email')
        self.tree.heading('phone', text='Điện thoại')
        
        # Thiết lập độ rộng cột và căn chỉnh
        self.tree.column('id', width=80)
        self.tree.column('username', width=120)
        self.tree.column('name', width=150)
        self.tree.column('role', width=100, anchor=tk.CENTER)
        self.tree.column('email', width=180)
        self.tree.column('phone', width=100)
        
        # Thêm thanh cuộn
        scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bắt sự kiện chọn item
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
    
    def setup_detail_frame(self):
        """
        Thiết lập frame chi tiết người dùng
        """
        # Frame chứa form nhập liệu
        form_frame = ttk.Frame(self.detail_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ID (readonly)
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.id_var, state="readonly", width=30).grid(row=0, column=1, pady=5)
        
        # Tên đăng nhập
        ttk.Label(form_frame, text="Tên đăng nhập:").grid(row=1, column=0, sticky="w", pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.username_var, width=30).grid(row=1, column=1, pady=5)
        
        # Mật khẩu (chỉ hiển thị khi thêm mới)
        ttk.Label(form_frame, text="Mật khẩu:").grid(row=2, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=2, column=1, pady=5)
        
        # Tên người dùng
        ttk.Label(form_frame, text="Tên người dùng:").grid(row=3, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var, width=30).grid(row=3, column=1, pady=5)
        
        # Vai trò
        ttk.Label(form_frame, text="Vai trò:").grid(row=4, column=0, sticky="w", pady=5)
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(form_frame, textvariable=self.role_var, width=27, state="readonly")
        role_combo.grid(row=4, column=1, pady=5)
        role_combo['values'] = ["admin", "staff", "customer"]
        
        # Email
        ttk.Label(form_frame, text="Email:").grid(row=5, column=0, sticky="w", pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.email_var, width=30).grid(row=5, column=1, pady=5)
        
        # Điện thoại
        ttk.Label(form_frame, text="Điện thoại:").grid(row=6, column=0, sticky="w", pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.phone_var, width=30).grid(row=6, column=1, pady=5)
        
        # Frame chứa các nút hành động
        button_frame = ttk.Frame(self.detail_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút Lưu
        ttk.Button(button_frame, text="Lưu", command=self.save_user).pack(side=tk.LEFT, padx=5)
        
        # Nút Xóa
        ttk.Button(button_frame, text="Xóa", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        
        # Nút Đổi mật khẩu
        ttk.Button(button_frame, text="Đổi mật khẩu", command=self.change_password).pack(side=tk.LEFT, padx=5)
        
        # Vô hiệu hóa form ban đầu
        self.disable_form()
    
    def load_users(self):
        """
        Tải danh sách người dùng
        """
        # Xóa các dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Lấy danh sách người dùng
        users = self.auth_controller.data_manager.get_all_items("users.json", "users")
        
        # Thêm vào treeview
        for user in users:
            self.tree.insert('', tk.END, values=(
                user.get('id', ''),
                user.get('username', ''),
                user.get('name', ''),
                self.get_role_display(user.get('role', '')),
                user.get('email', ''),
                user.get('phone', '')
            ))
    
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
    
    def search_users(self):
        """
        Tìm kiếm người dùng
        """
        search_term = self.search_var.get().lower()
        
        # Xóa các dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Lấy danh sách người dùng
        users = self.auth_controller.data_manager.get_all_items("users.json", "users")
        
        # Lọc và thêm vào treeview
        for user in users:
            if (search_term in user.get('username', '').lower() or 
                search_term in user.get('name', '').lower() or
                search_term in user.get('email', '').lower()):
                self.tree.insert('', tk.END, values=(
                    user.get('id', ''),
                    user.get('username', ''),
                    user.get('name', ''),
                    self.get_role_display(user.get('role', '')),
                    user.get('email', ''),
                    user.get('phone', '')
                ))
    
    def on_tree_select(self, event):
        """
        Xử lý sự kiện chọn người dùng trong treeview
        """
        # Lấy item đang chọn
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Lấy ID người dùng
        item = self.tree.item(selected_items[0])
        user_id = item['values'][0]
        
        # Lấy thông tin chi tiết người dùng
        user = self.auth_controller.data_manager.get_item_by_id("users.json", "users", user_id)
        if not user:
            return
        
        # Lưu lại người dùng đang chọn
        self.selected_user = user
        
        # Hiển thị thông tin lên form
        self.id_var.set(user.get('id', ''))
        self.username_var.set(user.get('username', ''))
        self.password_var.set("")  # Không hiển thị mật khẩu
        self.name_var.set(user.get('name', ''))
        self.role_var.set(user.get('role', ''))
        self.email_var.set(user.get('email', ''))
        self.phone_var.set(user.get('phone', ''))
        
        # Ẩn trường mật khẩu khi cập nhật
        self.password_entry.grid_remove()
        
        # Kích hoạt form
        self.enable_form()
    
    def enable_form(self):
        """
        Kích hoạt form nhập liệu
        """
        self.username_var._entry.config(state="normal")
        self.name_var._entry.config(state="normal")
        self.role_var._entry.config(state="readonly")
        self.email_var._entry.config(state="normal")
        self.phone_var._entry.config(state="normal")
    
    def disable_form(self):
        """
        Vô hiệu hóa form nhập liệu
        """
        widgets = [
            self.id_var, self.username_var, self.password_var, self.name_var,
            self.role_var, self.email_var, self.phone_var
        ]
        
        for widget in widgets:
            if hasattr(widget, '_entry'):
                widget._entry.config(state="disabled")
    
    def add_user(self):
        """
        Thêm mới người dùng
        """
        # Xóa chọn hiện tại
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        
        # Xóa dữ liệu cũ trên form
        self.selected_user = None
        self.id_var.set(f"user_{uuid.uuid4().hex[:8]}")
        self.username_var.set("")
        self.password_var.set("")
        self.name_var.set("")
        self.role_var.set("customer")  # Mặc định là khách hàng
        self.email_var.set("")
        self.phone_var.set("")
        
        # Hiển thị trường mật khẩu
        self.password_entry.grid()
        
        # Kích hoạt form
        self.enable_form()
    
    def save_user(self):
        """
        Lưu thông tin người dùng
        """
        # Lấy thông tin từ form
        user_id = self.id_var.get()
        username = self.username_var.get()
        password = self.password_var.get()
        name = self.name_var.get()
        role = self.role_var.get()
        email = self.email_var.get()
        phone = self.phone_var.get()
        
        # Kiểm tra các trường bắt buộc
        if not username:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên đăng nhập!")
            return
        
        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên người dùng!")
            return
        
        if not role:
            messagebox.showerror("Lỗi", "Vui lòng chọn vai trò!")
            return
        
        if not self.selected_user and not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập mật khẩu cho người dùng mới!")
            return
        
        if self.selected_user:
            # Cập nhật người dùng
            success, message = self.auth_controller.update_user(user_id, name, role, email, phone)
            if success:
                messagebox.showinfo("Thành công", message)
                # Tải lại danh sách người dùng
                self.load_users()
            else:
                messagebox.showerror("Lỗi", message)
        else:
            # Thêm người dùng mới
            success, message = self.auth_controller.create_user(username, password, name, role, email, phone)
            if success:
                messagebox.showinfo("Thành công", message)
                # Tải lại danh sách người dùng
                self.load_users()
            else:
                messagebox.showerror("Lỗi", message)
    
    def delete_user(self):
        """
        Xóa người dùng
        """
        # Kiểm tra người dùng đang chọn
        if not self.selected_user:
            messagebox.showerror("Lỗi", "Vui lòng chọn người dùng cần xóa!")
            return
        
        # Không thể xóa người dùng hiện tại
        if self.selected_user.get('id') == self.user.get('id'):
            messagebox.showerror("Lỗi", "Không thể xóa tài khoản đang đăng nhập!")
            return
        
        # Xác nhận xóa
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa người dùng '{self.selected_user.get('username')}'?"):
            return
        
        # Xóa người dùng
        success = self.auth_controller.data_manager.delete_item("users.json", "users", self.selected_user.get('id'))
        
        if success:
            messagebox.showinfo("Thành công", "Xóa người dùng thành công!")
            # Tải lại danh sách người dùng
            self.load_users()
            # Vô hiệu hóa form
            self.disable_form()
            # Xóa người dùng đang chọn
            self.selected_user = None
        else:
            messagebox.showerror("Lỗi", "Có lỗi xảy ra khi xóa người dùng!")
    
    def change_password(self):
        """
        Đổi mật khẩu người dùng
        """
        # Kiểm tra người dùng đang chọn
        if not self.selected_user:
            messagebox.showerror("Lỗi", "Vui lòng chọn người dùng cần đổi mật khẩu!")
            return
        
        # Tạo dialog đổi mật khẩu
        change_password_dialog = tk.Toplevel(self)
        change_password_dialog.title("Đổi mật khẩu")
        change_password_dialog.geometry("400x200")
        change_password_dialog.resizable(False, False)
        change_password_dialog.transient(self)
        change_password_dialog.grab_set()
        
        # Chỉ admin mới có thể đổi mật khẩu của người khác mà không cần mật khẩu cũ
        need_old_password = self.user.get('role') != 'admin' or self.selected_user.get('id') == self.user.get('id')
        
        # Frame chứa form
        form_frame = ttk.Frame(change_password_dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mật khẩu cũ
        if need_old_password:
            ttk.Label(form_frame, text="Mật khẩu cũ:").grid(row=0, column=0, sticky="w", pady=5)
            old_password_var = tk.StringVar()
            ttk.Entry(form_frame, textvariable=old_password_var, show="*", width=30).grid(row=0, column=1, pady=5)
        
        # Mật khẩu mới
        ttk.Label(form_frame, text="Mật khẩu mới:").grid(row=1, column=0, sticky="w", pady=5)
        new_password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=new_password_var, show="*", width=30).grid(row=1, column=1, pady=5)
        
        # Xác nhận mật khẩu mới
        ttk.Label(form_frame, text="Xác nhận mật khẩu mới:").grid(row=2, column=0, sticky="w", pady=5)
        confirm_password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=confirm_password_var, show="*", width=30).grid(row=2, column=1, pady=5)
        
        # Nút hành động
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Hàm xử lý đổi mật khẩu
        def do_change_password():
            # Lấy mật khẩu
            old_password = old_password_var.get() if need_old_password else ""
            new_password = new_password_var.get()
            confirm_password = confirm_password_var.get()
            
            # Kiểm tra mật khẩu mới
            if not new_password:
                messagebox.showerror("Lỗi", "Vui lòng nhập mật khẩu mới!", parent=change_password_dialog)
                return
            
            if new_password != confirm_password:
                messagebox.showerror("Lỗi", "Mật khẩu mới không khớp!", parent=change_password_dialog)
                return
            
            # Đổi mật khẩu
            if need_old_password:
                from utils.password_utils import verify_password
                # Kiểm tra mật khẩu cũ
                if not verify_password(self.selected_user.get('password', ''), old_password):
                    messagebox.showerror("Lỗi", "Mật khẩu cũ không đúng!", parent=change_password_dialog)
                    return
            
            # Cập nhật mật khẩu
            from utils.password_utils import hash_password
            user = self.selected_user.copy()
            user['password'] = hash_password(new_password)
            
            # Lưu lại
            success = self.auth_controller.data_manager.update_item("users.json", "users", user.get('id'), user)
            
            if success:
                messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!", parent=change_password_dialog)
                change_password_dialog.destroy()
            else:
                messagebox.showerror("Lỗi", "Có lỗi xảy ra khi đổi mật khẩu!", parent=change_password_dialog)
        
        # Nút xác nhận
        ttk.Button(button_frame, text="Xác nhận", command=do_change_password).pack(side=tk.LEFT, padx=5)
        
        # Nút hủy
        ttk.Button(button_frame, text="Hủy", command=change_password_dialog.destroy).pack(side=tk.LEFT, padx=5)
        
