from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from borrower import views as borrower_views
from manager import views as manager_views
from library_system import views
from django.conf import settings
from django.conf.urls.static import static

# Trang chủ tạm
def home(request):
    return HttpResponse("""
        <h1>📚 Hệ thống Quản lý Thư viện</h1>
        <p>Vui lòng <a href='/accounts/login/'>đăng nhập</a> để tiếp tục.</p>
    """)

urlpatterns = [
    # Trang quản trị
    path("admin/", admin.site.urls),

    # Trang chủ
    path("", views.home_page, name="home"),

    # 🔐 Đăng nhập / Đăng xuất
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login"
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(template_name="registration/logout.html"),
        name="logout"
    ),

    # 🔰 Đăng ký người dùng
    path("register/", borrower_views.register, name="register"),

    # Ứng dụng con
    path("borrower/", include("borrower.urls")),
    path("manager/", include("manager.urls")),
    path("api/", include("api.urls")),

    # Trang chuyển hướng sau đăng nhập
    path("redirect/", manager_views.redirect_view, name="redirect_view"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# =================== QUÊN MẬT KHẨU ===================
from django.contrib.auth import views as auth_views

urlpatterns += [
    path("password-reset/", 
         auth_views.PasswordResetView.as_view(
             template_name="borrower/password_reset.html"
         ), 
         name="password_reset"),

    path("password-reset/done/", 
         auth_views.PasswordResetDoneView.as_view(
             template_name="borrower/password_reset_done.html"
         ), 
         name="password_reset_done"),

    path("reset/<uidb64>/<token>/", 
         auth_views.PasswordResetConfirmView.as_view(
             template_name="borrower/password_reset_confirm.html"
         ), 
         name="password_reset_confirm"),

    path("reset/done/", 
         auth_views.PasswordResetCompleteView.as_view(
             template_name="borrower/password_reset_complete.html"
         ), 
         name="password_reset_complete"),
]
