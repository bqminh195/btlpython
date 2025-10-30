from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.utils import timezone
from .forms import UserUpdateForm, UserProfileForm, CustomPasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from manager.models import Book, Penalty, CheckRequest
from borrower.models import Loan, UserProfile
from .forms import CheckRequestForm
from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.core.exceptions import ObjectDoesNotExist
# ======================================================
#QUÊN MẬT KHẨU
# ======================================================
class CustomPasswordResetView(PasswordResetView):
    template_name = 'borrower/password_reset.html'
    email_template_name = 'borrower/password_reset_email.html'
    html_email_template_name = 'borrower/password_reset_email.html'
    subject_template_name = 'borrower/password_reset_subject.txt'
    success_url = '/borrower/password-reset/done/'

    def get_form_kwargs(self):
        """
        Ghi đè để hỗ trợ nhập username thay vì email.
        Django sẽ tự tạo form dùng email, nhưng ta thay giá trị này bằng email của user tìm được.
        """
        kwargs = super().get_form_kwargs()
        if self.request.method == "POST":
            username = self.request.POST.get("username")
            try:
                user = User.objects.get(username=username)
                # Gửi đúng định dạng mà Django PasswordResetForm cần
                kwargs["data"] = {"email": user.email}
            except User.DoesNotExist:
                # Không tiết lộ thông tin người dùng không tồn tại
                kwargs["data"] = {"email": ""}
        return kwargs
