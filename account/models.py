from django.db import models

class Member(models.Model):
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)
    nric = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    dob = models.DateField(blank=True, null=True)
    class_passed = models.CharField(max_length=50)
    address = models.TextField(blank=True, null=True)
    issue_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.full_name

class DocumentStorage(models.Model):
    image = models.CharField(max_length=200, blank=True, null=True)
    member = models.ForeignKey(Member,related_name='member_image', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Document for {self.member.full_name}"
