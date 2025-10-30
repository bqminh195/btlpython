from django.urls import path
from . import views

app_name = "manager"

urlpatterns = [
    # 🏠 Trang chủ quản lý (quản lý sách)
    path("home/", views.manager_home, name="manager_home"),

    # 📚 CRUD sách
    path("books/add/", views.add_book, name="add_book"),
    path("books/edit/<int:book_id>/", views.edit_book, name="edit_book"),
    path("books/delete/<int:book_id>/", views.delete_book, name="delete_book"),

    # 📖 Quản lý mượn sách
    path("borrow/", views.manage_loans, name="manage_loans"),
    path("borrow/return/<int:loan_id>/", views.mark_returned, name="mark_returned"),

    # ⚠️ Quản lý phạt
    path("penalty/", views.manage_penalties, name="manage_penalties"),
    path("penalty/clear/<int:penalty_id>/", views.clear_penalty, name="clear_penalty"),
    path("check-requests/", views.manage_check_requests, name="manage_check_requests"),

    # 🕒 Quản lý yêu cầu check-in / check-out
    path("check-requests/", views.manage_check_requests, name="manage_check_requests"),
    path("check-requests/approve/<int:req_id>/", views.approve_check_request, name="approve_check_request"),
    path("check-requests/reject/<int:req_id>/", views.reject_check_request, name="reject_check_request"),

    # 📊 Trang thống kê
    path("statistics/", views.statistics_view, name="statistics"),
    path("export/<str:export_type>/", views.export_excel, name="export_excel"),
    path('loans/edit/<int:loan_id>/', views.edit_loan_dates, name='edit_loan_dates'),

    path('home/', views.manager_home, name='home'),
    path('profile/', views.manager_profile, name='profile'),  # 🆕 Hồ sơ quản lý
    path('reset-password/', views.ManagerPasswordResetView.as_view(), name='reset_password'),

]
