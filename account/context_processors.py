# context_processors.py
from django.contrib.auth.models import User

def user_context(request):
    user_name = request.user
    return {'user_name': user_name}
