from django.contrib import admin
from .models import Auction, Vote

class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date_time', 'end_date_time','starting_price')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'auction', 'price')

admin.site.register(Auction, AuctionAdmin)
admin.site.register(Vote, VoteAdmin)
