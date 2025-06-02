# DoAn_Python

Đây là dự án Python được phát triển theo mô hình MVC (Model-View-Controller).

## Cấu trúc thư mục

```
DoAn_Python/
├── controllers/     # Chứa các controller
├── models/         # Chứa các model
├── views/          # Chứa các view
├── utils/          # Chứa các tiện ích
├── data/           # Chứa dữ liệu
└── main.py         # File chính của ứng dụng
```

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/XTruong1511/Python.git
```

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python main.py
```

## Đóng gói ứng dụng

Để tạo file thực thi (.exe):
```bash
pyinstaller DoAn_Python.spec
```

File thực thi sẽ được tạo trong thư mục `dist/`. 
