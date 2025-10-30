from django.urls import path
from . import views
from django.contrib.auth import views as auth_views   # 👈 nếu bạn có phần reset password bên dưới

app_name = "borrower"

urlpatterns = [
    path('home/', views.borrower_home, name='borrower_home'),
    path("search/", views.search, name="search"),
    path("register/", views.register, name="register"),
    path('home/', views.borrower_home, name='home'),
    path("profile/", views.profile_view, name="profile"),
    path("my-loans/", views.my_loans, name="my_loans"),
    path("return/<int:loan_id>/", views.return_book, name="return_book"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path("profile/change-password/", views.change_password, name="change_password"),
    path('borrow/confirm/<int:book_id>/', views.confirm_borrow, name='confirm_borrow'),
    path("penalties/", views.my_penalties, name="my_penalties"),
    path("check-requests/", views.check_request_view, name="check_requests"),
    path("check-requests/delete/<int:request_id>/", views.delete_check_request, name="delete_check_request"),
]

# =================== QUÊN MẬT KHẨU ===================
urlpatterns += [
    path("password-reset/", views.CustomPasswordResetView.as_view(), name="password_reset"),
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
