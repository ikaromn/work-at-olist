from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from .models import CallRecord
from .serializers import CallRecordSerializer

class CallRecordCreate(generics.CreateAPIView):
    queryset = CallRecord.objects.all()
    serializer_class = CallRecordSerializer
