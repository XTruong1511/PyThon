# controllers/schedule_controller.py
from models.data_manager import DataManager
import uuid
from datetime import datetime, timedelta

class ScheduleController:
    """
    Controller xử lý logic cho lịch chiếu
    """
    def __init__(self):
        self.data_manager = DataManager()
    
    def get_all_schedules(self):
        """
        Lấy tất cả lịch chiếu
        """
        return self.data_manager.get_all_items("schedules.json", "schedules")
    
    def get_schedule_by_id(self, schedule_id):
        """
        Lấy thông tin lịch chiếu theo ID
        """
        return self.data_manager.get_item_by_id("schedules.json", "schedules", schedule_id)
    
    def get_movie_by_id(self, movie_id):
        """
        Lấy thông tin phim theo ID
        """
        return self.data_manager.get_item_by_id("movies.json", "movies", movie_id)
    
    def get_theater_by_id(self, theater_id):
        """
        Lấy thông tin phòng chiếu theo ID
        """
        return self.data_manager.get_item_by_id("theaters.json", "theaters", theater_id)
    
    def add_schedule(self, schedule):
        """
        Thêm lịch chiếu mới
        """
        return self.data_manager.append_item("schedules.json", "schedules", schedule)
    
    def update_schedule(self, schedule):
        """
        Cập nhật thông tin lịch chiếu
        """
        return self.data_manager.update_item("schedules.json", "schedules", schedule.get('id'), schedule)
    
    def delete_schedule(self, schedule_id):
        """
        Xóa lịch chiếu
        """
        return self.data_manager.delete_item("schedules.json", "schedules", schedule_id)
    
    def get_all_movies(self):
        """
        Lấy tất cả phim
        """
        return self.data_manager.get_all_items("movies.json", "movies")
    
    def get_all_theaters(self):
        """
        Lấy tất cả phòng chiếu
        """
        return self.data_manager.get_all_items("theaters.json", "theaters")
    
    def check_schedule_overlap(self, theater_id, start_time, end_time, exclude_id=None):
        """
        Kiểm tra trùng lịch
        """
        # Chuyển đổi thời gian thành datetime
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        
        # Lấy tất cả lịch chiếu
        schedules = self.get_all_schedules()
        
        for schedule in schedules:
            # Bỏ qua lịch đang cập nhật
            if exclude_id and schedule.get('id') == exclude_id:
                continue
            
            # Kiểm tra cùng phòng
            if schedule.get('theater_id') != theater_id:
                continue
            
            # Chuyển đổi thời gian lịch đang kiểm tra
            try:
                s_start = datetime.fromisoformat(schedule.get('start_time'))
                s_end = datetime.fromisoformat(schedule.get('end_time'))
                
                # Kiểm tra trùng lịch
                if (start < s_end and end > s_start):
                    return True, schedule
            except:
                # Bỏ qua các lịch có định dạng thời gian không hợp lệ
                pass
        
        return False, None
    
    def calculate_end_time(self, start_time, movie_id):
        """
        Tính thời gian kết thúc dự kiến dựa trên thời lượng phim và thời gian bắt đầu
        """
        # Lấy thông tin phim
        movie = self.get_movie_by_id(movie_id)
        if not movie:
            return None
        
        # Lấy thời lượng phim (phút)
        duration = movie.get('duration', 0)
        
        # Tính thời gian kết thúc
        try:
            start = datetime.fromisoformat(start_time)
            end = start + timedelta(minutes=duration)
            return end.isoformat()
        except:
            return None
    
    def get_schedules_by_date(self, date):
        """
        Lấy danh sách lịch chiếu theo ngày
        """
        schedules = self.get_all_schedules()
        return [s for s in schedules if s.get('start_time', '').startswith(date)]
    
    def get_schedules_by_movie(self, movie_id):
        """
        Lấy danh sách lịch chiếu theo phim
        """
        schedules = self.get_all_schedules()
        return [s for s in schedules if s.get('movie_id') == movie_id]
    
    def get_schedules_by_theater(self, theater_id):
        """
        Lấy danh sách lịch chiếu theo phòng chiếu
        """
        schedules = self.get_all_schedules()
        return [s for s in schedules if s.get('theater_id') == theater_id]
