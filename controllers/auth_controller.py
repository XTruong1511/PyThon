# controllers/auth_controller.py
from models.data_manager import DataManager
from utils.password_utils import verify_password
import uuid

class AuthController:
    """
    Controller xử lý đăng nhập và phân quyền
    """
    def __init__(self):
        self.data_manager = DataManager()
        self.current_user = None
    
    def login(self, username, password):
        """
        Xác thực đăng nhập
        """
        users = self.data_manager.get_all_items("users.json", "users")
        
        for user in users:
            if user.get("username") == username:
                # Kiểm tra mật khẩu
                if verify_password(user.get("password", ""), password):
                    self.current_user = user
                    return user
                break
        
        return None
    
    def logout(self):
        """
        Đăng xuất
        """
        self.current_user = None
    
    def get_current_user(self):
        """
        Lấy thông tin người dùng hiện tại
        """
        return self.current_user
    
    def check_permission(self, required_role):
        """
        Kiểm tra xem người dùng hiện tại có quyền cần thiết không
        """
        if not self.current_user:
            return False
        
        # Nếu cần quyền admin, chỉ admin mới có thể truy cập
        if required_role == "admin":
            return self.current_user.get("role") == "admin"
        
        # Nếu cần quyền staff, cả admin và staff đều có thể truy cập
        elif required_role == "staff":
            return self.current_user.get("role") in ["admin", "staff"]
        
        # Nếu cần quyền customer, tất cả các loại người dùng đều có thể truy cập
        elif required_role == "customer":
            return True
        
        return False
    
    def create_user(self, username, password, name, role, email, phone):
        """
        Tạo người dùng mới
        """
        from utils.password_utils import hash_password
        
        # Kiểm tra username đã tồn tại chưa
        users = self.data_manager.get_all_items("users.json", "users")
        for user in users:
            if user.get("username") == username:
                return False, "Tên đăng nhập đã tồn tại!"
        
        # Tạo ID mới
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        # Tạo người dùng mới
        new_user = {
            "id": user_id,
            "username": username,
            "password": hash_password(password),
            "name": name,
            "role": role,
            "email": email,
            "phone": phone
        }
        
        # Thêm vào dữ liệu
        if self.data_manager.append_item("users.json", "users", new_user):
            return True, "Tạo tài khoản thành công!"
        else:
            return False, "Lỗi khi lưu dữ liệu!"
    
    def update_user(self, user_id, name, role, email, phone):
        """
        Cập nhật thông tin người dùng
        """
        # Lấy thông tin người dùng hiện tại
        user = self.data_manager.get_item_by_id("users.json", "users", user_id)
        if not user:
            return False, "Không tìm thấy người dùng!"
        
        # Cập nhật thông tin
        user["name"] = name
        user["role"] = role
        user["email"] = email
        user["phone"] = phone
        
        # Lưu lại
        if self.data_manager.update_item("users.json", "users", user_id, user):
            return True, "Cập nhật thông tin người dùng thành công!"
        else:
            return False, "Lỗi khi lưu dữ liệu!"
    
    def change_password(self, user_id, old_password, new_password):
        """
        Đổi mật khẩu người dùng
        """
        from utils.password_utils import hash_password
        
        # Lấy thông tin người dùng
        user = self.data_manager.get_item_by_id("users.json", "users", user_id)
        if not user:
            return False, "Không tìm thấy người dùng!"
        
        # Kiểm tra mật khẩu cũ
        if not verify_password(user.get("password", ""), old_password):
            return False, "Mật khẩu cũ không đúng!"
        
        # Cập nhật mật khẩu mới
        user["password"] = hash_password(new_password)
        
        # Lưu lại
        if self.data_manager.update_item("users.json", "users", user_id, user):
            return True, "Đổi mật khẩu thành công!"
        else:
            return False, "Lỗi khi lưu dữ liệu!"
