import logging
from datetime import timedelta
from huey import crontab
from huey.contrib.djhuey import periodic_task, task
from django.utils import timezone
from django.db import IntegrityError

from auction.models import Auction, AuctionNotification

logger = logging.getLogger(__name__)


def send_notification(user, auction, notification_type, send_func, **kwargs):
    """
    Helper to send a notification and track it to prevent duplicates.

    Args:
        user: User to notify
        auction: The auction
        notification_type: Type of notification (e.g., 'start_soon', 'ended')
        send_func: The email sending function to call
        **kwargs: Additional arguments to pass to send_func
    """
    try:
        # Create notification record (will fail if duplicate due to unique_together)
        AuctionNotification.objects.create(
            auction=auction,
            user=user,
            notification_type=notification_type
        )
        # Send the email
        send_func(user, auction, **kwargs)
        logger.info(f"Sent {notification_type} notification to {user.email} for auction {auction.id}")
    except IntegrityError:
        # Notification already sent
        logger.debug(f"Notification {notification_type} already sent to {user.email} for auction {auction.id}")
    except Exception as e:
        logger.error(f"Failed to send {notification_type} notification: {e}")


@periodic_task(crontab(minute='*'))  # Run every minute
def check_auction_start_times():
    """
    Periodic task that checks for scheduled auctions that should be started
    based on their start_date_time.
    """
    from accounts.utils import send_auction_started_email

    current_time = timezone.now()

    # Find all scheduled auctions where start_date_time has passed
    auctions_to_start = Auction.objects.filter(
        status='scheduled',
        start_date_time__lte=current_time
    )

    # Get list of auctions before update for notifications
    auction_ids = list(auctions_to_start.values_list('id', flat=True))

    # Update status to 'started' for matching auctions
    updated_count = auctions_to_start.update(status='started')

    # Send notifications for each started auction
    if auction_ids:
        started_auctions = Auction.objects.filter(id__in=auction_ids).prefetch_related('users')
        for auction in started_auctions:
            for user in auction.users.all():
                send_notification(user, auction, 'started', send_auction_started_email)

    return f"Updated {updated_count} auctions to 'started' status"


@periodic_task(crontab(minute='*'))  # Run every minute
def check_auction_end_times():
    """
    Periodic task that checks for auctions that should be marked as 'ended'
    based on their end_date_time.
    """
    from accounts.utils import send_auction_ended_email, send_winner_email

    current_time = timezone.now()

    # Find all auctions where end_date_time has passed and the status is 'started'
    auctions_to_end = Auction.objects.filter(
        status='started',
        end_date_time__lte=current_time
    )

    # Get list of auctions before update for notifications
    auction_ids = list(auctions_to_end.values_list('id', flat=True))

    # Update status to 'ended' for matching auctions
    updated_count = auctions_to_end.update(status='ended')

    # Send notifications for each ended auction
    if auction_ids:
        ended_auctions = Auction.objects.filter(id__in=auction_ids).prefetch_related('users', 'votes__user')
        for auction in ended_auctions:
            # Get the winner
            winner_vote = auction.get_winner()
            winner_user = winner_vote.user if winner_vote else None

            # Send "auction ended" to all participants
            for user in auction.users.all():
                send_notification(user, auction, 'ended', send_auction_ended_email)

            # Send "winner" notification to the winner
            if winner_user:
                send_notification(winner_user, auction, 'winner', send_winner_email)

    return f"Updated {updated_count} auctions to 'ended' status"


@periodic_task(crontab(minute='*'))  # Run every minute
def check_auctions_starting_soon():
    """
    Check for auctions starting in approximately 30 minutes and notify users.
    """
    from accounts.utils import send_auction_start_soon_email

    current_time = timezone.now()
    # Window: 29-31 minutes from now (to catch auctions within 1 minute of the 30-min mark)
    window_start = current_time + timedelta(minutes=29)
    window_end = current_time + timedelta(minutes=31)

    auctions_starting_soon = Auction.objects.filter(
        status='scheduled',
        start_date_time__gte=window_start,
        start_date_time__lte=window_end
    ).prefetch_related('users')

    notification_count = 0
    for auction in auctions_starting_soon:
        for user in auction.users.all():
            try:
                AuctionNotification.objects.create(
                    auction=auction,
                    user=user,
                    notification_type='start_soon'
                )
                send_auction_start_soon_email(user, auction)
                notification_count += 1
                logger.info(f"Sent start_soon notification to {user.email} for auction {auction.id}")
            except IntegrityError:
                # Already notified
                pass
            except Exception as e:
                logger.error(f"Failed to send start_soon notification: {e}")

    return f"Sent {notification_count} 'starting soon' notifications"


@periodic_task(crontab(minute='*'))  # Run every minute
def check_auctions_ending_soon():
    """
    Check for auctions ending in approximately 10 minutes and notify users.
    """
    from accounts.utils import send_auction_ends_soon_email

    current_time = timezone.now()
    # Window: 9-11 minutes from now (to catch auctions within 1 minute of the 10-min mark)
    window_start = current_time + timedelta(minutes=9)
    window_end = current_time + timedelta(minutes=11)

    auctions_ending_soon = Auction.objects.filter(
        status='started',
        end_date_time__gte=window_start,
        end_date_time__lte=window_end
    ).prefetch_related('users')

    notification_count = 0
    for auction in auctions_ending_soon:
        for user in auction.users.all():
            try:
                AuctionNotification.objects.create(
                    auction=auction,
                    user=user,
                    notification_type='ends_soon'
                )
                send_auction_ends_soon_email(user, auction)
                notification_count += 1
                logger.info(f"Sent ends_soon notification to {user.email} for auction {auction.id}")
            except IntegrityError:
                # Already notified
                pass
            except Exception as e:
                logger.error(f"Failed to send ends_soon notification: {e}")

    return f"Sent {notification_count} 'ending soon' notifications"


@task()
def send_outbid_notification(auction_id, outbid_user_id, previous_bid, current_bid):
    """
    Async task to send outbid notification email.
    Called from WebSocket consumer when a new bid is placed.
    """
    from accounts.utils import send_outbid_email
    from accounts.models import CustomUser

    try:
        auction = Auction.objects.get(id=auction_id)
        user = CustomUser.objects.get(id=outbid_user_id)

        # Check if we already sent an outbid notification for this specific outbid event
        # We use a different approach here - we don't use unique_together since a user
        # can be outbid multiple times in the same auction
        send_outbid_email(user, auction, previous_bid, current_bid)
        logger.info(f"Sent outbid notification to {user.email} for auction {auction.id}")
    except Auction.DoesNotExist:
        logger.error(f"Auction {auction_id} not found for outbid notification")
    except CustomUser.DoesNotExist:
        logger.error(f"User {outbid_user_id} not found for outbid notification")
    except Exception as e:
        logger.error(f"Failed to send outbid notification: {e}")
