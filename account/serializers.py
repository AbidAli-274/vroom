from rest_framework import serializers
from .models import Member,DocumentStorage
from django.contrib.auth.models import User


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"
        
        
class DocumentStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentStorage
        fields = "__all__"
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
        ]
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value