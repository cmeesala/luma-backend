from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Item
from .serializers import ItemSerializer

# Create your views here.

class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            'status': 'healthy',
            'service': 'luma-api',
            'version': '1.0.0'
        }, status=status.HTTP_200_OK)

class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
