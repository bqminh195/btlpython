from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "category", "year")
    search_fields = ("title", "author", "category", "year")
    list_filter = ("category", "year")