# Gắn alias ngắn gọn để import dễ
custom_password_reset_view = CustomPasswordResetView.as_view()
# ======================================================
#XÁC NHẬN MƯỢN
# ======================================================
@login_required
def confirm_borrow(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        # Tạo bản ghi mượn
        Loan.objects.create(
            user=request.user,
            book=book,
            borrowed_at=timezone.now(),
            due_date=timezone.now() + timedelta(days=14)
        )
        # Sau khi xác nhận → chuyển đến danh sách mượn
        return redirect('borrower:my_loans')

    return render(request, 'borrower/confirm_borrow.html', {'book': book})
# ======================================================
# ĐĂNG KÝ YÊU CẦU KIỂM TRA (CHECK-IN / CHECK-OUT)
# ======================================================
@login_required
def check_request_view(request):
    """
    Sinh viên gửi yêu cầu Check-in / Check-out.
    Hiển thị danh sách yêu cầu đã gửi và trạng thái duyệt của quản lý.
    """
    if request.method == 'POST':
        form = CheckRequestForm(request.POST)
        if form.is_valid():
            check_request = form.save(commit=False)
            check_request.user = request.user
            check_request.save()
            messages.success(request, "✅ Yêu cầu của bạn đã được gửi tới quản lý.")
            return redirect('borrower:borrower_home')
    else:
        form = CheckRequestForm()

    # Danh sách yêu cầu của người dùng hiện tại
    user_requests = CheckRequest.objects.filter(user=request.user).order_by('-created_at')

    # Phân trang 5 yêu cầu mỗi trang
    paginator = Paginator(user_requests, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'borrower/check_requests.html', {
        'form': form,
        'page_obj': page_obj,
    })


@login_required
def delete_check_request(request, request_id):
    """
    Cho phép người dùng xóa yêu cầu chưa được duyệt hoặc bị từ chối.
    """
    check_request = get_object_or_404(CheckRequest, id=request_id, user=request.user)

    if check_request.approved:
        messages.error(request, "❌ Yêu cầu đã được duyệt, không thể xóa.")
    else:
        check_request.delete()
        messages.success(request, "🗑️ Yêu cầu của bạn đã được xóa thành công.")

    return redirect('borrower:check_requests')


# ======================================================
# ĐĂNG KÝ NGƯỜI DÙNG (REGISTER)
# ======================================================
def register(request):
    """
    Trang đăng ký tài khoản người dùng mới.
    Sau khi đăng ký xong sẽ tự đăng nhập và chuyển về trang mượn sách.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "🎉 Đăng ký thành công! Bạn đã được đăng nhập.")
            return redirect("borrower:borrower_home")
        else:
            messages.error(request, "❌ Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.")
    else:
        form = UserCreationForm()

    return render(request, "borrower/register.html", {"form": form})


# ======================================================
# TRANG CHỦ NGƯỜI MƯỢN
# ======================================================
from django.db.models import Sum
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from manager.models import Book, Penalty, CheckRequest
from borrower.models import Loan


@login_required
def borrower_home(request):
    """
    Trang chủ hiển thị danh sách sách, lọc, tìm kiếm,
    và cảnh báo nếu có sách mượn quá hạn hoặc bị phạt.
    """

    # ======================================================
    # 1️⃣ Lấy phiếu mượn của người dùng
    # ======================================================
    user_loans = Loan.objects.filter(user=request.user, returned=False)
    overdue_loans = user_loans.filter(due_date__lt=timezone.now())

    # Tạo phiếu phạt tự động nếu quá hạn
    for loan in overdue_loans:
        loan.create_penalty_if_overdue()

    # ======================================================
    # 2️⃣ Tính tổng số phiếu phạt chưa thanh toán
    # ======================================================
    unpaid_penalties = Penalty.objects.filter(user=request.user, cleared=False)
    total_unpaid_amount = unpaid_penalties.aggregate(Sum("amount"))["amount__sum"] or 0

    # ======================================================
    # 3️⃣ Thông báo sắp đến hạn trả (trước 2 ngày)
    # ======================================================
    today = timezone.now().date()
    upcoming_loans = user_loans.filter(due_date__gt=today, due_date__lte=today + timedelta(days=2))

    if upcoming_loans.exists():
        loan_titles = ", ".join([loan.book.title for loan in upcoming_loans])
        messages.info(
            request,
            f"📅 Bạn có {upcoming_loans.count()} cuốn sách sắp đến hạn trả: {loan_titles}."
        )
    # ======================================================
    # 4️⃣ Trạng thái yêu cầu Check-in / Check-out
    # ======================================================
    latest_request = CheckRequest.objects.filter(user=request.user).order_by('-created_at').first()
    if latest_request:
        if latest_request.approved:
            messages.success(request, "🎉 Yêu cầu Check-in/Check-out của bạn đã được quản lý duyệt!")
        elif latest_request.rejected:
            messages.error(request, "❌ Yêu cầu Check-in/Check-out của bạn đã bị từ chối.")
        else:
            messages.info(request, "🕓 Yêu cầu Check-in/Check-out của bạn đang chờ duyệt...")

    # ======================================================
    # 5️⃣ Tìm kiếm & lọc sách
    # ======================================================
    query = request.GET.get("q", "")
    selected_category = request.GET.get("category", "")
    selected_year = request.GET.get("year", "")

    books = Book.objects.all()

    if query:
        books = books.filter(title__icontains=query) | books.filter(author__icontains=query)
    if selected_category:
        books = books.filter(category__iexact=selected_category)
    if selected_year:
        books = books.filter(year=selected_year)

    categories = sorted(
        [c for c in Book.objects.values_list('category', flat=True).distinct() if c],
        key=lambda x: x.lower()
    )
    years = sorted(
        [y for y in Book.objects.values_list('year', flat=True).distinct() if y],
        reverse=True
    )

    # ======================================================
    # 6️⃣ Phân trang & hiển thị
    # ======================================================
    paginator = Paginator(books, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    new_books = Book.objects.all().order_by("-created_at")[:6]

    context = {
        "new_books": new_books,
        "page_obj": page_obj,
        "query": query,
        "categories": categories,
        "years": years,
        "selected_category": selected_category,
        "selected_year": selected_year,
        "overdue_loans": overdue_loans,
        "unpaid_penalties": unpaid_penalties,
        "total_unpaid_amount": total_unpaid_amount,  # 👈 Dùng cho popup gộp
    }

    return render(request, "borrower/home.html", context)



# ======================================================
# MƯỢN SÁCH
# ======================================================
# ======================================================
# XÁC NHẬN MƯỢN (cho phép người quản lý chọn thời gian mượn)
# ======================================================
@login_required
def confirm_borrow(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        # Nếu là quản lý (is_staff) thì cho phép chọn số ngày mượn tùy ý
        if request.user.is_staff:
            try:
                days = int(request.POST.get("days", 7))
            except ValueError:
                days = 7
        else:
            # Người mượn bình thường: mặc định 7 ngày
            days = 7

        due_date = timezone.now() + timedelta(days=days)

        # Tạo bản ghi mượn
        if book.available_copies > 0:
            Loan.objects.create(
                user=request.user,
                book=book,
                borrowed_at=timezone.now(),
                due_date=due_date
            )
            book.available_copies -= 1
            book.save()

            messages.success(
                request,
                f"✅ Mượn sách '{book.title}' thành công. Hạn trả sau {days} ngày ({due_date.strftime('%d/%m/%Y')})."
            )
        else:
            messages.error(request, "❌ Sách hiện đã hết bản có sẵn.")

        return redirect('borrower:my_loans')

    # GET → hiển thị form xác nhận mượn
    return render(request, 'borrower/confirm_borrow.html', {'book': book})

# ======================================================
# DANH SÁCH PHIẾU MƯỢN
# ======================================================
@login_required
def my_loans(request):
    """
    Hiển thị tất cả các phiếu mượn của người dùng hiện tại,
    kèm xử lý phạt nếu có sách quá hạn và phân trang.
    """
    loans = Loan.objects.filter(user=request.user).order_by("-borrowed_at")

    for loan in loans:
        loan.create_penalty_if_overdue()

    paginator = Paginator(loans, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "borrower/my_loans.html", {"page_obj": page_obj})


# ======================================================
# TRẢ SÁCH
# ======================================================
@login_required
def return_book(request, loan_id):
    """
    Người dùng trả sách → cập nhật trạng thái & số lượng
    """
    loan = get_object_or_404(Loan, id=loan_id, user=request.user)

    if loan.returned:
        messages.info(request, f"📘 Sách '{loan.book.title}' đã được trả trước đó.")
        return redirect("borrower:my_loans")

    loan.returned = True
    loan.returned_at = timezone.now()
    loan.save()

    loan.book.available_copies += 1
    loan.book.save()

    messages.success(request, f"✅ Bạn đã trả sách '{loan.book.title}' thành công.")
    return redirect("borrower:my_loans")


# ======================================================
# TÌM KIẾM
# ======================================================
@login_required
def search(request):
    query = request.GET.get("q", "")
    books = Book.objects.all()

    if query:
        books = books.filter(title__icontains=query) | books.filter(author__icontains=query)
    else:
        messages.info(request, "🔍 Hãy nhập tên hoặc tác giả để tìm sách.")

    paginator = Paginator(books, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "borrower/search.html", {
        "query": query,
        "page_obj": page_obj,
    })


# ======================================================
# HỒ SƠ NGƯỜI DÙNG
# ======================================================
@login_required
def profile_view(request):
    """
    Trang hồ sơ người dùng — hiển thị thông tin tài khoản và các sách đang mượn.
    (Không hiển thị cảnh báo quá hạn, chỉ cập nhật phạt trong nền)
    """
    # 🧹 Xóa toàn bộ message còn tồn đọng (ví dụ từ trang home)
    list(messages.get_messages(request))

    user = request.user
    profile = UserProfile.objects.filter(user=user).first()
    loans = Loan.objects.filter(user=user).select_related('book')

    # 🔹 Tự động cập nhật phiếu phạt nếu có sách quá hạn, nhưng KHÔNG hiển thị cảnh báo
    for loan in loans:
        if loan.is_overdue():
            loan.create_penalty_if_overdue()

    return render(request, "borrower/profile.html", {
        "profile": profile,
        "loans": loans,
    })



@login_required
def update_profile(request):
    """
    Cho phép người dùng cập nhật thông tin hồ sơ (email, mã sinh viên)
    """
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "✅ Hồ sơ đã được cập nhật thành công.")
            return redirect("borrower:profile")
        else:
            messages.error(request, "⚠️ Có lỗi xảy ra khi cập nhật hồ sơ.")
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, "borrower/update_profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })


@login_required
def change_password(request):
    """
    Cho phép người dùng đổi mật khẩu (và vẫn giữ đăng nhập sau khi đổi)
    """
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "🔐 Mật khẩu đã được thay đổi thành công.")
            return redirect("borrower:profile")
        else:
            messages.error(request, "⚠️ Mật khẩu không hợp lệ. Vui lòng thử lại.")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, "borrower/change_password.html", {"form": form})


# ======================================================
# TRANG XEM DANH SÁCH PHIẾU PHẠT
# ======================================================
@login_required
def my_penalties(request):
    penalties = Penalty.objects.filter(user=request.user).order_by('-created_at')

    paginator = Paginator(penalties, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'borrower/my_penalties.html', {'penalties': page_obj})
