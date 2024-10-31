from django.urls import path
from .views import MemberView, SignupView,HomeView

urlpatterns = [
    path('member/', MemberView.as_view(), name='member'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('', HomeView.as_view(), name='signup'),
]
