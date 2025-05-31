# controllers/movie_controller.py
from models.data_manager import DataManager
from utils.api_client import MovieAPI
import uuid

class MovieController:
    """
    Controller xử lý logic cho phim
    """
    def __init__(self):
        self.data_manager = DataManager()
        self.api_client = MovieAPI()
    
    def get_all_movies(self):
        """
        Lấy tất cả phim
        """
        return self.data_manager.get_all_items("movies.json", "movies")
    
    def get_movie_by_id(self, movie_id):
        """
        Lấy thông tin phim theo ID
        """
        return self.data_manager.get_item_by_id("movies.json", "movies", movie_id)
    
    def add_movie(self, movie):
        """
        Thêm phim mới
        """
        return self.data_manager.append_item("movies.json", "movies", movie)
    
    def update_movie(self, movie):
        """
        Cập nhật thông tin phim
        """
        return self.data_manager.update_item("movies.json", "movies", movie.get('id'), movie)
    
    def delete_movie(self, movie_id):
        """
        Xóa phim (cải tiến với kiểm tra ràng buộc)
        """
        # Kiểm tra xem phim có đang được sử dụng trong lịch chiếu không
        movie_schedules = self.check_movie_in_schedules(movie_id)
        
        if movie_schedules:
            # Trả về thông tin lỗi kèm chi tiết
            return False, movie_schedules
        
        # Nếu không có lịch chiếu nào sử dụng phim này, tiến hành xóa
        success = self.data_manager.delete_item("movies.json", "movies", movie_id)
        
        if success:
            return True, None
        else:
            return False, None
    
    def import_from_api(self, num_movies=10):
        """
        Import phim từ API
        """
        return self.api_client.import_movies_to_json(num_movies)
    
    def search_movies(self, keyword):
        """
        Tìm kiếm phim theo từ khóa
        """
        movies = self.get_all_movies()
        result = []
        
        for movie in movies:
            if (keyword.lower() in movie.get('title', '').lower() or 
                keyword.lower() in movie.get('director', '').lower() or
                any(keyword.lower() in genre.lower() for genre in movie.get('genre', []))):
                result.append(movie)
        
        return result
    
    def check_movie_in_schedules(self, movie_id):
        """
        Kiểm tra xem phim có đang được sử dụng trong lịch chiếu không
        """
        # Lấy tất cả lịch chiếu
        schedules = self.data_manager.get_all_items("schedules.json", "schedules")
        
        # Tìm lịch chiếu sử dụng phim này
        movie_schedules = []
        for schedule in schedules:
            if schedule.get('movie_id') == movie_id:
                movie_schedules.append(schedule)
        
        return movie_schedules
    
    
