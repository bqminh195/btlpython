# api/serializers.py
from rest_framework import serializers
from manager.models import Book
from borrower.models import Loan


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'year', 'copies', 'cover']


class LoanSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = Loan
        fields = ['id', 'user', 'book_title', 'borrowed_at', 'due_date', 'returned']
