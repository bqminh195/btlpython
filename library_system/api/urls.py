# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'books', views.BookViewSet, basename='book')
router.register(r'loans', views.LoanViewSet, basename='loan')

urlpatterns = [
    path('', views.index, name='api-home'),
    path('login/', views.login_view, name='api-login'),
    path('stats/', views.stats_view, name='api-stats'),
    path('', include(router.urls)),
]
