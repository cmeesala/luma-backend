from django.urls import path
from .views import (
    health_check,
    record_intent,
    get_interactions,
    get_bills_view,
    create_bill_view
)

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('record_intent/', record_intent, name='record_intent'),
    path('get_interactions/', get_interactions, name='get_interactions'),
    path('get_bills/', get_bills_view, name='get_bills'),
    path('create_bill/', create_bill_view, name='create_bill'),
] 