from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Diary
from .serializers import DiarySerializer

# Create your views here.
class DiaryListCreateView(generics.ListCreateAPIView):
    serializer_class = DiarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Diary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DiaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DiarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Diary.objects.filter(user=self.request.user)