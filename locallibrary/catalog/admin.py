from django.contrib import admin

from .models import Auction, Bid, Comment

# @admin.register(Auction)
# class AuctionAdmin(admin.ModelAdmin):
#     list_display = (
#     'title', 'condition', 'date_created', 'owner', 'date_expired', 'price', 'amount_of_bids', 'closed', 'winnerBid')
#     list_filter = ('date_created', 'closed', 'condition')
#     fields = ['title', 'condition', ('date_created', 'date_expired'), 'owner', ('price', 'amount_of_bids'), 'image',
#               'closed']
#
#
# @admin.register(Bid)
# class BidAdmin(admin.ModelAdmin):
#     list_display = ('auction', 'price', 'user', 'date_created', 'winningBid')
#     list_filter = ('auction', 'winningBid')
#
# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('auction', 'user', 'message', 'date_created')
#     list_filter = ('auction', 'user')

admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Comment)

from .models import Profile

admin.site.register(Profile)
