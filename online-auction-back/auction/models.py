from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from project import settings

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

    def __str__(self):
        return self.title  # Return the auction title

class Vote(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='votes')  # Auction related to the vote
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')  # User who made the vote
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price for the vote

    def clean(self):
        """Custom validation to ensure the vote price is valid."""
        if self.price < self.auction.starting_price:
            raise ValidationError("Vote price cannot be less than the starting price.")
        
        # Get the last vote price if it exists
        last_vote = self.auction.votes.order_by('-id').first()
        if last_vote and self.price < last_vote.price:
            raise ValidationError("Vote price cannot be less than the last vote price.")

    def save(self, *args, **kwargs):
        """Override save method to include validation."""
        self.clean()  # Call the clean method to validate
        super().save(*args, **kwargs)  # Call the superclass save method

    def __str__(self):
        return f"Vote by {self.user.email} for {self.auction.title} at price {self.price}"
