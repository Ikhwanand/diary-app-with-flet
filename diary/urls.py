from django.urls import path 
from .views import DiaryListCreateView, DiaryDetailView

urlpatterns = [
    path('', DiaryListCreateView.as_view(), name='diary-list-create'),
    path('<int:pk>/', DiaryDetailView.as_view(), name='diary-detail'),
]
