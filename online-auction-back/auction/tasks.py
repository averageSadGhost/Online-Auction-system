from huey import crontab
from huey.contrib.djhuey import periodic_task
from django.utils import timezone

from auction.models import Auction


@periodic_task(crontab(minute='*'))  # Run every minute
def check_auction_start_times():
    """
    Periodic task that checks for scheduled auctions that should be started
    based on their start_date_time.
    """
    # Get current time
    current_time = timezone.now()
    
    # Find all scheduled auctions where start_date_time has passed
    auctions_to_start = Auction.objects.filter(
        status='scheduled',
        start_date_time__lte=current_time
    )
    
    # Update status to 'started' for matching auctions
    updated_count = auctions_to_start.update(status='started')
    
    return f"Updated {updated_count} auctions to 'started' status"

@periodic_task(crontab(minute='*'))  # Run every minute
def check_auction_end_times():
    """
    Periodic task that checks for auctions that should be marked as 'ended'
    based on their end_date_time.
    """
    # Get current time
    current_time = timezone.now()
    
    # Find all auctions where end_date_time has passed and the status is 'started'
    auctions_to_end = Auction.objects.filter(
        status='started',
        end_date_time__lte=current_time
    )
    
    # Update status to 'ended' for matching auctions
    updated_count = auctions_to_end.update(status='ended')
    
    return f"Updated {updated_count} auctions to 'ended' status"