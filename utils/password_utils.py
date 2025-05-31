# utils/password_utils.py
import hashlib
import uuid

def hash_password(password):
    """
    Mã hóa mật khẩu bằng SHA-256 với salt
    """
    salt = uuid.uuid4().hex
    return salt + "$" + hashlib.sha256(salt.encode() + password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """
    Kiểm tra mật khẩu có khớp với hash đã lưu
    """
    salt, hash_value = stored_password.split("$")
    calculated_hash = hashlib.sha256(salt.encode() + provided_password.encode()).hexdigest()
    return calculated_hash == hash_value
