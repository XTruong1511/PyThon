# utils/config.py
import os
from models.data_manager import DataManager
import hashlib
import uuid

def hash_password(password):
    """Mã hóa mật khẩu sử dụng SHA-256"""
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
    return f"{salt}${hashed_password}"

def check_password(stored_password, provided_password):
    """Kiểm tra mật khẩu có khớp với hash đã lưu hay không"""
    salt, hashed_password = stored_password.split('$')
    check_hash = hashlib.sha256(salt.encode() + provided_password.encode()).hexdigest()
    return check_hash == hashed_password

def setup_config():
    """Thiết lập cấu hình ban đầu cho ứng dụng"""
    data_manager = DataManager()
    
    # Khởi tạo dữ liệu người dùng mặc định nếu chưa có
    initial_users = {
        "users": [
            {
                "id": "user_001",
                "username": "admin",
                "password": hash_password("admin123"),
                "name": "Admin",
                "role": "admin",
                "email": "admin@cinema.com",
                "phone": "0123456789"
            },
            {
                "id": "user_002",
                "username": "staff",
                "password": hash_password("staff123"),
                "name": "Staff User",
                "role": "staff",
                "email": "staff@cinema.com",
                "phone": "0123456788"
            },
            {
                "id": "user_003",
                "username": "customer",
                "password": hash_password("customer123"),
                "name": "Customer",
                "role": "customer",
                "email": "customer@example.com",
                "phone": "0123456787"
            }
        ]
    }
    
    # Các cấu trúc dữ liệu JSON ban đầu
    initial_structures = {
        "users.json": initial_users,
        "movies.json": {"movies": []},
        "theaters.json": {"theaters": []},
        "schedules.json": {"schedules": []},
        "tickets.json": {"tickets": []}
    }
    
    # Khởi tạo các file dữ liệu nếu chưa tồn tại
    for file_name, initial_data in initial_structures.items():
        data_manager.initialize_data_if_empty(file_name, initial_data)
