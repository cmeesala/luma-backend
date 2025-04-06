from django.urls import path
from .views import ItemListCreateView, ItemDetailView, HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('items/', ItemListCreateView.as_view(), name='item-list-create'),
    path('items/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
] 