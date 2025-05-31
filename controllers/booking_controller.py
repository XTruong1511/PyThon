# controllers/booking_controller.py
from models.data_manager import DataManager
import uuid
from datetime import datetime

class BookingController:
    """
    Controller xử lý logic cho đặt vé
    """
    def __init__(self):
        self.data_manager = DataManager()
    
    def get_all_schedules(self, date=None):
        """
        Lấy tất cả lịch chiếu
        Nếu có date, lọc theo ngày
        """
        schedules = self.data_manager.get_all_items("schedules.json", "schedules")
        
        if date:
            schedules = [s for s in schedules if s.get('start_time', '').startswith(date)]
        
        return schedules
    
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
    
    def get_tickets_by_schedule(self, schedule_id):
        """
        Lấy tất cả vé đã đặt cho một lịch chiếu
        """
        tickets = self.data_manager.get_all_items("tickets.json", "tickets")
        return [t for t in tickets if t.get('schedule_id') == schedule_id and t.get('status') != 'cancelled']
    
    def get_booked_seats(self, schedule_id):
        """
        Lấy danh sách ghế đã đặt cho một lịch chiếu
        """
        tickets = self.get_tickets_by_schedule(schedule_id)
        booked_seats = []
        
        for ticket in tickets:
            booked_seats.extend(ticket.get('seats', []))
        
        return booked_seats
    
    def book_ticket(self, schedule_id, user_id, seats, total_price):
        """
        Đặt vé mới
        """
        # Kiểm tra xem ghế đã được đặt chưa
        booked_seats = self.get_booked_seats(schedule_id)
        
        # Kiểm tra trùng ghế
        for seat in seats:
            if seat in booked_seats:
                return False, f"Ghế {seat} đã được đặt!"
        
        # Tạo vé mới
        ticket = {
            "id": f"ticket_{uuid.uuid4().hex[:8]}",
            "schedule_id": schedule_id,
            "user_id": user_id,
            "seats": seats,
            "booking_time": datetime.now().isoformat(),
            "total_price": total_price,
            "status": "confirmed"
        }
        
        # Lưu vé
        success = self.data_manager.append_item("tickets.json", "tickets", ticket)
        
        if success:
            return True, ticket
        else:
            return False, "Có lỗi xảy ra khi lưu vé!"
    
    def get_user_tickets(self, user_id):
        """
        Lấy tất cả vé của một người dùng
        """
        tickets = self.data_manager.get_all_items("tickets.json", "tickets")
        return [t for t in tickets if t.get('user_id') == user_id]
    
    def cancel_ticket(self, ticket_id, user_id):
        """
        Hủy vé
        """
        # Lấy thông tin vé
        ticket = self.data_manager.get_item_by_id("tickets.json", "tickets", ticket_id)
        
        if not ticket:
            return False, "Không tìm thấy vé!"
        
        # Kiểm tra quyền (chỉ hủy vé của chính mình)
        if ticket.get('user_id') != user_id:
            return False, "Bạn không có quyền hủy vé này!"
        
        # Kiểm tra trạng thái
        if ticket.get('status') == 'cancelled':
            return False, "Vé đã bị hủy trước đó!"
        
        # Kiểm tra thời gian (không thể hủy vé quá sát giờ chiếu)
        schedule = self.get_schedule_by_id(ticket.get('schedule_id'))
        if schedule:
            try:
                start_time = datetime.fromisoformat(schedule.get('start_time'))
                current_time = datetime.now()
                
                # Nếu còn ít hơn 2 giờ đến giờ chiếu, không cho hủy
                if (start_time - current_time).total_seconds() < 7200:
                    return False, "Không thể hủy vé trước giờ chiếu ít hơn 2 giờ!"
            except:
                pass
        
        # Cập nhật trạng thái vé
        ticket['status'] = 'cancelled'
        
        # Lưu lại
        success = self.data_manager.update_item("tickets.json", "tickets", ticket_id, ticket)
        
        if success:
            return True, "Hủy vé thành công!"
        else:
            return False, "Có lỗi xảy ra khi hủy vé!"
