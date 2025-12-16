from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        # Set user_type to 'client' by default
        validated_data['user_type'] = 'client'
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'user_type')


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="User's email address")
    otp = serializers.CharField(max_length=6, help_text="6-digit OTP code")


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(help_text="User's email address")
