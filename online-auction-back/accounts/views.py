from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status
from django.utils.timezone import now

from accounts.models import CustomUser
from accounts.utils import send_otp_email
from .serializers import RegisterSerializer, LoginSerializer, UserInfoSerializer, OTPSerializer, EmailSerializer
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
        operation_description="Authenticate with email and password. Returns an auth token on success.",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={"application/json": {"token": "your-auth-token-here"}}
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

                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": token.key}, status=status.HTTP_200_OK)

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