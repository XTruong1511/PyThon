# models/schedule.py
from datetime import datetime

class Schedule:
    """
    Lớp đại diện cho một lịch chiếu
    """
    def __init__(self, id="", movie_id="", theater_id="", start_time="", end_time="", price=None):
        self.id = id
        self.movie_id = movie_id
        self.theater_id = theater_id
        self.start_time = start_time
        self.end_time = end_time
        self.price = price if price else {"normal": 0, "vip": 0}
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng Schedule từ dictionary
        """
        return cls(
            id=data.get("id", ""),
            movie_id=data.get("movie_id", ""),
            theater_id=data.get("theater_id", ""),
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
            price=data.get("price", {"normal": 0, "vip": 0})
        )
    
    def to_dict(self):
        """
        Chuyển đối tượng Schedule thành dictionary
        """
        return {
            "id": self.id,
            "movie_id": self.movie_id,
            "theater_id": self.theater_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "price": self.price
        }
