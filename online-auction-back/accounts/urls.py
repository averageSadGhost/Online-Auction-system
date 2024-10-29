from django.urls import path
from .views import RegisterView, LoginView, UserInfoView, VerifyOTPView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserInfoView.as_view(), name='user-info'),
    path('auth/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
]
