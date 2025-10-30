from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from .models import Book, Penalty, CheckRequest
from .forms import BookForm
from borrower.models import Loan
from django.http import HttpResponse
from .models import Penalty
from django.utils.encoding import smart_str
from io import BytesIO
from django.conf import settings

from datetime import datetime, timedelta, timezone as dt_timezone
from django.db.models import Count
from openpyxl import Workbook
from django.utils.timezone import now
from datetime import timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ManagerProfile
from .forms import ManagerProfileForm
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.db.models import Q
# ===========================================================
# 🧩 Decorator: chỉ cho phép nhân viên quản lý (is_staff)
# ===========================================================
def staff_required(view_func):
    return user_passes_test(
        lambda u: u.is_staff,
        login_url='/accounts/login/'
    )(view_func)

@staff_required
def statistics_view(request):
    # Lấy dữ liệu lọc tháng - năm từ form
    start_month = request.GET.get("start_month")
    end_month = request.GET.get("end_month")

    today = timezone.now()
    if not start_month:
        start_month = today.strftime("%Y-%m")
    if not end_month:
        end_month = today.strftime("%Y-%m")

    # Chuyển chuỗi yyyy-mm sang datetime
    start_date = datetime.strptime(start_month, "%Y-%m").replace(day=1, tzinfo=dt_timezone.utc)
    end_year, end_m = map(int, end_month.split("-"))
    end_date = datetime(end_year, end_m, 1, tzinfo=dt_timezone.utc) + timedelta(days=32)
    end_date = end_date.replace(day=1)

    # ==== Thống kê trong khoảng thời gian ====
    books_added = Book.objects.filter(created_at__gte=start_date, created_at__lt=end_date).count()
    loans_in_range = Loan.objects.filter(borrowed_at__gte=start_date, borrowed_at__lt=end_date)
    loans_returned = loans_in_range.filter(returned=True).count()
    loans_borrowed = loans_in_range.count()
    top_book = loans_in_range.values("book__title").annotate(total=Count("book")).order_by("-total").first()
    top_book_title = top_book["book__title"] if top_book else "Chưa có dữ liệu"
    penalties_unpaid = Penalty.objects.filter(cleared=False).count()

    context = {
        "books_added": books_added,
        "loans_borrowed": loans_borrowed,
        "loans_returned": loans_returned,
        "top_book_title": top_book_title,
        "penalties_unpaid": penalties_unpaid,
        "start_month": start_month,
        "end_month": end_month,
    }
    return render(request, "manager/statistics.html", context)


@staff_required
def export_excel(request, export_type):
    from openpyxl import Workbook
    from datetime import datetime

    wb = Workbook()
    ws = wb.active
    ws.title = "Danh sách"

    # Lọc theo khoảng thời gian nếu có
    start_month = request.GET.get("start_month")
    end_month = request.GET.get("end_month")
    start_date = None
    end_date = None

    if start_month and end_month:
        start_date = datetime.strptime(start_month, "%Y-%m")
        end_year, end_m = map(int, end_month.split("-"))
        end_date = datetime(end_year, end_m, 1) + timedelta(days=32)
        end_date = end_date.replace(day=1)

    # === Các loại dữ liệu xuất ===
    if export_type == "books":
        ws.append(["STT", "Tên sách", "Tác giả", "Thể loại", "Năm XB", "Số lượng"])
        books = Book.objects.all()
        if start_date and end_date:
            books = books.filter(created_at__gte=start_date, created_at__lt=end_date)
        for i, b in enumerate(books, start=1):
            ws.append([i, b.title, b.author, b.category, b.year, b.total_copies])


    elif export_type == "loans":
        ws.append(["Người mượn", "Sách", "Ngày mượn", "Hạn trả", "Đã trả"])
        loans = Loan.objects.select_related("user", "book")
        if start_date and end_date:
            loans = loans.filter(borrowed_at__gte=start_date, borrowed_at__lt=end_date)
        for l in loans:
            ws.append([
                l.user.username,
                l.book.title,
                l.borrowed_at.replace(tzinfo=None) if l.borrowed_at else "",
                l.due_date.replace(tzinfo=None) if l.due_date else "",
                "✅" if l.returned else "❌",
            ])

    elif export_type == "penalties":
        ws.append(["Người dùng", "Lý do", "Số tiền", "Đã thanh toán"])
        penalties = Penalty.objects.select_related("user")
        if start_date and end_date:
            penalties = penalties.filter(created_at__gte=start_date, created_at__lt=end_date)
        for p in penalties:
            ws.append([p.user.username, p.reason, p.amount, "✅" if p.cleared else "❌"])

    # Trả file về người dùng
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{export_type}_{start_month}_to_{end_month}.xlsx"'
    wb.save(response)
    return response




