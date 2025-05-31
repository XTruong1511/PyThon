# views/schedule_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
from controllers.schedule_controller import ScheduleController
import uuid
from datetime import datetime, timedelta
from tkcalendar import DateEntry

class ScheduleManagementView(ttk.Frame):
    """
    Giao diện quản lý lịch chiếu
    """
    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.auth_controller = AuthController()
        self.auth_controller.current_user = user  # Đảm bảo current_user được đặt
        self.schedule_controller = ScheduleController()
        
        # Biến lưu trữ thông tin lịch chiếu đang chọn
        self.selected_schedule = None
        
        # Thiết lập giao diện
        self.setup_ui()
        
        # Load dữ liệu lịch chiếu
        self.load_schedules()
    
    def setup_ui(self):
        """
        Thiết lập các thành phần giao diện
        """
        # Frame chính chia làm 2 phần: danh sách và form chi tiết
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame danh sách lịch chiếu
        self.list_frame = ttk.LabelFrame(self.main_paned, text="Danh sách lịch chiếu")
        self.main_paned.add(self.list_frame, weight=3)
        
        # Frame chi tiết lịch chiếu
        self.detail_frame = ttk.LabelFrame(self.main_paned, text="Thông tin chi tiết")
        self.main_paned.add(self.detail_frame, weight=2)
        
        # Thiết lập frame danh sách
        self.setup_list_frame()
        
        # Thiết lập frame chi tiết
        self.setup_detail_frame()
    
    def setup_list_frame(self):
        """
        Thiết lập frame danh sách lịch chiếu
        """
        # Frame chứa công cụ
        tools_frame = ttk.Frame(self.list_frame)
        tools_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Ô tìm kiếm ngày
        ttk.Label(tools_frame, text="Chọn ngày:").pack(side=tk.LEFT, padx=5)
        self.date_filter = DateEntry(tools_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2)
        self.date_filter.pack(side=tk.LEFT, padx=5)
        
        # Nút tìm kiếm
        ttk.Button(tools_frame, text="Tìm kiếm", command=self.search_schedules).pack(side=tk.LEFT, padx=5)
        
        # Nút làm mới
        ttk.Button(tools_frame, text="Tất cả", command=self.load_schedules).pack(side=tk.LEFT, padx=5)
        
        # Nút thêm mới - Chỉ hiển thị cho admin và staff
        if self.auth_controller.check_permission("staff"):
            ttk.Button(tools_frame, text="Thêm mới", command=self.add_schedule).pack(side=tk.LEFT, padx=5)
        
        # Treeview hiển thị danh sách lịch chiếu
        columns = ('id', 'movie', 'theater', 'start_time', 'end_time', 'normal_price')
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show='headings')
        
        # Thiết lập các cột
        self.tree.heading('id', text='ID')
        self.tree.heading('movie', text='Phim')
        self.tree.heading('theater', text='Phòng chiếu')
        self.tree.heading('start_time', text='Thời gian bắt đầu')
        self.tree.heading('end_time', text='Thời gian kết thúc')
        self.tree.heading('normal_price', text='Giá vé thường (VND)')
        
        # Thiết lập độ rộng cột và căn chỉnh
        self.tree.column('id', width=80)
        self.tree.column('movie', width=150)
        self.tree.column('theater', width=100)
        self.tree.column('start_time', width=130, anchor=tk.CENTER)
        self.tree.column('end_time', width=130, anchor=tk.CENTER)
        self.tree.column('normal_price', width=120, anchor=tk.CENTER)
        
        # Thêm thanh cuộn
        scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bắt sự kiện chọn item
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
    
    def setup_detail_frame(self):
        """
        Thiết lập frame chi tiết lịch chiếu
        """
        # Frame chứa form nhập liệu
        form_frame = ttk.Frame(self.detail_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ID (readonly)
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.id_var, state="readonly", width=30).grid(row=0, column=1, pady=5)
        
        # Phim
        ttk.Label(form_frame, text="Phim:").grid(row=1, column=0, sticky="w", pady=5)
        self.movie_var = tk.StringVar()
        self.movie_combo = ttk.Combobox(form_frame, textvariable=self.movie_var, width=27, state="readonly")
        self.movie_combo.grid(row=1, column=1, pady=5)
        self.movie_combo.bind("<<ComboboxSelected>>", self.on_movie_selected)
        
        # Phòng chiếu
        ttk.Label(form_frame, text="Phòng chiếu:").grid(row=2, column=0, sticky="w", pady=5)
        self.theater_var = tk.StringVar()
        self.theater_combo = ttk.Combobox(form_frame, textvariable=self.theater_var, width=27, state="readonly")
        self.theater_combo.grid(row=2, column=1, pady=5)
        
        # Ngày chiếu
        ttk.Label(form_frame, text="Ngày chiếu:").grid(row=3, column=0, sticky="w", pady=5)
        self.date_entry = DateEntry(form_frame, width=28, background='darkblue',
                                   foreground='white', borderwidth=2)
        self.date_entry.grid(row=3, column=1, sticky="w", pady=5)
        
        # Thời gian bắt đầu
        ttk.Label(form_frame, text="Giờ bắt đầu:").grid(row=4, column=0, sticky="w", pady=5)
        time_frame = ttk.Frame(form_frame)
        time_frame.grid(row=4, column=1, sticky="w", pady=5)
        
        self.hour_var = tk.StringVar()
        hour_combo = ttk.Combobox(time_frame, textvariable=self.hour_var, width=5, state="readonly")
        hour_combo['values'] = [f"{i:02d}" for i in range(24)]
        hour_combo.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT)
        
        self.minute_var = tk.StringVar()
        minute_combo = ttk.Combobox(time_frame, textvariable=self.minute_var, width=5, state="readonly")
        minute_combo['values'] = ["00", "15", "30", "45"]
        minute_combo.pack(side=tk.LEFT)
        
        # Nút tính thời gian kết thúc
        ttk.Button(time_frame, text="Tính thời gian kết thúc", command=self.calculate_end_time).pack(side=tk.LEFT, padx=5)
        
        # Thời gian kết thúc
        ttk.Label(form_frame, text="Thời gian kết thúc:").grid(row=5, column=0, sticky="w", pady=5)
        self.end_time_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.end_time_var, width=30, state="readonly").grid(row=5, column=1, pady=5)
        
        # Giá vé thường
        ttk.Label(form_frame, text="Giá vé thường (VND):").grid(row=6, column=0, sticky="w", pady=5)
        self.normal_price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.normal_price_var, width=30).grid(row=6, column=1, pady=5)
        
        # Giá vé VIP
        ttk.Label(form_frame, text="Giá vé VIP (VND):").grid(row=7, column=0, sticky="w", pady=5)
        self.vip_price_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.vip_price_var, width=30).grid(row=7, column=1, pady=5)
        
        # Frame hiển thị thông tin phim
        movie_info_frame = ttk.LabelFrame(form_frame, text="Thông tin phim")
        movie_info_frame.grid(row=0, column=2, rowspan=8, padx=10, pady=5, sticky="nsew")
        
        self.movie_title_label = ttk.Label(movie_info_frame, text="")
        self.movie_title_label.pack(anchor="w", padx=5, pady=2)
        
        self.movie_duration_label = ttk.Label(movie_info_frame, text="")
        self.movie_duration_label.pack(anchor="w", padx=5, pady=2)
        
        self.movie_genre_label = ttk.Label(movie_info_frame, text="")
        self.movie_genre_label.pack(anchor="w", padx=5, pady=2)
        
        # Frame chứa các nút hành động
        button_frame = ttk.Frame(self.detail_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút Lưu - Chỉ hiển thị cho admin và staff
        if self.auth_controller.check_permission("staff"):
            ttk.Button(button_frame, text="Lưu", command=self.save_schedule).pack(side=tk.LEFT, padx=5)
        
        # Nút Xóa - Chỉ hiển thị cho admin
        if self.auth_controller.check_permission("admin"):
            ttk.Button(button_frame, text="Xóa", command=self.delete_schedule).pack(side=tk.LEFT, padx=5)
        
        # Nạp dữ liệu phim và phòng chiếu
        self.load_movies_and_theaters()
    
    def load_movies_and_theaters(self):
        """
        Nạp danh sách phim và phòng chiếu vào combobox
        """
        # Nạp danh sách phim
        movies = self.schedule_controller.get_all_movies()
        self.movies = {movie.get('id'): movie for movie in movies}
        self.movie_combo['values'] = [f"{movie.get('title')} ({movie.get('id')})" for movie in movies]
        
        # Nạp danh sách phòng chiếu
        theaters = self.schedule_controller.get_all_theaters()
        self.theaters = {theater.get('id'): theater for theater in theaters}
        self.theater_combo['values'] = [f"{theater.get('name')} - {theater.get('type')} ({theater.get('id')})" for theater in theaters]
    
    def load_schedules(self):
        """
        Tải danh sách lịch chiếu
        """
        # Xóa các dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Lấy danh sách lịch chiếu
        schedules = self.schedule_controller.get_all_schedules()
        
        # Thêm vào treeview
        for schedule in schedules:
            # Lấy thông tin phim và phòng chiếu
            movie = self.schedule_controller.get_movie_by_id(schedule.get('movie_id', ''))
            theater = self.schedule_controller.get_theater_by_id(schedule.get('theater_id', ''))
            
            movie_title = movie.get('title', 'N/A') if movie else 'N/A'
            theater_name = theater.get('name', 'N/A') if theater else 'N/A'
            
            # Format thời gian
            start_time = self.format_datetime(schedule.get('start_time', ''))
            end_time = self.format_datetime(schedule.get('end_time', ''))
            
            # Lấy giá vé
            price = schedule.get('price', {})
            normal_price = price.get('normal', 0)
            
            self.tree.insert('', tk.END, values=(
                schedule.get('id', ''),
                movie_title,
                theater_name,
                start_time,
                end_time,
                f"{normal_price:,}"
            ))
    
    def search_schedules(self):
        """
        Tìm kiếm lịch chiếu theo ngày
        """
        # Xóa các dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Lấy ngày đã chọn
        selected_date = self.date_filter.get_date().strftime("%Y-%m-%d")
        
        # Lấy danh sách lịch chiếu
        schedules = self.schedule_controller.get_all_schedules()
        
        # Lọc theo ngày và thêm vào treeview
        for schedule in schedules:
            # Lấy ngày từ thời gian bắt đầu
            start_time = schedule.get('start_time', '')
            if start_time.startswith(selected_date):
                # Lấy thông tin phim và phòng chiếu
                movie = self.schedule_controller.get_movie_by_id(schedule.get('movie_id', ''))
                theater = self.schedule_controller.get_theater_by_id(schedule.get('theater_id', ''))
                
                movie_title = movie.get('title', 'N/A') if movie else 'N/A'
                theater_name = theater.get('name', 'N/A') if theater else 'N/A'
                
                # Format thời gian
                start_time_fmt = self.format_datetime(start_time)
                end_time_fmt = self.format_datetime(schedule.get('end_time', ''))
                
                # Lấy giá vé
                price = schedule.get('price', {})
                normal_price = price.get('normal', 0)
                
                self.tree.insert('', tk.END, values=(
                    schedule.get('id', ''),
                    movie_title,
                    theater_name,
                    start_time_fmt,
                    end_time_fmt,
                    f"{normal_price:,}"
                ))
    
    def on_tree_select(self, event):
        """
        Xử lý sự kiện chọn lịch chiếu trong treeview
        """
        # Lấy item đang chọn
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Lấy ID lịch chiếu
        item = self.tree.item(selected_items[0])
        schedule_id = item['values'][0]
        
        # Lấy thông tin chi tiết lịch chiếu
        schedule = self.schedule_controller.get_schedule_by_id(schedule_id)
        if not schedule:
            return
        
        # Lưu lại lịch chiếu đang chọn
        self.selected_schedule = schedule
        
        # Hiển thị thông tin lên form
        self.id_var.set(schedule.get('id', ''))
        
        # Hiển thị phim đã chọn
        movie_id = schedule.get('movie_id', '')
        movie = self.schedule_controller.get_movie_by_id(movie_id)
        if movie:
            movie_index = self.find_combo_index(self.movie_combo, movie_id)
            if movie_index >= 0:
                self.movie_combo.current(movie_index)
            self.show_movie_info(movie)
        
        # Hiển thị phòng chiếu đã chọn
        theater_id = schedule.get('theater_id', '')
        theater_index = self.find_combo_index(self.theater_combo, theater_id)
        if theater_index >= 0:
            self.theater_combo.current(theater_index)
        
        # Hiển thị thời gian
        start_time = schedule.get('start_time', '')
        end_time = schedule.get('end_time', '')
        
        if start_time:
            try:
                dt = datetime.fromisoformat(start_time)
                self.date_entry.set_date(dt.date())
                self.hour_var.set(f"{dt.hour:02d}")
                self.minute_var.set(f"{dt.minute:02d}")
            except:
                pass
        
        self.end_time_var.set(self.format_time(end_time))
        
        # Hiển thị giá vé
        price = schedule.get('price', {})
        self.normal_price_var.set(price.get('normal', 0))
        self.vip_price_var.set(price.get('vip', 0))
    
    def find_combo_index(self, combo, id_to_find):
        """
        Tìm vị trí của item trong combobox dựa vào ID
        """
        values = combo['values']
        for i, value in enumerate(values):
            if f"({id_to_find})" in value:
                return i
        return -1
    
    def get_id_from_combo(self, combo_text):
        """
        Lấy ID từ text của combobox
        """
        import re
        match = re.search(r'\((.*?)\)$', combo_text)
        if match:
            return match.group(1)
        return None
    
    def on_movie_selected(self, event):
        """
        Xử lý sự kiện chọn phim
        """
        # Lấy ID phim
        movie_id = self.get_id_from_combo(self.movie_var.get())
        if not movie_id:
            return
        
        # Lấy thông tin phim
        movie = self.schedule_controller.get_movie_by_id(movie_id)
        if not movie:
            return
        
        # Hiển thị thông tin phim
        self.show_movie_info(movie)
        
        # Tính thời gian kết thúc
        self.calculate_end_time()
    
    def show_movie_info(self, movie):
        """
        Hiển thị thông tin phim
        """
        self.movie_title_label.config(text=f"Phim: {movie.get('title', '')}")
        self.movie_duration_label.config(text=f"Thời lượng: {movie.get('duration', 0)} phút")
        self.movie_genre_label.config(text=f"Thể loại: {', '.join(movie.get('genre', []))}")
    
    def calculate_end_time(self):
        """
        Tính thời gian kết thúc dựa trên thời gian bắt đầu và thời lượng phim
        """
        # Lấy thời gian bắt đầu
        try:
            selected_date = self.date_entry.get_date()
            hour = int(self.hour_var.get() or 0)
            minute = int(self.minute_var.get() or 0)
            
            start_time = datetime(
                selected_date.year,
                selected_date.month,
                selected_date.day,
                hour,
                minute
            )
            
            # Lấy ID phim
            movie_id = self.get_id_from_combo(self.movie_var.get())
            if not movie_id:
                return
            
            # Lấy thông tin phim
            movie = self.schedule_controller.get_movie_by_id(movie_id)
            if not movie:
                return
            
            # Lấy thời lượng phim
            duration = movie.get('duration', 0)
            
            # Tính thời gian kết thúc
            end_time = start_time + timedelta(minutes=duration)
            self.end_time_var.set(end_time.strftime("%H:%M"))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tính thời gian kết thúc: {str(e)}")
    
    def add_schedule(self):
        """
        Thêm mới lịch chiếu
        """
        # Kiểm tra quyền
        if not self.auth_controller.check_permission("staff"):
            messagebox.showerror("Lỗi", "Bạn không có quyền thực hiện chức năng này!")
            return
        
        # Xóa chọn hiện tại
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        
        # Xóa dữ liệu cũ trên form
        self.selected_schedule = None
        self.id_var.set(f"schedule_{uuid.uuid4().hex[:8]}")
        self.movie_combo.set("")
        self.theater_combo.set("")
        self.hour_var.set("18")  # Mặc định 18:00
        self.minute_var.set("00")
        self.end_time_var.set("")
        self.normal_price_var.set("90000")  # Mặc định 90,000 VND
        self.vip_price_var.set("120000")    # Mặc định 120,000 VND
        
        # Ngày mặc định là hôm nay
        self.date_entry.set_date(datetime.now())
        
        # Xóa thông tin phim
        self.movie_title_label.config(text="")
        self.movie_duration_label.config(text="")
        self.movie_genre_label.config(text="")
    
    def save_schedule(self):
        """
        Lưu thông tin lịch chiếu
        """
        # Kiểm tra quyền
        if not self.auth_controller.check_permission("staff"):
            messagebox.showerror("Lỗi", "Bạn không có quyền thực hiện chức năng này!")
            return
        
        # Lấy thông tin từ form
        schedule_id = self.id_var.get()
        movie_id = self.get_id_from_combo(self.movie_var.get())
        theater_id = self.get_id_from_combo(self.theater_var.get())
        
        # Kiểm tra các trường bắt buộc
        if not movie_id:
            messagebox.showerror("Lỗi", "Vui lòng chọn phim!")
            return
        
        if not theater_id:
            messagebox.showerror("Lỗi", "Vui lòng chọn phòng chiếu!")
            return
        
        # Lấy thời gian bắt đầu
        try:
            selected_date = self.date_entry.get_date()
            hour = int(self.hour_var.get() or 0)
            minute = int(self.minute_var.get() or 0)
            
            start_time = datetime(
                selected_date.year,
                selected_date.month,
                selected_date.day,
                hour,
                minute
            ).isoformat()
        except:
            messagebox.showerror("Lỗi", "Thời gian bắt đầu không hợp lệ!")
            return
        
        # Lấy thời gian kết thúc từ end_time_var
        end_time_str = self.end_time_var.get()
        if not end_time_str:
            messagebox.showerror("Lỗi", "Vui lòng tính thời gian kết thúc!")
            return
        
        try:
            # Chuyển thành datetime
            end_hour, end_minute = map(int, end_time_str.split(":"))
            end_time = datetime(
                selected_date.year,
                selected_date.month,
                selected_date.day,
                end_hour,
                end_minute
            )
            
            # Nếu thời gian kết thúc < thời gian bắt đầu, tăng thêm 1 ngày
            if end_time < datetime.fromisoformat(start_time):
                end_time = end_time + timedelta(days=1)
                
            end_time = end_time.isoformat()
        except:
            messagebox.showerror("Lỗi", "Thời gian kết thúc không hợp lệ!")
            return
        
        # Kiểm tra giá vé
        try:
            normal_price = int(self.normal_price_var.get() or 0)
            vip_price = int(self.vip_price_var.get() or 0)
            
            if normal_price <= 0:
                messagebox.showerror("Lỗi", "Giá vé thường phải lớn hơn 0!")
                return
            
            if vip_price <= 0:
                messagebox.showerror("Lỗi", "Giá vé VIP phải lớn hơn 0!")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Giá vé phải là số nguyên!")
            return
        
        # Kiểm tra trùng lịch
        is_overlap, overlap_schedule = self.schedule_controller.check_schedule_overlap(
            theater_id, start_time, end_time,
            schedule_id if self.selected_schedule else None
        )
        
        if is_overlap:
            # Lấy thông tin phim trùng lịch
            overlap_movie = self.schedule_controller.get_movie_by_id(overlap_schedule.get('movie_id', ''))
            overlap_movie_title = overlap_movie.get('title', 'N/A') if overlap_movie else 'N/A'
            
            # Format thời gian
            overlap_start = self.format_datetime(overlap_schedule.get('start_time', ''))
            overlap_end = self.format_datetime(overlap_schedule.get('end_time', ''))
            
            error_message = f"Lịch chiếu bị trùng với:\n"
            error_message += f"- Phim: {overlap_movie_title}\n"
            error_message += f"- Thời gian: {overlap_start} - {overlap_end}"
            
            messagebox.showerror("Lỗi", error_message)
            return
        
        # Tạo đối tượng lịch chiếu mới
        schedule = {
            "id": schedule_id,
            "movie_id": movie_id,
            "theater_id": theater_id,
            "start_time": start_time,
            "end_time": end_time,
            "price": {
                "normal": normal_price,
                "vip": vip_price
            }
        }
        
        # Lưu lịch chiếu
        success = False
        if self.selected_schedule:
            # Cập nhật lịch chiếu
            success = self.schedule_controller.update_schedule(schedule)
            message = "Cập nhật lịch chiếu thành công!"
        else:
            # Thêm lịch chiếu mới
            success = self.schedule_controller.add_schedule(schedule)
            message = "Thêm lịch chiếu mới thành công!"
        
        if success:
            messagebox.showinfo("Thành công", message)
            # Tải lại danh sách lịch chiếu
            self.load_schedules()
            # Lưu lại lịch chiếu hiện tại
            self.selected_schedule = schedule
        else:
            messagebox.showerror("Lỗi", "Có lỗi xảy ra khi lưu thông tin lịch chiếu!")
    
    def delete_schedule(self):
        """
        Xóa lịch chiếu
        """
        # Kiểm tra quyền
        if not self.auth_controller.check_permission("admin"):
            messagebox.showerror("Lỗi", "Bạn không có quyền thực hiện chức năng này!")
            return
        
        # Kiểm tra lịch chiếu đang chọn
        if not self.selected_schedule:
            messagebox.showerror("Lỗi", "Vui lòng chọn lịch chiếu cần xóa!")
            return
        
        # Xác nhận xóa
        movie = self.schedule_controller.get_movie_by_id(self.selected_schedule.get('movie_id', ''))
        movie_title = movie.get('title', 'N/A') if movie else 'N/A'
        
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa lịch chiếu phim '{movie_title}'?"):
            return
        
        # Xóa lịch chiếu
        success = self.schedule_controller.delete_schedule(self.selected_schedule.get('id'))
        
        if success:
            messagebox.showinfo("Thành công", "Xóa lịch chiếu thành công!")
            # Tải lại danh sách lịch chiếu
            self.load_schedules()
            # Vô hiệu hóa form
            self.clear_form()
            # Xóa lịch chiếu đang chọn
            self.selected_schedule = None
        else:
            messagebox.showerror("Lỗi", "Có lỗi xảy ra khi xóa lịch chiếu!")
    
    def clear_form(self):
        """
        Xóa dữ liệu trên form
        """
        self.id_var.set("")
        self.movie_combo.set("")
        self.theater_combo.set("")
        self.date_entry.set_date(datetime.now())
        self.hour_var.set("")
        self.minute_var.set("")
        self.end_time_var.set("")
        self.normal_price_var.set("")
        self.vip_price_var.set("")
        
        # Xóa thông tin phim
        self.movie_title_label.config(text="")
        self.movie_duration_label.config(text="")
        self.movie_genre_label.config(text="")
    
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
    
    def format_time(self, dt_str):
        """
        Định dạng lại chuỗi datetime thành dạng giờ:phút
        """
        if not dt_str:
            return ""
        
        try:
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime("%H:%M")
        except:
            return dt_str
