from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from.models import Chapter
from.serializers import ChapterSerializer

class ChapterViewSet(ModelViewSet):
    
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer