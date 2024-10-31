from django.contrib import admin
from .models import Member, DocumentStorage

class MemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'nric', 'dob', 'class_passed', 'issue_date')
    search_fields = ('full_name', 'email', 'nric')
    list_filter = ('class_passed', 'issue_date')
    ordering = ('-issue_date',)

class DocumentStorageAdmin(admin.ModelAdmin):
    list_display = ('member', 'image')
    search_fields = ('member__full_name',)
    list_filter = ('member',)


admin.site.register(Member, MemberAdmin)
admin.site.register(DocumentStorage, DocumentStorageAdmin)