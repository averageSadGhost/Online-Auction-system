from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status
from django.utils.timezone import now

from django.conf import settings
from django.core import signing
from accounts.models import CustomUser
from accounts.utils import send_otp_email, send_password_reset_email
from .serializers import (
    RegisterSerializer, LoginSerializer, UserInfoSerializer,
    OTPSerializer, EmailSerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
    TwoFactorSetupSerializer, TwoFactorVerifySerializer, TwoFactorDisableSerializer,
    TwoFactorLoginSerializer
)
from rest_framework.generics import RetrieveAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RegisterView(APIView):
    """Register a new user account."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="register_user",
        operation_description="Register a new user account. An OTP will be sent to the provided email for verification.",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Registration successful, OTP sent",
                examples={"application/json": {"detail": "OTP sent to your email."}}
            ),
            400: openapi.Response(
                description="Validation error",
                examples={"application/json": {"email": ["This field must be unique."]}}
            ),
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.generate_otp()
            send_otp_email(user)
            return Response(
                {"detail": "OTP sent to your email."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """Authenticate a user and receive an auth token."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="login_user",
        operation_description="Authenticate with email and password. Returns an auth token on success, or requires 2FA if enabled.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful or 2FA required",
                examples={
                    "application/json": {
                        "token": "your-auth-token-here",
                        "requires_2fa": False
                    }
                }
            ),
            401: openapi.Response(
                description="Invalid credentials",
                examples={"application/json": {"detail": "Invalid credentials."}}
            ),
            403: openapi.Response(
                description="Account not verified",
                examples={"application/json": {"detail": "Account is not verified. Please verify your email."}}
            ),
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )

            if user is not None:
                if not user.is_verified:
                    return Response(
                        {"detail": "Account is not verified. Please verify your email."},
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Check if 2FA is enabled
                if user.two_factor_enabled:
                    # Generate temporary token for 2FA verification
                    temp_token = signing.dumps({'user_id': user.id}, salt='2fa-login')
                    return Response({
                        "requires_2fa": True,
                        "temp_token": temp_token
                    }, status=status.HTTP_200_OK)

                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    "token": token.key,
                    "requires_2fa": False
                }, status=status.HTTP_200_OK)

            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(RetrieveAPIView):
    """Get current authenticated user's information."""
    serializer_class = UserInfoSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="get_user_info",
        operation_description="Get the current authenticated user's profile information.",
        responses={
            200: UserInfoSerializer,
            401: openapi.Response(description="Not authenticated"),
        }
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class VerifyOTPView(APIView):
    """Verify user's email with OTP code."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="verify_otp",
        operation_description="Verify user's email address using the OTP code sent during registration.",
        request_body=OTPSerializer,
        responses={
            200: openapi.Response(
                description="Verification successful",
                examples={"application/json": {"detail": "Account verified successfully."}}
            ),
            400: openapi.Response(
                description="Invalid or expired OTP",
                examples={"application/json": {"detail": "Invalid OTP."}}
            ),
            404: openapi.Response(
                description="User not found",
                examples={"application/json": {"detail": "User not found."}}
            ),
        }
    )
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp and user.otp_expiry > now():
            user.is_verified = True
            user.otp = None
            user.otp_expiry = None
            user.save()
            return Response({"detail": "Account verified successfully."}, status=status.HTTP_200_OK)
        elif user.otp == otp and user.otp_expiry < now():
            return Response({"detail": "Expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):
    """Resend OTP verification code."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="resend_otp",
        operation_description="Request a new OTP code. Only works if the previous OTP has expired.",
        request_body=EmailSerializer,
        responses={
            200: openapi.Response(
                description="OTP sent successfully",
                examples={"application/json": {"detail": "A new OTP has been sent to your email."}}
            ),
            400: openapi.Response(
                description="Previous OTP still valid",
                examples={"application/json": {"detail": "The previous OTP is still valid."}}
            ),
            404: openapi.Response(
                description="User not found",
                examples={"application/json": {"detail": "User not found."}}
            ),
        }
    )
    def post(self, request):
        email = request.data.get('email')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.otp and user.otp_expiry > now():
            return Response(
                {"detail": "The previous OTP is still valid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.generate_otp()
        send_otp_email(user)

        return Response(
            {"detail": "A new OTP has been sent to your email."},
            status=status.HTTP_200_OK
        )


class ForgotPasswordView(APIView):
    """Request password reset link."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="forgot_password",
        operation_description="Request a password reset email. The email will contain a link to reset the password.",
        request_body=ForgotPasswordSerializer,
        responses={
            200: openapi.Response(
                description="Reset email sent",
                examples={"application/json": {"detail": "Password reset email sent."}}
            ),
            404: openapi.Response(
                description="User not found",
                examples={"application/json": {"detail": "User not found."}}
            ),
        }
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                # Return success even if user not found to prevent email enumeration
                return Response(
                    {"detail": "If an account exists with this email, a password reset link has been sent."},
                    status=status.HTTP_200_OK
                )

            # Generate password reset token
            token = user.generate_password_reset_token()

            # Build reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

            # Send password reset email
            send_password_reset_email(user, reset_url)

            return Response(
                {"detail": "If an account exists with this email, a password reset link has been sent."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """Reset password using token."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["Authentication"],
        operation_id="reset_password",
        operation_description="Reset password using the token received in the password reset email.",
        request_body=ResetPasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password reset successful",
                examples={"application/json": {"detail": "Password has been reset successfully."}}
            ),
            400: openapi.Response(
                description="Invalid or expired token",
                examples={"application/json": {"detail": "Invalid or expired reset token."}}
            ),
        }
    )
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']

            try:
                user = CustomUser.objects.get(password_reset_token=token)
            except CustomUser.DoesNotExist:
                return Response(
                    {"detail": "Invalid or expired reset token."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if token has expired
            if user.password_reset_expiry is None or user.password_reset_expiry < now():
                return Response(
                    {"detail": "Invalid or expired reset token."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Reset password
            user.set_password(password)
            user.password_reset_token = None
            user.password_reset_expiry = None
            user.save()

            return Response(
                {"detail": "Password has been reset successfully."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorSetupView(APIView):
    """Generate 2FA secret for setup."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Two-Factor Authentication"],
        operation_id="2fa_setup",
        operation_description="Generate a new 2FA secret. Returns the secret and QR code URI for authenticator apps.",
        responses={
            200: TwoFactorSetupSerializer,
            400: openapi.Response(
                description="2FA already enabled",
                examples={"application/json": {"detail": "2FA is already enabled."}}
            ),
        }
    )
    def post(self, request):
        user = request.user

        if user.two_factor_enabled:
            return Response(
                {"detail": "2FA is already enabled. Disable it first to set up again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate new secret
        secret = user.generate_2fa_secret()
        qr_uri = user.get_2fa_uri()

        return Response({
            "secret": secret,
            "qr_uri": qr_uri
        }, status=status.HTTP_200_OK)


class TwoFactorEnableView(APIView):
    """Enable 2FA after verifying setup code."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Two-Factor Authentication"],
        operation_id="2fa_enable",
        operation_description="Enable 2FA by verifying a code from the authenticator app.",
        request_body=TwoFactorVerifySerializer,
        responses={
            200: openapi.Response(
                description="2FA enabled successfully",
                examples={"application/json": {"detail": "2FA has been enabled successfully."}}
            ),
            400: openapi.Response(
                description="Invalid code or no secret",
                examples={"application/json": {"detail": "Invalid verification code."}}
            ),
        }
    )
    def post(self, request):
        serializer = TwoFactorVerifySerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            code = serializer.validated_data['code']

            if not user.two_factor_secret:
                return Response(
                    {"detail": "Please set up 2FA first."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.two_factor_enabled:
                return Response(
                    {"detail": "2FA is already enabled."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.verify_2fa_code(code):
                user.two_factor_enabled = True
                user.save()
                return Response(
                    {"detail": "2FA has been enabled successfully."},
                    status=status.HTTP_200_OK
                )

            return Response(
                {"detail": "Invalid verification code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorDisableView(APIView):
    """Disable 2FA."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Two-Factor Authentication"],
        operation_id="2fa_disable",
        operation_description="Disable 2FA. Requires password and current 2FA code.",
        request_body=TwoFactorDisableSerializer,
        responses={
            200: openapi.Response(
                description="2FA disabled successfully",
                examples={"application/json": {"detail": "2FA has been disabled successfully."}}
            ),
            400: openapi.Response(
                description="Invalid credentials or code",
                examples={"application/json": {"detail": "Invalid password or verification code."}}
            ),
        }
    )
    def post(self, request):
        serializer = TwoFactorDisableSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            password = serializer.validated_data['password']
            code = serializer.validated_data['code']

            if not user.two_factor_enabled:
                return Response(
                    {"detail": "2FA is not enabled."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verify password
            if not user.check_password(password):
                return Response(
                    {"detail": "Invalid password."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verify 2FA code
            if not user.verify_2fa_code(code):
                return Response(
                    {"detail": "Invalid verification code."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Disable 2FA
            user.two_factor_enabled = False
            user.two_factor_secret = None
            user.save()

            return Response(
                {"detail": "2FA has been disabled successfully."},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorVerifyLoginView(APIView):
    """Verify 2FA code during login."""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["Two-Factor Authentication"],
        operation_id="2fa_verify_login",
        operation_description="Verify 2FA code during login process. Returns auth token on success.",
        request_body=TwoFactorLoginSerializer,
        responses={
            200: openapi.Response(
                description="2FA verification successful",
                examples={"application/json": {"token": "your-auth-token-here"}}
            ),
            400: openapi.Response(
                description="Invalid or expired token/code",
                examples={"application/json": {"detail": "Invalid verification code."}}
            ),
        }
    )
    def post(self, request):
        serializer = TwoFactorLoginSerializer(data=request.data)
        if serializer.is_valid():
            temp_token = serializer.validated_data['temp_token']
            code = serializer.validated_data['code']

            try:
                # Decode temporary token (expires after 5 minutes)
                data = signing.loads(temp_token, salt='2fa-login', max_age=300)
                user_id = data.get('user_id')
                user = CustomUser.objects.get(id=user_id)
            except (signing.BadSignature, signing.SignatureExpired, CustomUser.DoesNotExist):
                return Response(
                    {"detail": "Invalid or expired session. Please login again."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verify 2FA code
            if not user.verify_2fa_code(code):
                return Response(
                    {"detail": "Invalid verification code."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate auth token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorStatusView(APIView):
    """Get 2FA status for current user."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Two-Factor Authentication"],
        operation_id="2fa_status",
        operation_description="Get the current 2FA status for the authenticated user.",
        responses={
            200: openapi.Response(
                description="2FA status",
                examples={"application/json": {"enabled": True}}
            ),
        }
    )
    def get(self, request):
        return Response({
            "enabled": request.user.two_factor_enabled
        }, status=status.HTTP_200_OK)