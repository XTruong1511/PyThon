# models/data_manager.py
import json
import os
from pathlib import Path

class DataManager:
    """
    Lớp quản lý đọc/ghi dữ liệu JSON
    """
    def __init__(self, data_folder="data"):
        """
        Khởi tạo DataManager với đường dẫn thư mục dữ liệu
        """
        self.data_folder = data_folder
        # Đảm bảo thư mục tồn tại
        os.makedirs(data_folder, exist_ok=True)
        
    def _get_file_path(self, file_name):
        """
        Lấy đường dẫn đầy đủ đến file dữ liệu
        """
        return os.path.join(self.data_folder, file_name)
    
    def read_data(self, file_name):
        """
        Đọc dữ liệu từ file JSON
        """
        file_path = self._get_file_path(file_name)
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                # Nếu file không tồn tại, trả về dictionary rỗng
                return {}
        except json.JSONDecodeError:
            # Nếu file không phải định dạng JSON hợp lệ
            return {}
        except Exception as e:
            print(f"Lỗi khi đọc file {file_name}: {str(e)}")
            return {}
    
    def write_data(self, file_name, data):
        """
        Ghi dữ liệu vào file JSON
        """
        file_path = self._get_file_path(file_name)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Lỗi khi ghi file {file_name}: {str(e)}")
            return False
    
    def append_item(self, file_name, collection_name, item):
        """
        Thêm một item vào collection trong file JSON
        Ví dụ: append_item('movies.json', 'movies', movie_object)
        """
        data = self.read_data(file_name)
        
        # Nếu collection chưa tồn tại, tạo mới
        if collection_name not in data:
            data[collection_name] = []
        
        # Thêm item vào collection
        data[collection_name].append(item)
        
        # Ghi lại vào file
        return self.write_data(file_name, data)
    
    def update_item(self, file_name, collection_name, item_id, updated_item):
        """
        Cập nhật một item trong collection dựa vào ID
        """
        data = self.read_data(file_name)
        
        if collection_name not in data:
            return False
        
        # Tìm và cập nhật item
        found = False
        for i, item in enumerate(data[collection_name]):
            if item.get('id') == item_id:
                data[collection_name][i] = updated_item
                found = True
                break
        
        if not found:
            return False
        
        # Ghi lại vào file
        return self.write_data(file_name, data)
    
    def delete_item(self, file_name, collection_name, item_id):
        """
        Xóa một item trong collection dựa vào ID
        """
        data = self.read_data(file_name)
        
        if collection_name not in data:
            return False
        
        # Tìm và xóa item
        initial_length = len(data[collection_name])
        data[collection_name] = [item for item in data[collection_name] if item.get('id') != item_id]
        
        if len(data[collection_name]) == initial_length:
            # Không tìm thấy item để xóa
            return False
        
        # Ghi lại vào file
        return self.write_data(file_name, data)
    
    def get_all_items(self, file_name, collection_name):
        """
        Lấy tất cả item trong một collection
        """
        data = self.read_data(file_name)
        return data.get(collection_name, [])
    
    def get_item_by_id(self, file_name, collection_name, item_id):
        """
        Lấy một item dựa vào ID
        """
        items = self.get_all_items(file_name, collection_name)
        for item in items:
            if item.get('id') == item_id:
                return item
        return None
    
    def initialize_data_if_empty(self, file_name, initial_data):
        """
        Khởi tạo dữ liệu mặc định nếu file rỗng hoặc không tồn tại
        """
        file_path = self._get_file_path(file_name)
        
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return self.write_data(file_name, initial_data)
        return True
