# api/views.py
from django.shortcuts import HttpResponse
from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from manager.models import Book
from borrower.models import Loan
from .serializers import BookSerializer, LoanSerializer


# 🟢 Kiểm tra API
def index(request):
    return HttpResponse("✅ API hoạt động thành công!")


# 🔐 Đăng nhập API
@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        role = "admin" if user.is_staff else "user"
        return Response({"message": f"Chào mừng {role}!", "role": role}, status=200)
    return Response({"error": "Sai tài khoản hoặc mật khẩu!"}, status=400)


# 📊 Thống kê
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_view(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    total_users = User.objects.count()
    total_books = Book.objects.count()
    borrowed_books = Loan.objects.filter(returned=False).count()
    borrows_this_week = Loan.objects.filter(borrowed_at__gte=week_ago).count()
    total_returns = Loan.objects.filter(returned=True).count()

    data = {
        "total_users": total_users,
        "total_books": total_books,
        "borrowed_books": borrowed_books,
        "total_returns": total_returns,
        "borrows_this_week": borrows_this_week,
    }
    return Response(data)


# 📚 API Sách (chỉ đọc)
class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = BookSerializer


# 📘 API danh sách mượn (cho admin hoặc người dùng)
class LoanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Loan.objects.select_related('book', 'user').all().order_by('-borrowed_at')
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
