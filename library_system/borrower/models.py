from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from manager.models import Book, Penalty  # 🔗 Đồng bộ dữ liệu với bên quản lý


# -----------------------------
# Hàm tính ngày trả mặc định
# -----------------------------
def default_due_date():
    """Hạn trả mặc định là 7 ngày kể từ ngày mượn"""
    return timezone.now() + timedelta(days=7)


# -----------------------------
# MODEL PHIẾU MƯỢN (Loan)
# -----------------------------
class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người mượn")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="Sách mượn")
    borrowed_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày mượn")
    due_date = models.DateTimeField(default=default_due_date, verbose_name="Hạn trả")
    returned = models.BooleanField(default=False, verbose_name="Đã trả")
    returned_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày trả")

    # -----------------------------
    # Các hàm xử lý nghiệp vụ
    # -----------------------------
    def is_overdue(self):
        """Kiểm tra nếu sách này đã quá hạn mà chưa trả."""
        return not self.returned and timezone.now().date() > self.due_date.date()

    def days_overdue(self):
        """Tính số ngày quá hạn (chỉ tính theo ngày)."""
        if not self.is_overdue():
            return 0
        return max(0, (timezone.now().date() - self.due_date.date()).days)

    def create_penalty_if_overdue(self):
        """
        Tự động tạo phiếu phạt nếu sách này quá hạn mà chưa có phiếu phạt tương ứng.
        """
        if self.is_overdue():
            overdue_days = self.days_overdue()
            fine_amount = overdue_days * 1000  # 💰 1000 VNĐ / ngày quá hạn

            # Kiểm tra xem phiếu phạt cho Loan này đã tồn tại chưa
            if not Penalty.objects.filter(loan=self).exists():
                Penalty.objects.create(
                    user=self.user,
                    loan=self,
                    amount=fine_amount,
                    reason=f"Quá hạn {overdue_days} ngày",
                    cleared=False,
                )

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    class Meta:
        verbose_name = "Phiếu mượn"
        verbose_name_plural = "📘 Danh sách phiếu mượn"
        ordering = ["-borrowed_at"]


# -----------------------------
# MODEL HỒ SƠ NGƯỜI MƯỢN
# -----------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Tài khoản")
    msv = models.CharField(max_length=20, verbose_name="Mã sinh viên", unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.msv}"

    class Meta:
        verbose_name = "Hồ sơ người mượn"
        verbose_name_plural = "👤 Hồ sơ người mượn"