# ===========================================================
# 🏠 TRANG CHỦ QUẢN LÝ SÁCH
# ===========================================================
@staff_required
def manager_home(request):
    print("🗂️ Đang dùng database:", settings.DATABASES['default']['NAME'])
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    year = request.GET.get('year', '')

    books = Book.objects.all().order_by('-created_at')

    if query:
        books = books.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if category:
        books = books.filter(category__icontains=category)
    if year:
        books = books.filter(year=year)   # ✅ SỬA: bỏ icontains, dùng so sánh chính xác


    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Book.objects.values_list('category', flat=True).distinct().order_by('category')
    years = Book.objects.values_list('year', flat=True).distinct().order_by('-year')

    return render(request, 'manager/home.html', {
        'books': page_obj,
        'page_obj': page_obj,
        'query': query,
        'category': category,
        'year': year,
        'categories': categories,
        'years': years,
        'total_books': Book.objects.count(),
    })


# ===========================================================
# 📚 CRUD SÁCH
# ===========================================================
@staff_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Thêm sách thành công!")
            return redirect('manager:manager_home')
    else:
        form = BookForm()
    return render(request, 'manager/add_book.html', {'form': form})


@staff_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Cập nhật sách thành công!")
            return redirect('manager:manager_home')
    else:
        form = BookForm(instance=book)
    return render(request, 'manager/edit_book.html', {'form': form, 'book': book})


@staff_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    book.delete()
    messages.success(request, f"🗑️ Đã xóa sách '{book.title}' thành công.")
    return redirect('manager:manager_home')


# ===========================================================
# 📖 QUẢN LÝ PHIẾU MƯỢN
# ===========================================================
@staff_required
def manage_loans(request):
    loans = Loan.objects.select_related('user', 'book').order_by('-borrowed_at')
    query = request.GET.get('q', '')
    filter_status = request.GET.get('status', '')

    if query:
        loans = loans.filter(user__username__icontains=query) | loans.filter(book__title__icontains=query)

    if filter_status == 'overdue':
        loans = loans.filter(returned=False, due_date__lt=timezone.now())
    elif filter_status == 'ontime':
        loans = loans.filter(returned=False, due_date__gte=timezone.now())

    paginator = Paginator(loans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manager/manage_loans.html', {
        'loans': page_obj,
        'page_obj': page_obj,
        'now': timezone.now(),
        'query': query,
        'filter_status': filter_status,
    })


