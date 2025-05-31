# views/theater_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from controllers.auth_controller import AuthController
from controllers.theater_controller import TheaterController
import uuid

class TheaterManagementView(ttk.Frame):
    """
    Giao diện quản lý phòng chiếu
    """
    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.auth_controller = AuthController()
        self.auth_controller.current_user = user
        self.theater_controller = TheaterController()
        
        
        # Biến lưu trữ thông tin phòng chiếu đang chọn
        self.selected_theater = None
        
        # Thiết lập giao diện
        self.setup_ui()
        
        # Load dữ liệu phòng chiếu
        self.load_theaters()
    
    def setup_ui(self):
        """
        Thiết lập các thành phần giao diện
        """
        # Frame chính chia làm 2 phần: danh sách và form chi tiết
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame danh sách phòng chiếu
        self.list_frame = ttk.LabelFrame(self.main_paned, text="Danh sách phòng chiếu")
        self.main_paned.add(self.list_frame, weight=3)
        
        # Frame chi tiết phòng chiếu
        self.detail_frame = ttk.LabelFrame(self.main_paned, text="Thông tin chi tiết")
        self.main_paned.add(self.detail_frame, weight=2)
        
        # Thiết lập frame danh sách
        self.setup_list_frame()
        
        # Thiết lập frame chi tiết
        self.setup_detail_frame()
    
    def setup_list_frame(self):
        """
        Thiết lập frame danh sách phòng chiếu
        """
        # Frame chứa công cụ
        tools_frame = ttk.Frame(self.list_frame)
        tools_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Ô tìm kiếm
        ttk.Label(tools_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.search_theaters())
        ttk.Entry(tools_frame, textvariable=self.search_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # Nút làm mới
        ttk.Button(tools_frame, text="Làm mới", command=self.load_theaters).pack(side=tk.LEFT, padx=5)
        
        # Nút thêm mới - Chỉ hiển thị cho admin và staff
        if self.auth_controller.check_permission("staff"):
            ttk.Button(tools_frame, text="Thêm mới", command=self.add_theater).pack(side=tk.LEFT, padx=5)
        
        # Treeview hiển thị danh sách phòng chiếu
        columns = ('id', 'name', 'type', 'capacity')
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show='headings')
        
        # Thiết lập các cột
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Tên phòng')
        self.tree.heading('type', text='Loại phòng')
        self.tree.heading('capacity', text='Sức chứa')
        
        # Thiết lập độ rộng cột và căn chỉnh
        self.tree.column('id', width=80)
        self.tree.column('name', width=150)
        self.tree.column('type', width=100)
        self.tree.column('capacity', width=80, anchor=tk.CENTER)
        
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
        Thiết lập frame chi tiết phòng chiếu
        """
        # Frame chứa form nhập liệu
        form_frame = ttk.Frame(self.detail_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ID (readonly)
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.id_var, state="readonly", width=30).grid(row=0, column=1, pady=5)
        
        # Tên phòng
        ttk.Label(form_frame, text="Tên phòng:").grid(row=1, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var, width=30).grid(row=1, column=1, pady=5)
        
        # Loại phòng
        ttk.Label(form_frame, text="Loại phòng:").grid(row=2, column=0, sticky="w", pady=5)
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(form_frame, textvariable=self.type_var, width=27)
        type_combo.grid(row=2, column=1, pady=5)
        type_combo['values'] = self.theater_controller.get_theater_types()
        
        # Sức chứa
        ttk.Label(form_frame, text="Sức chứa:").grid(row=3, column=0, sticky="w", pady=5)
        self.capacity_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.capacity_var, width=30).grid(row=3, column=1, pady=5)
        
        # Layout - Số hàng
        ttk.Label(form_frame, text="Số hàng:").grid(row=4, column=0, sticky="w", pady=5)
        self.rows_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.rows_var, width=30).grid(row=4, column=1, pady=5)
        
        # Layout - Số cột
        ttk.Label(form_frame, text="Số cột:").grid(row=5, column=0, sticky="w", pady=5)
        self.cols_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.cols_var, width=30).grid(row=5, column=1, pady=5)
        
        # Frame hiển thị sơ đồ ghế
        self.seat_frame = ttk.LabelFrame(form_frame, text="Sơ đồ ghế")
        self.seat_frame.grid(row=0, column=2, rowspan=6, padx=10, pady=5, sticky="nsew")
        
        # Canvas hiển thị sơ đồ ghế
        self.seat_canvas = tk.Canvas(self.seat_frame, width=300, height=200, bg="white")
        self.seat_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame chứa các nút hành động
        button_frame = ttk.Frame(self.detail_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút Lưu - Chỉ hiển thị cho admin và staff
        if self.auth_controller.check_permission("staff"):
            ttk.Button(button_frame, text="Lưu", command=self.save_theater).pack(side=tk.LEFT, padx=5)
        
        # Nút Xóa - Chỉ hiển thị cho admin
        if self.auth_controller.check_permission("admin"):
            ttk.Button(button_frame, text="Xóa", command=self.delete_theater).pack(side=tk.LEFT, padx=5)
        
        # Nút Cập nhật sơ đồ - Cho tất cả người dùng
        ttk.Button(button_frame, text="Cập nhật sơ đồ", command=self.update_seat_map).pack(side=tk.LEFT, padx=5)
        
        # Vô hiệu hóa form ban đầu
        self.disable_form()
    
    def load_theaters(self):
        """
        Tải danh sách phòng chiếu
        """
        # Xóa các dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Lấy danh sách phòng chiếu
        theaters = self.theater_controller.get_all_theaters()
        
        # Thêm vào treeview
        for theater in theaters:
            self.tree.insert('', tk.END, values=(
                theater.get('id', ''),
                theater.get('name', ''),
                theater.get('type', ''),
                theater.get('capacity', 0)
            ))
    
    def search_theaters(self):
        """
        Tìm kiếm phòng chiếu
        """
        search_term = self.search_var.get().lower()
        
        # Xóa các dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Lấy danh sách phòng chiếu
        theaters = self.theater_controller.get_all_theaters()
        
        # Lọc và thêm vào treeview
        for theater in theaters:
            if (search_term in theater.get('name', '').lower() or 
                search_term in theater.get('type', '').lower()):
                self.tree.insert('', tk.END, values=(
                    theater.get('id', ''),
                    theater.get('name', ''),
                    theater.get('type', ''),
                    theater.get('capacity', 0)
                ))
    
    def on_tree_select(self, event):
        """
        Xử lý sự kiện chọn phòng chiếu trong treeview
        """
        # Lấy item đang chọn
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Lấy ID phòng chiếu
        item = self.tree.item(selected_items[0])
        theater_id = item['values'][0]
        
        # Lấy thông tin chi tiết phòng chiếu
        theater = self.theater_controller.get_theater_by_id(theater_id)
        if not theater:
            return
        
        # Lưu lại phòng chiếu đang chọn
        self.selected_theater = theater
        
        # Hiển thị thông tin lên form
        self.id_var.set(theater.get('id', ''))
        self.name_var.set(theater.get('name', ''))
        self.type_var.set(theater.get('type', ''))
        self.capacity_var.set(theater.get('capacity', ''))
        
        # Lấy thông tin layout
        layout = theater.get('layout', {'rows': 0, 'cols': 0})
        self.rows_var.set(layout.get('rows', 0))
        self.cols_var.set(layout.get('cols', 0))
        
        # Hiển thị sơ đồ ghế
        self.draw_seat_map()
        
        # Kích hoạt form
        self.enable_form()
    
    def draw_seat_map(self):
        """
        Vẽ sơ đồ ghế
        """
        # Xóa nội dung canvas cũ
        self.seat_canvas.delete("all")
        
        if not self.selected_theater:
            return
        
        # Lấy thông tin layout
        layout = self.selected_theater.get('layout', {'rows': 0, 'cols': 0})
        rows = layout.get('rows', 0)
        cols = layout.get('cols', 0)
        
        if rows <= 0 or cols <= 0:
            self.seat_canvas.create_text(150, 100, text="Chưa thiết lập sơ đồ ghế", fill="gray")
            return
        
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
                
                # ĐỔI LOGIC GHẼ VIP: 2 hàng cuối thay vì 2 hàng đầu
                if row >= rows - 2:  # 2 hàng cuối là ghế VIP
                    fill_color = "gold"  # Ghế VIP
                else:
                    fill_color = "lightblue"  # Ghế thường
                
                # Vẽ ghế
                self.seat_canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="blue")
                
                # Vẽ nhãn ghế
                self.seat_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=seat_label, font=("Arial", 8))
        
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
    
    def update_seat_map(self):
        """
        Cập nhật sơ đồ ghế dựa trên thông tin nhập vào
        """
        try:
            rows = int(self.rows_var.get())
            cols = int(self.cols_var.get())
            
            if rows <= 0 or cols <= 0:
                messagebox.showerror("Lỗi", "Số hàng và số cột phải lớn hơn 0!")
                return
            
            # Cập nhật thông tin layout
            if self.selected_theater:
                self.selected_theater['layout'] = {
                    'rows': rows,
                    'cols': cols
                }
                
                # Cập nhật sức chứa
                self.capacity_var.set(rows * cols)
                
                # Vẽ lại sơ đồ ghế
                self.draw_seat_map()
            else:
                messagebox.showerror("Lỗi", "Vui lòng chọn phòng chiếu hoặc tạo mới trước!")
        except ValueError:
            messagebox.showerror("Lỗi", "Số hàng và số cột phải là số nguyên!")
    
    def enable_form(self):
        """
        Kích hoạt form nhập liệu
        """
        if self.auth_controller.check_permission("staff"):
            state = "normal"
        else:
            state = "disabled"
        
        widgets = [
            self.name_var, self.type_var, self.capacity_var, 
            self.rows_var, self.cols_var
        ]
        
        for widget in widgets:
            widget._entry.config(state=state)
    
    def disable_form(self):
        """
        Vô hiệu hóa form nhập liệu
        """
        # Reset tất cả các trường
        self.id_var.set("")
        self.name_var.set("")
        self.type_var.set("")
        self.capacity_var.set("")
        self.rows_var.set("")
        self.cols_var.set("")
        
        # Xóa sơ đồ ghế
        self.seat_canvas.delete("all")
        
        # Đặt lại selected_theater
        self.selected_theater = None
    
    def add_theater(self):
        """
        Thêm mới phòng chiếu
        """
        # Kiểm tra quyền
        if not self.auth_controller.check_permission("staff"):
            messagebox.showerror("Lỗi", "Bạn không có quyền thực hiện chức năng này!")
            return
        
        # Xóa chọn hiện tại
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        
        # Xóa dữ liệu cũ trên form
        self.selected_theater = None
        self.id_var.set(f"room_{uuid.uuid4().hex[:8]}")
        self.name_var.set("")
        self.type_var.set("")
        self.capacity_var.set("")
        self.rows_var.set("")
        self.cols_var.set("")
        
        # Xóa sơ đồ ghế
        self.seat_canvas.delete("all")
        
        # Kích hoạt form
        self.enable_form()
    
    def save_theater(self):
        """
        Lưu thông tin phòng chiếu
        """
        # Kiểm tra quyền
        if not self.auth_controller.check_permission("staff"):
            messagebox.showerror("Lỗi", "Bạn không có quyền thực hiện chức năng này!")
            return
        
        # Lấy thông tin từ form
        theater_id = self.id_var.get()
        name = self.name_var.get()
        type = self.type_var.get()
        
        # Kiểm tra các trường bắt buộc
        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên phòng chiếu!")
            return
        
        if not type:
            messagebox.showerror("Lỗi", "Vui lòng chọn loại phòng chiếu!")
            return
        
        try:
            capacity = int(self.capacity_var.get()) if self.capacity_var.get() else 0
        except ValueError:
            messagebox.showerror("Lỗi", "Sức chứa phải là số nguyên!")
            return
        
        try:
            rows = int(self.rows_var.get()) if self.rows_var.get() else 0
            cols = int(self.cols_var.get()) if self.cols_var.get() else 0
        except ValueError:
            messagebox.showerror("Lỗi", "Số hàng và số cột phải là số nguyên!")
            return
        
        # Tạo đối tượng phòng chiếu mới
        theater = {
            "id": theater_id,
            "name": name,
            "type": type,
            "capacity": capacity,
            "layout": {
                "rows": rows,
                "cols": cols
            }
        }
        
        # Lưu phòng chiếu
        success = False
        if self.selected_theater:
            # Cập nhật phòng chiếu
            success = self.theater_controller.update_theater(theater)
            message = "Cập nhật phòng chiếu thành công!"
        else:
            # Thêm phòng chiếu mới
            success = self.theater_controller.add_theater(theater)
            message = "Thêm phòng chiếu mới thành công!"
        
        if success:
            messagebox.showinfo("Thành công", message)
            # Tải lại danh sách phòng chiếu
            self.load_theaters()
            # Lưu lại phòng chiếu hiện tại
            self.selected_theater = theater
            # Vẽ lại sơ đồ ghế
            self.draw_seat_map()
        else:
            messagebox.showerror("Lỗi", "Có lỗi xảy ra khi lưu thông tin phòng chiếu!")
    
    def delete_theater(self):
        """
        Xóa phòng chiếu (có kiểm tra ràng buộc)
        """
        # Kiểm tra quyền
        if not self.auth_controller.check_permission("admin"):
            messagebox.showerror("Lỗi", "Bạn không có quyền thực hiện chức năng này!")
            return
        
        # Kiểm tra phòng chiếu đang chọn
        if not self.selected_theater:
            messagebox.showerror("Lỗi", "Vui lòng chọn phòng chiếu cần xóa!")
            return
        
        theater_name = self.selected_theater.get('name', '')
        theater_id = self.selected_theater.get('id', '')
        
        # Xác nhận xóa
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa phòng chiếu '{theater_name}'?"):
            return
        
        # Thực hiện xóa phòng chiếu với kiểm tra ràng buộc
        success, theater_schedules = self.theater_controller.delete_theater(theater_id)
        
        if success:
            messagebox.showinfo("Thành công", "Xóa phòng chiếu thành công!")
            # Tải lại danh sách phòng chiếu
            self.load_theaters()
            # Vô hiệu hóa form
            self.disable_form()
            # Xóa phòng chiếu đang chọn
            self.selected_theater = None
        elif theater_schedules is not None:
            # Phòng chiếu đang được sử dụng trong lịch chiếu
            self.show_schedule_conflict_dialog(theater_name, theater_schedules)
        else:
            messagebox.showerror("Lỗi", "Có lỗi xảy ra khi xóa phòng chiếu!")
            
    def show_schedule_conflict_dialog(self, theater_name, theater_schedules):
        """
        Hiển thị dialog chi tiết về xung đột lịch chiếu
        """
        # Tạo cửa sổ dialog
        conflict_dialog = tk.Toplevel(self)
        conflict_dialog.title("Không thể xóa phòng chiếu")
        conflict_dialog.geometry("650x450")
        conflict_dialog.resizable(False, False)
        conflict_dialog.transient(self)
        conflict_dialog.grab_set()
        
        # Căn giữa cửa sổ
        conflict_dialog.geometry("+%d+%d" % (
            conflict_dialog.winfo_screenwidth() // 2 - 325,
            conflict_dialog.winfo_screenheight() // 2 - 225
        ))
        
        # Frame chính
        main_frame = ttk.Frame(conflict_dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề lỗi
        error_label = ttk.Label(main_frame, 
                            text=f"❌ KHÔNG THỂ XÓA PHÒNG CHIẾU", 
                            font=("Arial", 14, "bold"),
                            foreground="red")
        error_label.pack(pady=(0, 10))
        
        # Thông báo chi tiết
        message_label = ttk.Label(main_frame, 
                                text=f"Phòng chiếu '{theater_name}' đang được sử dụng trong các lịch chiếu sau:",
                                font=("Arial", 11))
        message_label.pack(pady=(0, 15))
        
        # Frame chứa danh sách lịch chiếu
        list_frame = ttk.LabelFrame(main_frame, text="Lịch chiếu đang sử dụng phòng chiếu này")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview hiển thị lịch chiếu xung đột
        columns = ('schedule_id', 'movie', 'start_time', 'end_time', 'price')
        conflict_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # Thiết lập các cột
        conflict_tree.heading('schedule_id', text='ID Lịch chiếu')
        conflict_tree.heading('movie', text='Phim')
        conflict_tree.heading('start_time', text='Thời gian bắt đầu')
        conflict_tree.heading('end_time', text='Thời gian kết thúc')
        conflict_tree.heading('price', text='Giá vé (VND)')
        
        # Thiết lập độ rộng cột
        conflict_tree.column('schedule_id', width=100)
        conflict_tree.column('movie', width=150)
        conflict_tree.column('start_time', width=130)
        conflict_tree.column('end_time', width=130)
        conflict_tree.column('price', width=100)
        
        # Thêm thanh cuộn
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=conflict_tree.yview)
        conflict_tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        conflict_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thêm dữ liệu vào treeview
        for schedule in theater_schedules:
            # Lấy thông tin phim
            movie_id = schedule.get('movie_id', '')
            movie = None
            try:
                from controllers.schedule_controller import ScheduleController
                schedule_controller = ScheduleController()
                movie = schedule_controller.get_movie_by_id(movie_id)
            except:
                pass
            
            movie_title = movie.get('title', 'N/A') if movie else 'N/A'
            
            # Format thời gian
            start_time = self.format_datetime(schedule.get('start_time', ''))
            end_time = self.format_datetime(schedule.get('end_time', ''))
            
            # Lấy giá vé
            price = schedule.get('price', {})
            normal_price = price.get('normal', 0)
            
            conflict_tree.insert('', tk.END, values=(
                schedule.get('id', ''),
                movie_title,
                start_time,
                end_time,
                f"{normal_price:,}"
            ))
        
        # Thống kê
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_label = ttk.Label(stats_frame, 
                            text=f"📊 Tổng cộng: {len(theater_schedules)} lịch chiếu đang sử dụng phòng này",
                            font=("Arial", 10, "bold"),
                            foreground="darkblue")
        stats_label.pack()
        
        # Thông báo hướng dẫn
        guide_label = ttk.Label(main_frame, 
                            text="💡 Để xóa phòng chiếu này, bạn cần xóa tất cả lịch chiếu liên quan hoặc chuyển chúng sang phòng khác trước.",
                            font=("Arial", 10),
                            foreground="blue",
                            wraplength=600)
        guide_label.pack(pady=(0, 15))
        
        # Frame chứa nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Nút Đóng
        close_button = ttk.Button(button_frame, text="Đóng", command=conflict_dialog.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)
        
        # Nút "Đi tới Quản lý lịch chiếu" (tùy chọn)
        if self.auth_controller.check_permission("staff"):
            def go_to_schedule():
                conflict_dialog.destroy()
                # Trigger chuyển đến tab quản lý lịch chiếu
                messagebox.showinfo("Hướng dẫn", "Vui lòng chuyển sang tab 'Quản lý lịch chiếu' để xóa các lịch chiếu liên quan hoặc chuyển chúng sang phòng khác.")
            
            schedule_button = ttk.Button(button_frame, text="Quản lý lịch chiếu", command=go_to_schedule)
            schedule_button.pack(side=tk.RIGHT, padx=5)
        
        # Nút "Xem chi tiết phòng"
        def show_theater_details():
            details_text = f"""THÔNG TIN CHI TIẾT PHÒNG CHIẾU:

    🏛️ Tên phòng: {theater_name}
    🎭 Loại phòng: {self.selected_theater.get('type', 'N/A')}
    💺 Sức chứa: {self.selected_theater.get('capacity', 'N/A')} ghế
    📐 Sơ đồ: {self.selected_theater.get('layout', {}).get('rows', 0)} hàng x {self.selected_theater.get('layout', {}).get('cols', 0)} cột
    📅 Số lịch chiếu: {len(theater_schedules)}
            """
            messagebox.showinfo("Chi tiết phòng chiếu", details_text)
        
        details_button = ttk.Button(button_frame, text="Chi tiết phòng", command=show_theater_details)
        details_button.pack(side=tk.RIGHT, padx=5)

    def format_datetime(self, dt_str):
        """
        Định dạng lại chuỗi datetime thành dạng dễ đọc
        """
        if not dt_str:
            return ""
        
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return dt_str
