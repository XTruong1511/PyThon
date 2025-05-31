# views/booking_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
from controllers.booking_controller import BookingController
import uuid
from datetime import datetime, timedelta
from tkcalendar import DateEntry

class BookingView(ttk.Frame):
    """
    Giao diện đặt vé
    """
    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.auth_controller = AuthController()
        self.auth_controller.current_user = user
        self.booking_controller = BookingController()
        
        # Biến lưu trữ thông tin lịch chiếu đang chọn
        self.selected_schedule = None
        
        # Biến lưu trữ ghế đã chọn
        self.selected_seats = []
        
        # Thiết lập giao diện
        self.setup_ui()
        
        # Mặc định hiển thị tab "Đặt vé"
        self.notebook.select(0)
        
        # Load dữ liệu lịch chiếu cho ngày hiện tại
        self.load_schedules()

    def setup_ui(self):
        """
        Thiết lập các thành phần giao diện
        """
        # Notebook với 2 tab: Đặt vé và Lịch sử đặt vé
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab Đặt vé
        self.booking_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.booking_tab, text="Đặt vé")
        
        # Tab Lịch sử đặt vé
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="Lịch sử đặt vé")
        
        # Thiết lập tab Đặt vé
        self.setup_booking_tab()
        
        # Thiết lập tab Lịch sử đặt vé
        self.setup_history_tab()
    
    def setup_booking_tab(self):
        """
        Thiết lập tab Đặt vé
        """
        # Frame chính chia làm 2 phần: danh sách lịch chiếu và sơ đồ ghế
        self.booking_paned = ttk.PanedWindow(self.booking_tab, orient=tk.HORIZONTAL)
        self.booking_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame danh sách lịch chiếu
        self.schedule_frame = ttk.LabelFrame(self.booking_paned, text="Chọn lịch chiếu")
        self.booking_paned.add(self.schedule_frame, weight=1)
        
        # Frame sơ đồ ghế
        self.seat_frame = ttk.LabelFrame(self.booking_paned, text="Chọn ghế")
        self.booking_paned.add(self.seat_frame, weight=2)
        
        # Thiết lập frame danh sách lịch chiếu
        self.setup_schedule_frame()
        
        # Thiết lập frame sơ đồ ghế
        self.setup_seat_frame()
    
    def setup_schedule_frame(self):
        """
        Thiết lập frame danh sách lịch chiếu
        """
        # Frame chứa công cụ
        tools_frame = ttk.Frame(self.schedule_frame)
        tools_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Chọn ngày
        ttk.Label(tools_frame, text="Chọn ngày:").pack(side=tk.LEFT, padx=5)
        self.date_filter = DateEntry(tools_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2)
        self.date_filter.pack(side=tk.LEFT, padx=5)
        
        # Nút tìm kiếm
        ttk.Button(tools_frame, text="Tìm kiếm", command=self.load_schedules).pack(side=tk.LEFT, padx=5)
        
        # Treeview hiển thị danh sách lịch chiếu
        columns = ('id', 'movie', 'theater', 'time', 'price')
        self.schedule_tree = ttk.Treeview(self.schedule_frame, columns=columns, show='headings')
        
        # Thiết lập các cột
        self.schedule_tree.heading('id', text='ID')
        self.schedule_tree.heading('movie', text='Phim')
        self.schedule_tree.heading('theater', text='Phòng chiếu')
        self.schedule_tree.heading('time', text='Thời gian')
        self.schedule_tree.heading('price', text='Giá vé')
        
        # Thiết lập độ rộng cột và căn chỉnh
        self.schedule_tree.column('id', width=80)
        self.schedule_tree.column('movie', width=150)
        self.schedule_tree.column('theater', width=100)
        self.schedule_tree.column('time', width=130, anchor=tk.CENTER)
        self.schedule_tree.column('price', width=100, anchor=tk.CENTER)
        
        # Thêm thanh cuộn
        scrollbar = ttk.Scrollbar(self.schedule_frame, orient=tk.VERTICAL, command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.schedule_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bắt sự kiện chọn item
        self.schedule_tree.bind('<<TreeviewSelect>>', self.on_schedule_select)
    
    def setup_seat_frame(self):
        """
        Thiết lập frame sơ đồ ghế
        """
        # Frame thông tin phim và lịch chiếu
        self.movie_info_frame = ttk.LabelFrame(self.seat_frame, text="Thông tin phim")
        self.movie_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Labels hiển thị thông tin
        self.movie_title_label = ttk.Label(self.movie_info_frame, text="", font=("Arial", 12, "bold"))
        self.movie_title_label.pack(anchor="w", padx=5, pady=2)
        
        self.movie_theater_label = ttk.Label(self.movie_info_frame, text="")
        self.movie_theater_label.pack(anchor="w", padx=5, pady=2)
        
        self.movie_time_label = ttk.Label(self.movie_info_frame, text="")
        self.movie_time_label.pack(anchor="w", padx=5, pady=2)
        
        # Frame sơ đồ ghế
        self.seat_map_frame = ttk.LabelFrame(self.seat_frame, text="Sơ đồ ghế")
        self.seat_map_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas hiển thị sơ đồ ghế
        self.seat_canvas = tk.Canvas(self.seat_map_frame, bg="white")
        self.seat_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame thông tin đặt vé
        self.booking_info_frame = ttk.LabelFrame(self.seat_frame, text="Thông tin đặt vé")
        self.booking_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Frame hiển thị ghế đã chọn
        info_grid = ttk.Frame(self.booking_info_frame)
        info_grid.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_grid, text="Ghế đã chọn:").grid(row=0, column=0, sticky="w", pady=5)
        self.selected_seats_var = tk.StringVar()
        ttk.Entry(info_grid, textvariable=self.selected_seats_var, state="readonly", width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(info_grid, text="Tổng tiền:").grid(row=1, column=0, sticky="w", pady=5)
        self.total_price_var = tk.StringVar()
        ttk.Entry(info_grid, textvariable=self.total_price_var, state="readonly", width=30).grid(row=1, column=1, pady=5)
        
        # Nút đặt vé
        self.book_button = ttk.Button(self.booking_info_frame, text="Đặt vé", command=self.book_ticket)
        self.book_button.pack(pady=10)
        self.book_button.state(['disabled'])
        
        # Frame chú thích
        legend_frame = ttk.LabelFrame(self.seat_frame, text="Chú thích")
        legend_frame.pack(fill=tk.X, padx=5, pady=5)

        legend_grid = ttk.Frame(legend_frame)
        legend_grid.pack(padx=5, pady=5)

        # Canvas hiển thị chú thích
        available_canvas = tk.Canvas(legend_grid, width=20, height=20, bg="lightblue")
        available_canvas.grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(legend_grid, text="Ghế thường").grid(row=0, column=1, sticky="w", padx=5)

        selected_canvas = tk.Canvas(legend_grid, width=20, height=20, bg="lightgreen")
        selected_canvas.grid(row=0, column=2, padx=5, pady=2)
        ttk.Label(legend_grid, text="Ghế đã chọn").grid(row=0, column=3, sticky="w", padx=5)

        booked_canvas = tk.Canvas(legend_grid, width=20, height=20, bg="red")
        booked_canvas.grid(row=1, column=0, padx=5, pady=2)
        ttk.Label(legend_grid, text="Ghế đã đặt").grid(row=1, column=1, sticky="w", padx=5)

        vip_canvas = tk.Canvas(legend_grid, width=20, height=20, bg="gold")
        vip_canvas.grid(row=1, column=2, padx=5, pady=2)
        ttk.Label(legend_grid, text="Ghế VIP (2 hàng cuối)").grid(row=1, column=3, sticky="w", padx=5)
    
    def setup_history_tab(self):
        """
        Thiết lập tab Lịch sử đặt vé
        """
        # Frame chứa danh sách vé đã đặt
        history_frame = ttk.Frame(self.history_tab)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame chứa các nút điều khiển
        control_frame = ttk.Frame(history_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Nút làm mới
        ttk.Button(control_frame, text="Làm mới", command=self.load_ticket_history).pack(side=tk.LEFT, padx=5)
        
        # Nút hủy vé
        self.cancel_button = ttk.Button(control_frame, text="Hủy vé", 
                                    command=self.cancel_selected_ticket, 
                                    state='disabled')
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Treeview hiển thị danh sách vé đã đặt (BỎ CỘT "actions")
        columns = ('id', 'movie', 'theater', 'time', 'seats', 'price', 'status')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings')
        
        # Thiết lập các cột
        self.history_tree.heading('id', text='ID')
        self.history_tree.heading('movie', text='Phim')
        self.history_tree.heading('theater', text='Phòng chiếu')
        self.history_tree.heading('time', text='Thời gian')
        self.history_tree.heading('seats', text='Ghế')
        self.history_tree.heading('price', text='Tổng tiền')
        self.history_tree.heading('status', text='Trạng thái')
        
        # Thiết lập độ rộng cột và căn chỉnh
        self.history_tree.column('id', width=80)
        self.history_tree.column('movie', width=150)
        self.history_tree.column('theater', width=100)
        self.history_tree.column('time', width=130, anchor=tk.CENTER)
        self.history_tree.column('seats', width=100, anchor=tk.CENTER)
        self.history_tree.column('price', width=100, anchor=tk.CENTER)
        self.history_tree.column('status', width=100, anchor=tk.CENTER)
        
        # Thêm thanh cuộn
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bắt sự kiện chọn item để kích hoạt/vô hiệu hóa nút hủy vé
        self.history_tree.bind('<<TreeviewSelect>>', self.on_history_select)
        
        # Nạp dữ liệu lịch sử đặt vé
        self.load_ticket_history()
    
    def load_schedules(self):
        """
        Tải danh sách lịch chiếu theo ngày đã chọn
        """
        # Xóa các dữ liệu cũ
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        
        # Lấy ngày đã chọn
        selected_date = self.date_filter.get_date().strftime("%Y-%m-%d")
        
        # Lấy danh sách lịch chiếu
        schedules = self.booking_controller.get_all_schedules(selected_date)
        
        # Thêm vào treeview
        for schedule in schedules:
            # Lấy thông tin phim và phòng chiếu
            movie = self.booking_controller.get_movie_by_id(schedule.get('movie_id', ''))
            theater = self.booking_controller.get_theater_by_id(schedule.get('theater_id', ''))
            
            movie_title = movie.get('title', 'N/A') if movie else 'N/A'
            theater_name = theater.get('name', 'N/A') if theater else 'N/A'
            
            # Format thời gian
            start_time = self.format_datetime(schedule.get('start_time', ''))
            
            # Lấy giá vé
            price = schedule.get('price', {})
            normal_price = price.get('normal', 0)
            
            self.schedule_tree.insert('', tk.END, values=(
                schedule.get('id', ''),
                movie_title,
                theater_name,
                start_time,
                f"{normal_price:,} VND"
            ))
    
    def on_schedule_select(self, event):
        """
        Xử lý sự kiện chọn lịch chiếu
        """
        # Xóa các dữ liệu cũ
        self.selected_schedule = None
        self.selected_seats = []
        self.selected_seats_var.set("")
        self.total_price_var.set("")
        self.book_button.state(['disabled'])
        
        # Lấy item đang chọn
        selected_items = self.schedule_tree.selection()
        if not selected_items:
            return
        
        # Lấy ID lịch chiếu
        item = self.schedule_tree.item(selected_items[0])
        schedule_id = item['values'][0]
        
        # Lấy thông tin chi tiết lịch chiếu
        schedule = self.booking_controller.get_schedule_by_id(schedule_id)
        if not schedule:
            return
        
        # Lưu lại lịch chiếu đang chọn
        self.selected_schedule = schedule
        
        # Hiển thị thông tin lịch chiếu
        self.show_schedule_info(schedule)
        
        # Vẽ sơ đồ ghế
        self.draw_seat_map(schedule)
    
    def show_schedule_info(self, schedule):
        """
        Hiển thị thông tin lịch chiếu
        """
        # Lấy thông tin phim và phòng chiếu
        movie = self.booking_controller.get_movie_by_id(schedule.get('movie_id', ''))
        theater = self.booking_controller.get_theater_by_id(schedule.get('theater_id', ''))
        
        if movie:
            self.movie_title_label.config(text=movie.get('title', ''))
        else:
            self.movie_title_label.config(text="N/A")
        
        if theater:
            self.movie_theater_label.config(text=f"Phòng chiếu: {theater.get('name', '')} - {theater.get('type', '')}")
        else:
            self.movie_theater_label.config(text="Phòng chiếu: N/A")
        
        # Format thời gian
        start_time = self.format_datetime(schedule.get('start_time', ''))
        end_time = self.format_datetime(schedule.get('end_time', ''))
        
        self.movie_time_label.config(text=f"Thời gian: {start_time} - {end_time}")
    
    def draw_seat_map(self, schedule):
        """
        Vẽ sơ đồ ghế
        """
        # Xóa nội dung canvas cũ
        self.seat_canvas.delete("all")
        
        # Lấy thông tin phòng chiếu
        theater_id = schedule.get('theater_id', '')
        theater = self.booking_controller.get_theater_by_id(theater_id)
        
        if not theater:
            self.seat_canvas.create_text(150, 100, text="Không tìm thấy thông tin phòng chiếu", fill="red")
            return
        
        # Lấy thông tin layout
        layout = theater.get('layout', {'rows': 0, 'cols': 0})
        rows = layout.get('rows', 0)
        cols = layout.get('cols', 0)
        
        if rows <= 0 or cols <= 0:
            self.seat_canvas.create_text(150, 100, text="Chưa thiết lập sơ đồ ghế", fill="red")
            return
        
        # Lấy danh sách ghế đã đặt
        booked_seats = self.booking_controller.get_booked_seats(schedule.get('id', ''))
        
        # Tính kích thước ghế
        canvas_width = self.seat_canvas.winfo_width()
        canvas_height = self.seat_canvas.winfo_height()
        
        seat_width = min(30, (canvas_width - 20) / cols)
        seat_height = min(30, (canvas_height - 20) / rows)
        
        # Tính toán vị trí bắt đầu để căn giữa
        start_x = (canvas_width - (cols * seat_width)) / 2
        start_y = (canvas_height - (rows * seat_height)) / 2
        
        # Vẽ các ghế
        for row in range(rows):
            for col in range(cols):
                x1 = start_x + col * seat_width
                y1 = start_y + row * seat_height
                x2 = x1 + seat_width - 2
                y2 = y1 + seat_height - 2
                
                # Tạo nhãn ghế (A1, A2, ...)
                seat_label = f"{chr(65 + row)}{col + 1}"
                
                # Kiểm tra ghế đã đặt
                if seat_label in booked_seats:
                    fill_color = "red"  # Đã đặt
                    state = "disabled"
                elif row >= rows - 2:  # ĐỔI LOGIC: 2 hàng cuối là ghế VIP
                    fill_color = "gold"  # Ghế VIP
                    state = "normal"
                else:
                    fill_color = "lightblue"  # Ghế thường
                    state = "normal"
                
                # Kiểm tra ghế đang chọn
                if seat_label in self.selected_seats:
                    fill_color = "lightgreen"  # Đang chọn
                
                # Vẽ ghế
                seat_id = self.seat_canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    fill=fill_color, 
                    outline="blue",
                    tags=(seat_label, state)
                )
                
                # Vẽ nhãn ghế
                text_id = self.seat_canvas.create_text(
                    (x1 + x2) / 2, 
                    (y1 + y2) / 2, 
                    text=seat_label, 
                    font=("Arial", 8),
                    tags=(seat_label, state)
                )
                
                # Gắn sự kiện click chuột
                if state == "normal":
                    self.seat_canvas.tag_bind(seat_label, "<Button-1>", self.on_seat_click)
        
        # Vẽ màn hình
        screen_width = cols * seat_width
        self.seat_canvas.create_rectangle(
            start_x, start_y - 20, 
            start_x + screen_width, start_y - 10, 
            fill="white", outline="black"
        )
        self.seat_canvas.create_text(
            start_x + screen_width / 2, 
            start_y - 15, 
            text="MÀN HÌNH", 
            font=("Arial", 8, "bold")
        )
   
    def on_seat_click(self, event):
        """
        Xử lý sự kiện click vào ghế
        """
        # Lấy ID của đối tượng được click
        clicked_item = self.seat_canvas.find_closest(event.x, event.y)[0]
        
        # Lấy tags của đối tượng
        tags = self.seat_canvas.gettags(clicked_item)
        
        # Lấy tên ghế (tag đầu tiên)
        seat_label = tags[0]
        
        # Kiểm tra trạng thái ghế
        if "disabled" in tags:
            return
        
        # Cập nhật danh sách ghế đã chọn
        if seat_label in self.selected_seats:
            # Bỏ chọn ghế
            self.selected_seats.remove(seat_label)
            
            # Cập nhật màu sắc (về màu ban đầu)
            items = self.seat_canvas.find_withtag(seat_label)
            for item in items:
                if item != clicked_item:  # Chỉ cập nhật hình chữ nhật, không cập nhật text
                    tags = self.seat_canvas.gettags(item)
                    if "A" <= seat_label[0] <= "B":  # 2 hàng đầu là ghế VIP
                        self.seat_canvas.itemconfig(item, fill="gold")
                    else:
                        self.seat_canvas.itemconfig(item, fill="lightblue")
        else:
            # Chọn ghế
            self.selected_seats.append(seat_label)
            
            # Cập nhật màu sắc (xanh lá cây)
            items = self.seat_canvas.find_withtag(seat_label)
            for item in items:
                if item != clicked_item:  # Chỉ cập nhật hình chữ nhật, không cập nhật text
                    self.seat_canvas.itemconfig(item, fill="lightgreen")
        
        # Cập nhật thông tin ghế đã chọn
        self.selected_seats_var.set(", ".join(sorted(self.selected_seats)))
        
        # Tính tổng tiền
        self.calculate_total_price()
        
        # Kích hoạt nút đặt vé nếu có ghế được chọn
        if self.selected_seats:
            self.book_button.state(['!disabled'])
        else:
            self.book_button.state(['disabled'])
    
    def calculate_total_price(self):
        """
        Tính tổng tiền dựa trên ghế đã chọn
        """
        if not self.selected_schedule or not self.selected_seats:
            self.total_price_var.set("")
            return
        
        # Lấy thông tin phòng chiếu để biết số hàng
        theater_id = self.selected_schedule.get('theater_id', '')
        theater = self.booking_controller.get_theater_by_id(theater_id)
        
        if not theater:
            self.total_price_var.set("")
            return
        
        # Lấy số hàng từ layout
        layout = theater.get('layout', {'rows': 0, 'cols': 0})
        rows = layout.get('rows', 0)
        
        # Lấy giá vé
        price = self.selected_schedule.get('price', {})
        normal_price = price.get('normal', 0)
        vip_price = price.get('vip', 0)
        
        # Tính tổng tiền
        total = 0
        for seat in self.selected_seats:
            # Lấy số thứ tự hàng từ ký tự đầu (A=0, B=1, ...)
            seat_row = ord(seat[0]) - ord('A')
            
            # ĐỔI LOGIC: Kiểm tra 2 hàng cuối
            if seat_row >= rows - 2:  # 2 hàng cuối là ghế VIP
                total += vip_price
            else:
                total += normal_price
        
        # Hiển thị tổng tiền
        self.total_price_var.set(f"{total:,} VND")
    
    def book_ticket(self):
        """
        Đặt vé
        """
        if not self.selected_schedule or not self.selected_seats:
            messagebox.showerror("Lỗi", "Vui lòng chọn lịch chiếu và ghế!")
            return
        
        # Lấy tổng tiền
        total_text = self.total_price_var.get().replace(",", "").replace("VND", "").strip()
        try:
            total_price = int(total_text)
        except:
            messagebox.showerror("Lỗi", "Tổng tiền không hợp lệ!")
            return
        
        # Xác nhận đặt vé
        movie = self.booking_controller.get_movie_by_id(self.selected_schedule.get('movie_id', ''))
        movie_title = movie.get('title', 'N/A') if movie else 'N/A'
        
        confirm_message = f"Xác nhận đặt vé xem phim '{movie_title}'?\n"
        confirm_message += f"Ghế: {', '.join(sorted(self.selected_seats))}\n"
        confirm_message += f"Tổng tiền: {self.total_price_var.get()}"
        
        if not messagebox.askyesno("Xác nhận đặt vé", confirm_message):
            return
        
        # Thực hiện đặt vé
        success, result = self.booking_controller.book_ticket(
            self.selected_schedule.get('id', ''),
            self.user.get('id', ''),
            self.selected_seats,
            total_price
        )
        
        if success:
            messagebox.showinfo("Thành công", "Đặt vé thành công!")
            
            # Cập nhật lại sơ đồ ghế
            self.draw_seat_map(self.selected_schedule)
            
            # Xóa ghế đã chọn
            self.selected_seats = []
            self.selected_seats_var.set("")
            self.total_price_var.set("")
            
            # Vô hiệu hóa nút đặt vé
            self.book_button.state(['disabled'])
            
            # Chuyển sang tab lịch sử đặt vé
            self.notebook.select(1)
            
            # Tải lại lịch sử đặt vé
            self.load_ticket_history()
        else:
            messagebox.showerror("Lỗi", f"Đặt vé thất bại: {result}")
    
    def load_ticket_history(self):
        """
        Tải lịch sử đặt vé
        """
        # Xóa các dữ liệu cũ
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Lấy danh sách vé đã đặt
        tickets = self.booking_controller.get_user_tickets(self.user.get('id', ''))
        
        # Thêm vào treeview
        for ticket in tickets:
            # Lấy thông tin lịch chiếu
            schedule = self.booking_controller.get_schedule_by_id(ticket.get('schedule_id', ''))
            if not schedule:
                continue
            
            # Lấy thông tin phim và phòng chiếu
            movie = self.booking_controller.get_movie_by_id(schedule.get('movie_id', ''))
            theater = self.booking_controller.get_theater_by_id(schedule.get('theater_id', ''))
            
            movie_title = movie.get('title', 'N/A') if movie else 'N/A'
            theater_name = theater.get('name', 'N/A') if theater else 'N/A'
            
            # Format thời gian
            start_time = self.format_datetime(schedule.get('start_time', ''))
            
            # Trạng thái vé
            status = ticket.get('status', '')
            if status == 'confirmed':
                status_text = "Đã xác nhận"
            elif status == 'cancelled':
                status_text = "Đã hủy"
            else:
                status_text = "Đang xử lý"
            
            # Thêm vào treeview (BỎ CỘT "Thao tác")
            item_id = self.history_tree.insert('', tk.END, values=(
                ticket.get('id', ''),
                movie_title,
                theater_name,
                start_time,
                ", ".join(sorted(ticket.get('seats', []))),
                f"{ticket.get('total_price', 0):,} VND",
                status_text
            ))
        
        # Vô hiệu hóa nút hủy vé ban đầu
        self.cancel_button.config(state='disabled')

    # def on_cancel_ticket(self, event, ticket_id):
    #     """
    #     Xử lý sự kiện hủy vé
    #     """
    #     # Lấy cột đã click
    #     col = self.history_tree.identify_column(event.x)
        
    #     # Nếu click vào cột "Thao tác"
    #     if col == "#8":  # Cột thứ 8 (cột "Thao tác")
    #         # Xác nhận hủy vé
    #         if not messagebox.askyesno("Xác nhận hủy vé", "Bạn có chắc chắn muốn hủy vé này không?"):
    #             return
            
    #         # Thực hiện hủy vé
    #         success, message = self.booking_controller.cancel_ticket(ticket_id, self.user.get('id', ''))
            
    #         if success:
    #             messagebox.showinfo("Thành công", message)
    #             # Tải lại lịch sử đặt vé
    #             self.load_ticket_history()
    #         else:
    #             messagebox.showerror("Lỗi", message)
    
    def format_datetime(self, dt_str):
        """
        Định dạng lại chuỗi datetime thành dạng dễ đọc
        """
        if not dt_str:
            return ""
        
        try:
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return dt_str
        
    def on_history_select(self, event):
        """
        Xử lý sự kiện chọn vé trong lịch sử
        """
        # Lấy item đang chọn
        selected_items = self.history_tree.selection()
        if not selected_items:
            # Không có item nào được chọn, vô hiệu hóa nút hủy vé
            self.cancel_button.config(state='disabled')
            return
        
        # Lấy thông tin vé
        item = self.history_tree.item(selected_items[0])
        ticket_id = item['values'][0]
        status = item['values'][6]  # Cột trạng thái
        
        # Chỉ cho phép hủy vé đã xác nhận
        if status == "Đã xác nhận":
            self.cancel_button.config(state='normal')
        else:
            self.cancel_button.config(state='disabled')

    def cancel_selected_ticket(self):
        """
        Hủy vé đã chọn
        """
        # Lấy item đang chọn
        selected_items = self.history_tree.selection()
        if not selected_items:
            messagebox.showerror("Lỗi", "Vui lòng chọn vé cần hủy!")
            return
        
        # Lấy thông tin vé
        item = self.history_tree.item(selected_items[0])
        ticket_id = item['values'][0]
        movie_name = item['values'][1]
        seats = item['values'][4]
        
        # Xác nhận hủy vé
        confirm_message = f"Bạn có chắc chắn muốn hủy vé?\n\n"
        confirm_message += f"Phim: {movie_name}\n"
        confirm_message += f"Ghế: {seats}\n"
        confirm_message += f"ID vé: {ticket_id}"
        
        if not messagebox.askyesno("Xác nhận hủy vé", confirm_message):
            return
        
        # Thực hiện hủy vé
        success, message = self.booking_controller.cancel_ticket(ticket_id, self.user.get('id', ''))
        
        if success:
            messagebox.showinfo("Thành công", message)
            # Tải lại lịch sử đặt vé
            self.load_ticket_history()
            # Vô hiệu hóa nút hủy vé
            self.cancel_button.config(state='disabled')
        else:
            messagebox.showerror("Lỗi", message)
