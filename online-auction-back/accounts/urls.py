from django.urls import path
from .views import (
    RegisterView, LoginView, ResendOTPView, UserInfoView, VerifyOTPView,
    ForgotPasswordView, ResetPasswordView, TwoFactorSetupView, TwoFactorEnableView,
    TwoFactorDisableView, TwoFactorVerifyLoginView, TwoFactorStatusView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserInfoView.as_view(), name='user-info'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='auth-resend-otp'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    # 2FA endpoints
    path('2fa/setup/', TwoFactorSetupView.as_view(), name='2fa-setup'),
    path('2fa/enable/', TwoFactorEnableView.as_view(), name='2fa-enable'),
    path('2fa/disable/', TwoFactorDisableView.as_view(), name='2fa-disable'),
    path('2fa/verify/', TwoFactorVerifyLoginView.as_view(), name='2fa-verify'),
    path('2fa/status/', TwoFactorStatusView.as_view(), name='2fa-status'),
]
