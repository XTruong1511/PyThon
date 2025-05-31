# utils/api_client.py
import requests
import json
import os
from models.data_manager import DataManager

class MovieAPI:
    """
    Lớp quản lý kết nối với API phim (TMDB)
    """
    def __init__(self):
        # Thay API_KEY bằng key thực tế của bạn khi đăng ký TMDB
        self.api_key = "8938fdbabf869416151e925086a716fe"
        self.base_url = "https://api.themoviedb.org/3"
        self.data_manager = DataManager()
    
    def get_trending_movies(self, page=1):
        """
        Lấy danh sách phim thịnh hành từ TMDB
        """
        endpoint = f"{self.base_url}/trending/movie/week"
        params = {
            "api_key": self.api_key,
            "language": "vi-VN",
            "page": page
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi kết nối đến API: {e}")
            return None
    
    def get_movie_details(self, movie_id):
        """
        Lấy thông tin chi tiết của một phim
        """
        endpoint = f"{self.base_url}/movie/{movie_id}"
        params = {
            "api_key": self.api_key,
            "language": "vi-VN",
            "append_to_response": "videos,images"
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi lấy thông tin phim: {e}")
            return None
    
    def import_movies_to_json(self, num_movies=10):
        """
        Import số lượng phim cần thiết vào file JSON
        """
        # Lấy phim thịnh hành
        result = self.get_trending_movies()
        if not result or "results" not in result:
            return False
        
        movies_data = []
        count = 0
        
        for movie in result["results"]:
            if count >= num_movies:
                break
                
            # Lấy thông tin chi tiết
            movie_detail = self.get_movie_details(movie["id"])
            if not movie_detail:
                continue
            
            # Tạo đối tượng phim để lưu vào JSON
            movie_obj = {
                "id": f"movie_{movie['id']}",
                "title": movie_detail.get("title", ""),
                "director": "Đang cập nhật",  # TMDB API không trả về trực tiếp
                "duration": movie_detail.get("runtime", 0),
                "genre": [genre["name"] for genre in movie_detail.get("genres", [])],
                "release_date": movie_detail.get("release_date", ""),
                "rating": movie_detail.get("vote_average", 0),
                "description": movie_detail.get("overview", ""),
                "poster_url": f"https://image.tmdb.org/t/p/w500{movie_detail.get('poster_path', '')}",
                "trailer_url": ""
            }
            
            # Thêm trailer nếu có
            videos = movie_detail.get("videos", {}).get("results", [])
            for video in videos:
                if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                    movie_obj["trailer_url"] = f"https://www.youtube.com/watch?v={video.get('key', '')}"
                    break
            
            movies_data.append(movie_obj)
            count += 1
        
        # Đọc dữ liệu hiện tại
        current_data = self.data_manager.read_data("movies.json")
        if "movies" not in current_data:
            current_data["movies"] = []
        
        # Thêm phim mới
        current_data["movies"].extend(movies_data)
        
        # Ghi lại vào file JSON
        return self.data_manager.write_data("movies.json", current_data)
