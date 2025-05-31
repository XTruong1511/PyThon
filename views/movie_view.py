# views/movie_view.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from controllers.auth_controller import AuthController
from controllers.movie_controller import MovieController
import uuid
from PIL import Image, ImageTk
from io import BytesIO
import requests

class MovieManagementView(ttk.Frame):
    """
    Giao diện quản lý phim
    """
    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.auth_controller = AuthController()
        self.auth_controller.current_user = user
        self.movie_controller = MovieController()
        
        # Biến lưu trữ thông tin phim đang chọn
        self.selected_movie = None
        
        # Thiết lập giao diện
        self.setup_ui()
        
        # Load dữ liệu phim
        self.load_movies()
    
    def setup_ui(self):
        """
        Thiết lập các thành phần giao diện
        """
        # Frame chính chia làm 2 phần: danh sách và form chi tiết
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame danh sách phim
        self.list_frame = ttk.LabelFrame(self.main_paned, text="Danh sách phim")
        self.main_paned.add(self.list_frame, weight=3)
        
        # Frame chi tiết phim
        self.detail_frame = ttk.LabelFrame(self.main_paned, text="Thông tin chi tiết")
        self.main_paned.add(self.detail_frame, weight=2)
        
        # Thiết lập frame danh sách
        self.setup_list_frame()
        
        # Thiết lập frame chi tiết
        self.setup_detail_frame()
    
    def setup_list_frame(self):
        """
        Thiết lập frame danh sách phim
        """
        # Frame chứa công cụ
        tools_frame = ttk.Frame(self.list_frame)
        tools_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Ô tìm kiếm
        ttk.Label(tools_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.search_movies())
        ttk.Entry(tools_frame, textvariable=self.search_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # Nút làm mới
        ttk.Button(tools_frame, text="Làm mới", command=self.load_movies).pack(side=tk.LEFT, padx=5)
        
        # Nút thêm mới - Chỉ hiển thị cho admin và staff
        if self.auth_controller.check_permission("staff"):
            ttk.Button(tools_frame, text="Thêm mới", command=self.add_movie).pack(side=tk.LEFT, padx=5)
        
        # Nút import từ API - Chỉ hiển thị cho admin và staff
        if self.auth_controller.check_permission("staff"):
            ttk.Button(tools_frame, text="Import từ API", command=self.import_from_api).pack(side=tk.LEFT, padx=5)
        
        # Treeview hiển thị danh sách phim
        columns = ('id', 'title', 'director', 'duration', 'rating')
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show='headings')
        
        # Thiết lập các cột
        self.tree.heading('id', text='ID')
        self.tree.heading('title', text='Tên phim')
        self.tree.heading('director', text='Đạo diễn')
        self.tree.heading('duration', text='Thời lượng (phút)')
        self.tree.heading('rating', text='Đánh giá')
        
        # Thiết lập độ rộng cột và căn chỉnh
        self.tree.column('id', width=80)
        self.tree.column('title', width=200)
        self.tree.column('director', width=150)
        self.tree.column('duration', width=100, anchor=tk.CENTER)
        self.tree.column('rating', width=80, anchor=tk.CENTER)
        
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
        Thiết lập frame chi tiết phim
        """
        # Frame chứa form nhập liệu
        form_frame = ttk.Frame(self.detail_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ID (readonly)
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.id_var, state="readonly", width=30).grid(row=0, column=1, pady=5)
        
        # Tên phim
        ttk.Label(form_frame, text="Tên phim:").grid(row=1, column=0, sticky="w", pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.title_var, width=30).grid(row=1, column=1, pady=5)
        
        # Đạo diễn
        ttk.Label(form_frame, text="Đạo diễn:").grid(row=2, column=0, sticky="w", pady=5)
        self.director_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.director_var, width=30).grid(row=2, column=1, pady=5)
        
        # Thời lượng
        ttk.Label(form_frame, text="Thời lượng (phút):").grid(row=3, column=0, sticky="w", pady=5)
        self.duration_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.duration_var, width=30).grid(row=3, column=1, pady=5)
        
        # Thể loại
        ttk.Label(form_frame, text="Thể loại:").grid(row=4, column=0, sticky="w", pady=5)
        self.genre_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.genre_var, width=30).grid(row=4, column=1, pady=5)
        
        # Ngày phát hành
        ttk.Label(form_frame, text="Ngày phát hành:").grid(row=5, column=0, sticky="w", pady=5)
        self.release_date_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.release_date_var, width=30).grid(row=5, column=1, pady=5)
        
        # Đánh giá
        ttk.Label(form_frame, text="Đánh giá:").grid(row=6, column=0, sticky="w", pady=5)
        self.rating_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.rating_var, width=30).grid(row=6, column=1, pady=5)
        
        # Poster URL
        ttk.Label(form_frame, text="URL Poster:").grid(row=7, column=0, sticky="w", pady=5)
        self.poster_url_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.poster_url_var, width=30).grid(row=7, column=1, pady=5)
        
        # Trailer URL
        ttk.Label(form_frame, text="URL Trailer:").grid(row=8, column=0, sticky="w", pady=5)
        self.trailer_url_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.trailer_url_var, width=30).grid(row=8, column=1, pady=5)
        
        # Mô tả
        ttk.Label(form_frame, text="Mô tả:").grid(row=9, column=0, sticky="nw", pady=5)
        self.description_text = tk.Text(form_frame, width=30, height=5)
        self.description_text.grid(row=9, column=1, pady=5)
        
        # Frame để hiển thị poster
        poster_frame = ttk.LabelFrame(form_frame, text="Poster phim")
        poster_frame.grid(row=0, column=2, rowspan=10, padx=10, pady=5, sticky="nsew")
        
        # Label hiển thị poster
        self.poster_label = ttk.Label(poster_frame, text="Không có ảnh")
        self.poster_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame chứa các nút hành động
        button_frame = ttk.Frame(self.detail_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Nút Lưu - Chỉ hiển thị cho admin và staff
        if self.auth_controller.check_permission("staff"):
            ttk.Button(button_frame, text="Lưu", command=self.save_movie).pack(side=tk.LEFT, padx=5)
        
        # Nút Xóa - Chỉ hiển thị cho admin
        if self.auth_controller.check_permission("admin"):
            ttk.Button(button_frame, text="Xóa", command=self.delete_movie).pack(side=tk.LEFT, padx=5)
        
        # Vô hiệu hóa form ban đầu
        self.disable_form()
    
    def load_movies(self):
        """
        Tải danh sách phim
        """
        # Xóa các dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Lấy danh sách phim
        movies = self.movie_controller.get_all_movies()
        
        # Thêm vào treeview
        for movie in movies:
            self.tree.insert('', tk.END, values=(
                movie.get('id', ''),
                movie.get('title', ''),
                movie.get('director', ''),
                movie.get('duration', 0),
                movie.get('rating', 0)
            ))
    
    def search_movies(self):
        """
        Tìm kiếm phim
        """
        search_term = self.search_var.get().lower()
        
        # Xóa các dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Lấy danh sách phim
        movies = self.movie_controller.get_all_movies()
        
        # Lọc và thêm vào treeview
        for movie in movies:
            if (search_term in movie.get('title', '').lower() or 
                search_term in movie.get('director', '').lower()):
                self.tree.insert('', tk.END, values=(
                    movie.get('id', ''),
                    movie.get('title', ''),
                    movie.get('director', ''),
                    movie.get('duration', 0),
                    movie.get('rating', 0)
                ))
    
    def on_tree_select(self, event):
        """
        Xử lý sự kiện chọn phim trong treeview
        """
        # Lấy item đang chọn
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Lấy ID phim
        item = self.tree.item(selected_items[0])
        movie_id = item['values'][0]
        
        # Lấy thông tin chi tiết phim
        movie = self.movie_controller.get_movie_by_id(movie_id)
        if not movie:
            return
        
        # Lưu lại phim đang chọn
        self.selected_movie = movie
        
        # Hiển thị thông tin lên form
        self.id_var.set(movie.get('id', ''))
        self.title_var.set(movie.get('title', ''))
        self.director_var.set(movie.get('director', ''))
        self.duration_var.set(movie.get('duration', ''))
        self.genre_var.set(', '.join(movie.get('genre', [])))
        self.release_date_var.set(movie.get('release_date', ''))
        self.rating_var.set(movie.get('rating', ''))
        self.poster_url_var.set(movie.get('poster_url', ''))
        self.trailer_url_var.set(movie.get('trailer_url', ''))
        
        # Xóa nội dung mô tả cũ
        self.description_text.delete(1.0, tk.END)
        
        # Thêm nội dung mô tả mới
        self.description_text.insert(tk.END, movie.get('description', ''))
        
        # Hiển thị poster nếu có
        self.load_poster(movie.get('poster_url', ''))
        
        # Kích hoạt form
        self.enable_form()
    
    def load_poster(self, url):
        """
        Tải và hiển thị poster phim
        """
        # Xóa ảnh cũ
        self.poster_label.config(text="Đang tải ảnh...")
        self.poster_label.image = None
        
        if not url:
            self.poster_label.config(text="Không có ảnh")
            return
        
        try:
            # Tải ảnh từ URL
            response = requests.get(url)
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            
            # Resize ảnh để vừa với kích thước hiển thị
            image = image.resize((150, 200), Image.LANCZOS)
            
            # Chuyển đổi thành PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Hiển thị ảnh
            self.poster_label.config(image=photo, text="")
            
            # Lưu lại reference để tránh bị thu hồi bởi garbage collector
            self.poster_label.image = photo
        except Exception as e:
            self.poster_label.config(text=f"Lỗi tải ảnh: {str(e)}")
    
    def enable_form(self):
        """
        Kích hoạt form nhập liệu
        """
        if self.auth_controller.check_permission("staff"):
            state = "normal"
        else:
            state = "disabled"
        
        widgets = [
            self.title_var, self.director_var, self.duration_var, 
            self.genre_var, self.release_date_var, self.rating_var,
            self.poster_url_var, self.trailer_url_var
        ]
        
        for widget in widgets:
            widget._entry.config(state=state)
        
        self.description_text.config(state=state)
    
    def disable_form(self):
        """
        Vô hiệu hóa form nhập liệu
        """
        widgets = [
            self.id_var, self.title_var, self.director_var, self.duration_var, 
            self.genre_var, self.release_date_var, self.rating_var,
            self.poster_url_var, self.trailer_url_var
        ]
        
        for widget in widgets:
            if hasattr(widget, '_entry'):
                widget._entry.config(state="disabled")
        
        self.description_text.config(state="disabled")
        
        # Xóa ảnh poster
        self.poster_label.config(text="Không có ảnh", image=None)
        self.poster_label.image = None
    
    def add_movie(self):
        """
        Thêm mới phim
        """
        # Kiểm tra quyền
        if not self.auth_controller.check_permission("staff"):
            messagebox.showerror("Lỗi", "Bạn không có quyền thực hiện chức năng này!")
            return
        
        # Xóa chọn hiện tại
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        
        # Xóa dữ liệu cũ trên form
        self.selected_movie = None
        self.id_var.set(f"movie_{uuid.uuid4().hex[:8]}")
        self.title_var.set("")
        self.director_var.set("")
        self.duration_var.set("")
        self.genre_var.set("")
        self.release_date_var.set("")
        self.rating_var.set("")
        self.poster_url_var.set("")
        self.trailer_url_var.set("")
        self.description_text.delete(1.0, tk.END)
        
        # Xóa ảnh poster
        self.poster_label.config(text="Không có ảnh", image=None)
        self.poster_label.image = None
        
        # Kích hoạt form
        self.enable_form()
    
    def save_movie(self):
        """
        Lưu thông tin phim
        """
        # Kiểm tra quyền
        if not self.auth_controller.check_permission("staff"):
            messagebox.showerror("Lỗi", "Bạn không có quyền thực hiện chức năng này!")
            return
        
        # Lấy thông tin từ form
        movie_id = self.id_var.get()
        title = self.title_var.get()
        director = self.director_var.get()
        
        # Kiểm tra các trường bắt buộc
        if not title:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên phim!")
            return
        
        try:
            duration = int(self.duration_var.get()) if self.duration_var.get() else 0
        except ValueError:
            messagebox.showerror("Lỗi", "Thời lượng phải là số nguyên!")
            return
        
        try:
            rating = float(self.rating_var.get()) if self.rating_var.get() else 0
        except ValueError:
            messagebox.showerror("Lỗi", "Đánh giá phải là số thực!")
            return
        
        # Xử lý thể loại (chuyển từ chuỗi thành list)
        genre_text = self.genre_var.get()
        genre = [g.strip() for g in genre_text.split(',')] if genre_text else []
        
        # Tạo đối tượng phim mới
        movie = {
            "id": movie_id,
            "title": title,
            "director": director,
            "duration": duration,
            "genre": genre,
            "release_date": self.release_date_var.get(),
            "rating": rating,
            "poster_url": self.poster_url_var.get(),
            "trailer_url": self.trailer_url_var.get(),
            "description": self.description_text.get(1.0, tk.END).strip()
        }
        
        # Lưu phim
        success = False
        if self.selected_movie:
            # Cập nhật phim
            success = self.movie_controller.update_movie(movie)
            message = "Cập nhật phim thành công!"
        else:
            # Thêm phim mới
            success = self.movie_controller.add_movie(movie)
            message = "Thêm phim mới thành công!"
        
        if success:
            messagebox.showinfo("Thành công", message)
            # Tải lại danh sách phim
            self.load_movies()
        else:
            messagebox.showerror("Lỗi", "Có lỗi xảy ra khi lưu thông tin phim!")
    
    def delete_movie(self):
        """
        Xóa phim (có kiểm tra ràng buộc)
        """
        # Kiểm tra quyền
        if not self.auth_controller.check_permission("admin"):
            messagebox.showerror("Lỗi", "Bạn không có quyền thực hiện chức năng này!")
            return
        
        # Kiểm tra phim đang chọn
        if not self.selected_movie:
            messagebox.showerror("Lỗi", "Vui lòng chọn phim cần xóa!")
            return
        
        movie_title = self.selected_movie.get('title', '')
        movie_id = self.selected_movie.get('id', '')
        
        # Xác nhận xóa
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa phim '{movie_title}'?"):
            return
        
        # Thực hiện xóa phim với kiểm tra ràng buộc
        success, movie_schedules = self.movie_controller.delete_movie(movie_id)
        
        if success:
            messagebox.showinfo("Thành công", "Xóa phim thành công!")
            # Tải lại danh sách phim
            self.load_movies()
            # Vô hiệu hóa form
            self.disable_form()
            # Xóa phim đang chọn
            self.selected_movie = None
        elif movie_schedules is not None:
            # Phim đang được sử dụng trong lịch chiếu
            self.show_schedule_conflict_dialog(movie_title, movie_schedules)
        else:
            messagebox.showerror("Lỗi", "Có lỗi xảy ra khi xóa phim!")

    
    def import_from_api(self):
        """
        Import phim từ API
        """
        # Kiểm tra quyền
        if not self.auth_controller.check_permission("staff"):
            messagebox.showerror("Lỗi", "Bạn không có quyền thực hiện chức năng này!")
            return
        
        # Hỏi số lượng phim cần import
        from tkinter.simpledialog import askinteger
        num_movies = askinteger("Import phim", "Nhập số lượng phim cần import:", minvalue=1, maxvalue=20)
        
        if not num_movies:
            return
        
        # Thực hiện import
        success = self.movie_controller.import_from_api(num_movies)
        
        if success:
            messagebox.showinfo("Thành công", f"Đã import {num_movies} phim từ API!")
            # Tải lại danh sách phim
            self.load_movies()
        else:
            messagebox.showerror("Lỗi", "Có lỗi xảy ra khi import phim từ API!")
            
    def show_schedule_conflict_dialog(self, movie_title, movie_schedules):
        """
        Hiển thị dialog chi tiết về xung đột lịch chiếu
        """
        # Tạo cửa sổ dialog
        conflict_dialog = tk.Toplevel(self)
        conflict_dialog.title("Không thể xóa phim")
        conflict_dialog.geometry("600x400")
        conflict_dialog.resizable(False, False)
        conflict_dialog.transient(self)
        conflict_dialog.grab_set()
        
        # Căn giữa cửa sổ
        conflict_dialog.geometry("+%d+%d" % (
            conflict_dialog.winfo_screenwidth() // 2 - 300,
            conflict_dialog.winfo_screenheight() // 2 - 200
        ))
        
        # Frame chính
        main_frame = ttk.Frame(conflict_dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề lỗi
        error_label = ttk.Label(main_frame, text=f"❌ KHÔNG THỂ XÓA PHIM", font=("Arial", 14, "bold"),foreground="red")
        error_label.pack(pady=(0, 10))
        
        # Thông báo chi tiết
        message_label = ttk.Label(main_frame, text=f"Phim '{movie_title}' đang được sử dụng trong các lịch chiếu sau:",font=("Arial", 11))
        message_label.pack(pady=(0, 15))
        
        # Frame chứa danh sách lịch chiếu
        list_frame = ttk.LabelFrame(main_frame, text="Lịch chiếu đang sử dụng phim này")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview hiển thị lịch chiếu xung đột
        columns = ('schedule_id', 'theater', 'start_time', 'end_time')
        conflict_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # Thiết lập các cột
        conflict_tree.heading('schedule_id', text='ID Lịch chiếu')
        conflict_tree.heading('theater', text='Phòng chiếu')
        conflict_tree.heading('start_time', text='Thời gian bắt đầu')
        conflict_tree.heading('end_time', text='Thời gian kết thúc')
        
        # Thiết lập độ rộng cột
        conflict_tree.column('schedule_id', width=100)
        conflict_tree.column('theater', width=120)
        conflict_tree.column('start_time', width=150)
        conflict_tree.column('end_time', width=150)
        
        # Thêm thanh cuộn
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=conflict_tree.yview)
        conflict_tree.configure(yscrollcommand=scrollbar.set)
        
        # Đặt vị trí
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        conflict_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Thêm dữ liệu vào treeview
        for schedule in movie_schedules:
            # Lấy thông tin phòng chiếu
            theater_id = schedule.get('theater_id', '')
            theater = None
            try:
                from controllers.schedule_controller import ScheduleController
                schedule_controller = ScheduleController()
                theater = schedule_controller.get_theater_by_id(theater_id)
            except:
                pass
            
            theater_name = theater.get('name', 'N/A') if theater else 'N/A'
            
            # Format thời gian
            start_time = self.format_datetime(schedule.get('start_time', ''))
            end_time = self.format_datetime(schedule.get('end_time', ''))
            
            conflict_tree.insert('', tk.END, values=(
                schedule.get('id', ''),
                theater_name,
                start_time,
                end_time
            ))
        
        # Thông báo hướng dẫn
        guide_label = ttk.Label(main_frame, text="💡 Để xóa phim này, bạn cần xóa tất cả lịch chiếu liên quan trước.",font=("Arial", 10),foreground="blue")
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
                messagebox.showinfo("Hướng dẫn", "Vui lòng chuyển sang tab 'Quản lý lịch chiếu' để xóa các lịch chiếu liên quan.")
            
            schedule_button = ttk.Button(button_frame, text="Quản lý lịch chiếu", command=go_to_schedule)
            schedule_button.pack(side=tk.RIGHT, padx=5)

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
    