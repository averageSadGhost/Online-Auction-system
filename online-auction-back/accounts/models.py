from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now, timedelta
import secrets

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        

        return self.create_user(email, password, **extra_fields)
    

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('client', 'Client'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client')
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Password reset fields
    password_reset_token = models.CharField(max_length=64, blank=True, null=True)
    password_reset_expiry = models.DateTimeField(blank=True, null=True)

    # 2FA fields (TOTP)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['password_reset_token']),
        ]

    def __str__(self):
        return self.email

    def generate_otp(self):
        """Generate a 6-digit OTP and set expiry to 3 minutes from now."""
        import random
        self.otp = f"{random.randint(100000, 999999)}"
        self.otp_expiry = now() + timedelta(minutes=3)
        self.save()

    def generate_password_reset_token(self):
        """Generate a password reset token valid for 1 hour."""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_expiry = now() + timedelta(hours=1)
        self.save()
        return self.password_reset_token

    def clear_password_reset_token(self):
        """Clear the password reset token after use."""
        self.password_reset_token = None
        self.password_reset_expiry = None
        self.save()

    def generate_2fa_secret(self):
        """Generate a new TOTP secret for 2FA setup."""
        import pyotp
        self.two_factor_secret = pyotp.random_base32()
        self.save()
        return self.two_factor_secret

    def get_2fa_uri(self):
        """Get the otpauth URI for QR code generation."""
        import pyotp
        if not self.two_factor_secret:
            return None
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.provisioning_uri(name=self.email, issuer_name="AuctionHub")

    def verify_2fa_code(self, code):
        """Verify a TOTP code."""
        import pyotp
        if not self.two_factor_secret:
            return False
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(code)
