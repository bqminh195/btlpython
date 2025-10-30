from django.contrib import admin
from manager.models import Book, CheckRequest, Penalty

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "category", "year", "total_copies", "available_copies")
    search_fields = ("title", "author", "category")
    list_filter = ("category", "year")

@admin.register(CheckRequest)
class CheckRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "check_type", "created_at", "approved", "rejected")
    list_filter = ("check_type", "approved", "rejected")

@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "cleared", "created_at")
    list_filter = ("cleared",)
