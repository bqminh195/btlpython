from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class CheckRequest(models.Model):
    CHECK_TYPE_CHOICES = [
        ('IN', 'Check-in'),
        ('OUT', 'Check-out'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    check_type = models.CharField(max_length=10, choices=CHECK_TYPE_CHOICES)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    manager_note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_check_type_display()} ({'✔' if self.approved else '⏳'})"


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Tên sách")
    author = models.CharField(max_length=255, verbose_name="Tác giả")
    year = models.PositiveIntegerField(verbose_name="Năm xuất bản", null=True, blank=True)
    category = models.CharField(max_length=100, verbose_name="Thể loại", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover = models.ImageField(upload_to='book_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.available_copies = self.total_copies
        elif self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# -------------------------------
# HỒ SƠ QUẢN LÝ
# -------------------------------
class ManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    manager_code = models.CharField(max_length=20, unique=True, verbose_name="Mã quản lý")
    email = models.EmailField(verbose_name="Email liên hệ")

    def __str__(self):
        return f"{self.user.username} - {self.manager_code}"

    class Meta:
        verbose_name = "Hồ sơ quản lý"
        verbose_name_plural = "Hồ sơ quản lý"

# -------------------------------
# CHỈ GIỮ LẠI MỘT BẢNG PHẠT
# -------------------------------
class Penalty(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Người bị phạt")
    loan = models.ForeignKey(
        "borrower.Loan",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="manager_penalties",
        verbose_name="Phiếu mượn liên quan"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reason = models.TextField(default="Quá hạn trả sách")
    created_at = models.DateTimeField(auto_now_add=True)
    cleared = models.BooleanField(default=False, verbose_name="Đã thanh toán")

    def __str__(self):
        return f"{self.user.username} - {self.amount}đ ({'Đã trả' if self.cleared else 'Chưa trả'})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Phiếu phạt"
        verbose_name_plural = "Quản lý phiếu phạt"
