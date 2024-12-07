from rest_framework import serializers
from .models import Diary
import os

class DiarySerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    file_url = serializers.SerializerMethodField()
    file_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Diary
        fields = ['id', 'user', 'title', 'content', 'file', 'file_url', 'file_type', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'file_url', 'file_type']
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None
    
    def get_file_type(self, obj):
        if obj.file:
            ext = os.path.splitext(obj.file.name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                return 'image'
            elif ext in ['.mp3', '.wav', '.ogg', '.m4a']:
                return 'audio'
            else:
                return 'other'
        return None