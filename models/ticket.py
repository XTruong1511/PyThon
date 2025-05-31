# models/ticket.py
from datetime import datetime

class Ticket:
    """
    Lớp đại diện cho một vé xem phim
    """
    def __init__(self, id="", schedule_id="", user_id="", seats=None, 
                 booking_time="", total_price=0, status="pending"):
        self.id = id
        self.schedule_id = schedule_id
        self.user_id = user_id
        self.seats = seats if seats else []
        self.booking_time = booking_time
        self.total_price = total_price
        self.status = status  # pending, confirmed, cancelled
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng Ticket từ dictionary
        """
        return cls(
            id=data.get("id", ""),
            schedule_id=data.get("schedule_id", ""),
            user_id=data.get("user_id", ""),
            seats=data.get("seats", []),
            booking_time=data.get("booking_time", ""),
            total_price=data.get("total_price", 0),
            status=data.get("status", "pending")
        )
    
    def to_dict(self):
        """
        Chuyển đối tượng Ticket thành dictionary
        """
        return {
            "id": self.id,
            "schedule_id": self.schedule_id,
            "user_id": self.user_id,
            "seats": self.seats,
            "booking_time": self.booking_time,
            "total_price": self.total_price,
            "status": self.status
        }
