# 🧰 HƯỚNG DẪN CÀI ĐẶT MÔI TRƯỜNG DỰ ÁN DJANGO (BTL_PYTHON)

## 📦 1. Yêu cầu hệ thống

Trước khi chạy dự án, hãy đảm bảo máy bạn có:

* **Python 3.10 – 3.13** (khuyên dùng Python 3.12+)
* **Git** để clone repo
* **VS Code** hoặc IDE tương đương
* **Trình duyệt web (Chrome, Edge, …)**

---

## 🚀 2. Clone dự án về máy

```bash
git clone https://github.com/BuiHongHa/BTL_PYTHON.git
cd BTL_PYTHON/BTL_PYTHON-main/Webquanly/library_system
```

---

## 🧱 3. Tạo môi trường ảo (virtual environment)

Tạo môi trường ảo để tách biệt các thư viện:

### Trên **Windows**:

```bash
python -m venv venv
```

Kích hoạt:

```bash
.\venv\Scripts\Activate.ps1
```

(Nếu bị lỗi quyền, chạy PowerShell bằng quyền Admin và gõ:

```bash
Set-ExecutionPolicy Unrestricted
```

rồi xác nhận bằng **Y**)

### Trên **Linux/Mac**:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 📚 4. Cài đặt các thư viện cần thiết

```bash
pip install -r requirements.txt
```

Nếu chưa có file `requirements.txt`, chạy lệnh dưới để tạo:

```bash
pip install django djangorestframework openpyxl pillow
pip freeze > requirements.txt
```

---

## ⚙️ 5. Cấu hình cơ sở dữ liệu

Dự án dùng **SQLite3** (tích hợp sẵn trong Django).
Nếu bạn dùng CSDL khác (MySQL, PostgreSQL), sửa file:

```
library_system/settings.py
```

trong phần `DATABASES`.

---

## 🧩 6. Chạy migration (tạo bảng trong database)

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 👤 7. Tạo tài khoản quản trị viên (Admin)

```bash
python manage.py createsuperuser
```

Nhập:

* Tên đăng nhập
* Email
* Mật khẩu

---

## 💻 8. Chạy dự án

```bash
python manage.py runserver
```

Truy cập tại:
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📈 9. Các chức năng chính

* Đăng nhập / Đăng ký người dùng
* Mượn – Trả sách
* Quản lý người mượn
* Xuất file Excel (thống kê, danh sách mượn trả, sách, phạt, …)
* Chức năng thống kê theo tháng, lọc thời gian
* Quên mật khẩu (gửi email reset)

---

## 📬 10. Gửi mail (tùy chọn)

Nếu dùng tính năng **quên mật khẩu**, cập nhật cấu hình mail trong:

```
library_system/settings.py
```

Ví dụ (dùng Gmail):

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your_email@gmail.com"
EMAIL_HOST_PASSWORD = "your_app_password"
```

> ⚠️ Không dùng mật khẩu thật, hãy tạo **App Password** trong phần bảo mật Gmail.

---

## ✅ 11. Kiểm tra lại

Nếu server chạy ổn, bạn sẽ thấy dòng:

```
Django version X.X.X, using settings 'library_system.settings'
Starting development server at http://127.0.0.1:8000/
```

---

## 📁 12. Cấu trúc thư mục

```
library_system/
│
├── accounts/         → Đăng nhập, đăng ký, reset mật khẩu
├── borrower/         → Trang người mượn
├── manager/          → Trang quản lý, thống kê, xuất Excel
├── static/           → CSS, JS, ảnh tĩnh
├── templates/        → HTML giao diện
├── venv/             → Môi trường ảo (tự tạo, không commit)
└── manage.py         → File chạy chính
```

---

## 💡 Lỗi thường gặp

| Lỗi                                                     | Cách khắc phục                                   |
| ------------------------------------------------------- | ------------------------------------------------ |
| `mvn not recognized`                                    | Cài Java Maven (nếu cần build phần khác)         |
| `ModuleNotFoundError: No module named 'rest_framework'` | `pip install djangorestframework`                |
| `Invalid character / in sheet title`                    | Sửa tên sheet không chứa `/`                     |
| `Excel does not support timezones`                      | Dùng `.replace(tzinfo=None)` khi export datetime |

---


