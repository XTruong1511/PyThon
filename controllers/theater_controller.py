# controllers/theater_controller.py
from models.data_manager import DataManager
import uuid

class TheaterController:
    """
    Controller xử lý logic cho phòng chiếu
    """
    def __init__(self):
        self.data_manager = DataManager()
    
    def get_all_theaters(self):
        """
        Lấy tất cả phòng chiếu
        """
        return self.data_manager.get_all_items("theaters.json", "theaters")
    
    def get_theater_by_id(self, theater_id):
        """
        Lấy thông tin phòng chiếu theo ID
        """
        return self.data_manager.get_item_by_id("theaters.json", "theaters", theater_id)
    
    def add_theater(self, theater):
        """
        Thêm phòng chiếu mới
        """
        return self.data_manager.append_item("theaters.json", "theaters", theater)
    
    def update_theater(self, theater):
        """
        Cập nhật thông tin phòng chiếu
        """
        return self.data_manager.update_item("theaters.json", "theaters", theater.get('id'), theater)
    
    
    def check_theater_in_schedules(self, theater_id):
        """
        Kiểm tra xem phòng chiếu có đang được sử dụng trong lịch chiếu không
        """
        # Lấy tất cả lịch chiếu
        schedules = self.data_manager.get_all_items("schedules.json", "schedules")
        
        # Tìm lịch chiếu sử dụng phòng chiếu này
        theater_schedules = []
        for schedule in schedules:
            if schedule.get('theater_id') == theater_id:
                theater_schedules.append(schedule)
        
        return theater_schedules
    
    def delete_theater(self, theater_id):
        """
        Xóa phòng chiếu (cải tiến với kiểm tra ràng buộc)
        """
        # Kiểm tra xem phòng chiếu có đang được sử dụng trong lịch chiếu không
        theater_schedules = self.check_theater_in_schedules(theater_id)
        
        if theater_schedules:
            # Trả về thông tin lỗi kèm chi tiết
            return False, theater_schedules
        
        # Nếu không có lịch chiếu nào sử dụng phòng chiếu này, tiến hành xóa
        success = self.data_manager.delete_item("theaters.json", "theaters", theater_id)
        
        if success:
            return True, None
        else:
            return False, None
    
    def get_theater_types(self):
        """
        Lấy danh sách loại phòng chiếu
        """
        return ["Thường", "VIP", "3D", "IMAX", "4DX"]
    
    
    
    