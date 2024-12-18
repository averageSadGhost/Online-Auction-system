from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework import status
from django.utils.timezone import now

from accounts.models import CustomUser
from accounts.utils import send_otp_email
from .serializers import RegisterSerializer, LoginSerializer, UserInfoSerializer
from rest_framework.generics import RetrieveAPIView
from drf_yasg.utils import swagger_auto_schema

class RegisterView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        tags=["auth"],
        operation_description="Register a new user and send OTP",
        request_body=RegisterSerializer,
    )
    def post(self, request):

        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate OTP and save it to the user
            user.generate_otp()

            # Send OTP to the user's email
            send_otp_email(user)

            return Response(
                {"detail": "OTP sent to your email."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["auth"],
        operation_description="Login a user",
        request_body=LoginSerializer,
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )

            if user is not None:
                if not user.is_verified:  # Check if the user is verified
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
    serializer_class = UserInfoSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["auth"], operation_description="Get user information")
    def get(self, request, *args, **kwargs):
        # Use the authenticated user from the request
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp and user.otp_expiry > now():
            user.is_verified = True
            user.otp = None  # Clear OTP after verification
            user.otp_expiry = None
            user.save()
            return Response({"detail": "Account verified successfully."}, status=status.HTTP_200_OK)
        elif user.otp == otp and user.otp_expiry < now():
            return Response({"detail": "Expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["auth"],
        operation_description="Resend a new OTP if the last one is expired.",
        request_body=None
    )
    def post(self, request):
        email = request.data.get('email')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the OTP has expired
        if user.otp and user.otp_expiry > now():
            return Response(
                {"detail": "The previous OTP is still valid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate and send a new OTP
        user.generate_otp()
        send_otp_email(user)

        return Response(
            {"detail": "A new OTP has been sent to your email."},
            status=status.HTTP_200_OK
        )