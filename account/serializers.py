from rest_framework import serializers
from .models import Member,DocumentStorage


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"
        
        
class DocumentStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentStorage
        fields = "__all__"