from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

User = get_user_model()  # Get the user model (to support custom user models)


class Auction(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('started', 'Started'),
        ('ended', 'Ended'),
    ]

    title = models.CharField(max_length=200)  # Title of the auction item
    description = models.TextField()  # Description of the auction item
    image = models.ImageField(upload_to='auction_items/')  # Image for the auction item
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="auctions", blank=True)
    start_date_time = models.DateTimeField()  # Start date and time of the auction
    end_date_time = models.DateTimeField()  # End date and time of the auction
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)  # Starting price of the auction
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')  # Auction status

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_date_time']),
            models.Index(fields=['end_date_time']),
            models.Index(fields=['starting_price']),
            models.Index(fields=['status', 'start_date_time']),
            models.Index(fields=['status', 'end_date_time']),
        ]

    def __str__(self):
        return self.title  # Return the auction title

    def get_winner(self):
        """Get the winning bid (highest vote) for this auction."""
        return self.votes.order_by('-price').first()

    def get_current_price(self):
        """Get the current highest bid or starting price."""
        highest_vote = self.get_winner()
        return highest_vote.price if highest_vote else self.starting_price


class Vote(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='votes')  # Auction related to the vote
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')  # User who made the vote
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price for the vote
    created_at = models.DateTimeField(default=timezone.now)  # When the bid was placed

    class Meta:
        indexes = [
            models.Index(fields=['auction', '-price']),
            models.Index(fields=['user']),
            models.Index(fields=['-created_at']),
        ]

    def clean(self):
        """Custom validation to ensure the vote price is valid."""
        if self.price <= self.auction.starting_price:
            raise ValidationError("Vote price must be higher than the starting price.")

        # Get the last vote price if it exists
        last_vote = self.auction.votes.order_by('-price').first()
        if last_vote and self.price <= last_vote.price:
            raise ValidationError("Vote price must be higher than the last vote price.")

    def save(self, *args, **kwargs):
        """Override save method to include validation."""
        self.clean()  # Call the clean method to validate
        super().save(*args, **kwargs)  # Call the superclass save method

    def __str__(self):
        return f"Vote by {self.user.email} for {self.auction.title} at price {self.price}"


class AuctionNotification(models.Model):
    """Track sent notifications to prevent duplicates."""
    NOTIFICATION_TYPES = [
        ('start_soon', 'Auction Start Soon'),
        ('started', 'Auction Started'),
        ('ends_soon', 'Auction Ends Soon'),
        ('ended', 'Auction Ended'),
        ('outbid', 'Outbid'),
        ('winner', 'Winner'),
    ]

    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auction_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['auction', 'user', 'notification_type']),
        ]
        unique_together = [['auction', 'user', 'notification_type']]

    def __str__(self):
        return f"{self.notification_type} for {self.user.email} - {self.auction.title}"
