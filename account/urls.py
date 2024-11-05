from django.urls import path
from account.views.home import MemberView,HomeView
from account.views.user import SignupView,UserLogin,UserLogout

urlpatterns = [
    path('member/', MemberView.as_view(), name='member'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('', HomeView.as_view(), name='home'),
]

