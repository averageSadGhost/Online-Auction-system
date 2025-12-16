import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_html_email(subject, template_name, context, recipient_email):
    """
    Send an HTML email using a template.

    Args:
        subject: Email subject
        template_name: Name of the template file (without path)
        context: Dictionary of context variables for the template
        recipient_email: Recipient's email address
    """
    try:
        html_content = render_to_string(f'emails/{template_name}', context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        logger.info(f"Email '{subject}' sent successfully to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email '{subject}' to {recipient_email}: {e}")
        return False


def send_otp_email(user):
    """
    Generate and send OTP email to user for account verification.

    Args:
        user: The user instance to send OTP to.
    """
    user.generate_otp()

    context = {
        'first_name': user.first_name,
        'otp': user.otp,
    }

    send_html_email(
        subject="Your OTP for Account Verification - AuctionHub",
        template_name='otp.html',
        context=context,
        recipient_email=user.email
    )


def send_password_reset_email(user, reset_url):
    """
    Send password reset email with reset link.

    Args:
        user: The user instance
        reset_url: The password reset URL with token
    """
    context = {
        'first_name': user.first_name,
        'reset_url': reset_url,
    }

    send_html_email(
        subject="Reset Your Password - AuctionHub",
        template_name='password_reset.html',
        context=context,
        recipient_email=user.email
    )


def send_auction_start_soon_email(user, auction):
    """
    Send notification that auction is starting soon (30 min).

    Args:
        user: The user to notify
        auction: The auction object
    """
    context = {
        'first_name': user.first_name,
        'auction_title': auction.title,
        'starting_price': f"{auction.starting_price:,.2f}",
        'start_time': auction.start_date_time.strftime('%B %d, %Y at %I:%M %p'),
        'auction_url': f"{settings.FRONTEND_URL}/auction/{auction.id}",
    }

    send_html_email(
        subject=f"Auction Starting Soon: {auction.title} - AuctionHub",
        template_name='auction_start_soon.html',
        context=context,
        recipient_email=user.email
    )


def send_auction_started_email(user, auction):
    """
    Send notification that auction has started.

    Args:
        user: The user to notify
        auction: The auction object
    """
    context = {
        'first_name': user.first_name,
        'auction_title': auction.title,
        'starting_price': f"{auction.starting_price:,.2f}",
        'end_time': auction.end_date_time.strftime('%B %d, %Y at %I:%M %p'),
        'auction_url': f"{settings.FRONTEND_URL}/auction/{auction.id}/bidding",
    }

    send_html_email(
        subject=f"Auction Now Live: {auction.title} - AuctionHub",
        template_name='auction_started.html',
        context=context,
        recipient_email=user.email
    )


def send_outbid_email(user, auction, previous_bid, current_bid):
    """
    Send notification that user has been outbid.

    Args:
        user: The user who was outbid
        auction: The auction object
        previous_bid: User's previous bid amount
        current_bid: New highest bid amount
    """
    context = {
        'first_name': user.first_name,
        'auction_title': auction.title,
        'previous_bid': f"{previous_bid:,.2f}",
        'current_bid': f"{current_bid:,.2f}",
        'end_time': auction.end_date_time.strftime('%B %d, %Y at %I:%M %p'),
        'auction_url': f"{settings.FRONTEND_URL}/auction/{auction.id}/bidding",
    }

    send_html_email(
        subject=f"You've Been Outbid: {auction.title} - AuctionHub",
        template_name='outbid.html',
        context=context,
        recipient_email=user.email
    )


def send_auction_ends_soon_email(user, auction):
    """
    Send notification that auction is ending soon (10 min).

    Args:
        user: The user to notify
        auction: The auction object
    """
    highest_vote = auction.get_winner()
    current_bid = highest_vote.price if highest_vote else auction.starting_price
    highest_bidder = highest_vote.user.email if highest_vote else "No bids yet"

    context = {
        'first_name': user.first_name,
        'auction_title': auction.title,
        'current_bid': f"{current_bid:,.2f}",
        'highest_bidder': highest_bidder,
        'end_time': auction.end_date_time.strftime('%B %d, %Y at %I:%M %p'),
        'auction_url': f"{settings.FRONTEND_URL}/auction/{auction.id}/bidding",
    }

    send_html_email(
        subject=f"Final Minutes: {auction.title} - AuctionHub",
        template_name='auction_ends_soon.html',
        context=context,
        recipient_email=user.email
    )


def send_auction_ended_email(user, auction):
    """
    Send notification that auction has ended.

    Args:
        user: The user to notify
        auction: The auction object
    """
    winner = auction.get_winner()
    final_price = winner.price if winner else auction.starting_price
    winner_name = f"{winner.user.first_name} {winner.user.last_name}" if winner else "No winner"

    context = {
        'first_name': user.first_name,
        'auction_title': auction.title,
        'final_price': f"{final_price:,.2f}",
        'winner_name': winner_name,
        'total_bids': auction.votes.count(),
        'auctions_url': f"{settings.FRONTEND_URL}/auctions",
    }

    send_html_email(
        subject=f"Auction Ended: {auction.title} - AuctionHub",
        template_name='auction_ended.html',
        context=context,
        recipient_email=user.email
    )


def send_winner_email(user, auction):
    """
    Send congratulations email to auction winner.

    Args:
        user: The winning user
        auction: The auction object
    """
    winner_vote = auction.get_winner()
    winning_price = winner_vote.price if winner_vote else auction.starting_price

    # Generate transaction ID
    transaction_id = f"AH-{auction.id}-{auction.end_date_time.strftime('%Y%m%d%H%M')}"

    context = {
        'first_name': user.first_name,
        'auction_title': auction.title,
        'winning_price': f"{winning_price:,.2f}",
        'transaction_id': transaction_id,
        'date_won': auction.end_date_time.strftime('%B %d, %Y at %I:%M %p'),
        'receipt_url': f"{settings.FRONTEND_URL}/won-auctions",
    }

    send_html_email(
        subject=f"Congratulations! You Won: {auction.title} - AuctionHub",
        template_name='winner.html',
        context=context,
        recipient_email=user.email
    )