@staff_required
def mark_returned(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    if not loan.returned:
        loan.returned = True
        loan.returned_at = timezone.now()
        loan.book.available_copies += 1
        loan.book.save()
        loan.save()
        messages.success(request, f"✅ Đã đánh dấu '{loan.book.title}' là đã trả.")
    else:
        messages.info(request, f"ℹ️ Sách '{loan.book.title}' đã được trả trước đó.")
    return redirect('manager:manage_loans')


# ===========================================================
# 💰 QUẢN LÝ PHIẾU PHẠT
# ===========================================================
@staff_required
def manage_penalties(request):
    overdue_loans = Loan.objects.filter(returned=False, due_date__lt=timezone.now())
    for loan in overdue_loans:
        loan.create_penalty_if_overdue()

    penalties = Penalty.objects.all().order_by('-created_at')
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    if search:
        penalties = penalties.filter(user__username__icontains=search)
    if status == 'paid':
        penalties = penalties.filter(cleared=True)
    elif status == 'unpaid':
        penalties = penalties.filter(cleared=False)

    paginator = Paginator(penalties, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search': search,
        'status': status,
        'total_penalties': penalties.count(),
        'unpaid_count': penalties.filter(cleared=False).count(),
        'paid_count': penalties.filter(cleared=True).count(),
    }
    return render(request, 'manager/manage_penalties.html', context)


@staff_required
def clear_penalty(request, penalty_id):
    penalty = get_object_or_404(Penalty, id=penalty_id)
    penalty.cleared = True
    penalty.save()
    messages.success(request, f"💸 Đã xác nhận {penalty.user.username} đã thanh toán xong.")
    return redirect('manager:manage_penalties')


# ===========================================================
# 🧾 QUẢN LÝ YÊU CẦU CHECK-IN / CHECK-OUT
# ===========================================================
@staff_required
def manage_check_requests(request):
    """Hiển thị danh sách các yêu cầu check-in / check-out của người mượn"""    
    requests_list = CheckRequest.objects.select_related("user").order_by('-created_at')


    # Bộ lọc
    filter_type = request.GET.get('type', '')
    status = request.GET.get('status', '')

    if filter_type:
        requests_list = requests_list.filter(check_type=filter_type)
    if status == 'approved':
        requests_list = requests_list.filter(approved=True)
    elif status == 'rejected':
        requests_list = requests_list.filter(rejected=True)
    elif status == 'pending':
        requests_list = requests_list.filter(approved=False, rejected=False)

    paginator = Paginator(requests_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'manager/manage_check_requests.html', {
        'requests': requests_list
    })


@staff_required
def approve_check_request(request, req_id):
    req = get_object_or_404(CheckRequest, id=req_id)
    req.approved = True
    req.rejected = False
    req.manager_note = "✅ Đã duyệt bởi quản lý."
    req.save()
    messages.success(request, f"✔ Đã duyệt yêu cầu {req.user.username} ({req.get_check_type_display()}).")
    return redirect('manager:manage_check_requests')


@staff_required
def reject_check_request(request, req_id):
    req = get_object_or_404(CheckRequest, id=req_id)
    req.approved = False
    req.rejected = True
    req.manager_note = "❌ Bị từ chối bởi quản lý."
    req.save()
    messages.warning(request, f"❌ Đã từ chối yêu cầu {req.user.username} ({req.get_check_type_display()}).")
    return redirect('manager:manage_check_requests')


# ===========================================================
# 🚀 CHUYỂN HƯỚNG SAU ĐĂNG NHẬP
# ===========================================================
@login_required
def redirect_view(request):
    if request.user.is_staff:
        return redirect('manager:manager_home')
    else:
        return redirect('borrower:borrower_home')

        # Cập nhật ngày mượn và hạn trả cho phiếu mượn
@staff_required
def edit_loan_dates(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)

    if request.method == 'POST':
        borrowed_at = request.POST.get('borrowed_at')
        due_date = request.POST.get('due_date')

        if borrowed_at and due_date:
            from django.utils.dateparse import parse_datetime
            loan.borrowed_at = parse_datetime(borrowed_at)
            loan.due_date = parse_datetime(due_date)
            loan.save()
            messages.success(request, f"🕒 Đã cập nhật ngày mượn và hạn trả cho '{loan.book.title}'.")
            return redirect('manager:manage_loans')
        else:
            messages.error(request, "⚠️ Dữ liệu không hợp lệ.")
    
    return render(request, 'manager/edit_loan.html', {'loan': loan})

# ==========================================
# 👤 HỒ SƠ QUẢN LÝ (CẬP NHẬT VÀ CẤP LẠI MẬT KHẨU)
# ==========================================
@staff_required
def manager_profile(request):
    # Lấy hoặc tạo hồ sơ quản lý tương ứng với user hiện tại
    profile, created = ManagerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ManagerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Cập nhật hồ sơ quản lý thành công!")
            return redirect('manager:profile')
    else:
        form = ManagerProfileForm(instance=profile)

    return render(request, 'manager/profile.html', {
        'user': request.user,
        'form': form
    })


# ==========================================
# 🔑 GỬI EMAIL CẤP LẠI MẬT KHẨU (QUÊN MK)
# ==========================================
class ManagerPasswordResetView(PasswordResetView):
    template_name = 'manager/reset_password.html'
    success_url = reverse_lazy('login')
    email_template_name = 'manager/reset_email.html'