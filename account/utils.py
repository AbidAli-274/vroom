from django.contrib.auth.models import User
from djangoapp.exception_handler import CustomAPIException
from rest_framework import status

def get_user_by_email_or_username(staff_email_or_username):
    try:
        user = User.objects.get(email=staff_email_or_username)
    except User.DoesNotExist:
        try:
            user = User.objects.get(username=staff_email_or_username)
        except User.DoesNotExist:
            raise CustomAPIException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found with the provided email or username.",
            )
    return user