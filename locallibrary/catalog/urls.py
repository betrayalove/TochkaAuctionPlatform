from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('auction', views.AuctionListView.as_view(), name='auctions'),
    path('auction/<int:pk>', views.AuctionDetailView.as_view(), name='auction-detail'),
    path('register/', views.register, name='register'),
    path('about/', views.about, name='about'),
    path('profile/', views.profile, name='profile'),
    path('auction/<int:pk>/bids/', views.BidDetailView.as_view(), name='auction-bid'),
    path('account/<str:username>', views.UserAuctionListView.as_view(), name='account-auctions'),
    path('auction/closed', views.ClosedAuctionsListView.as_view(), name='auction-closed'),
    path('auction/<int:pk>/delete/', views.AuctionDeleteView.as_view(), name='auction-delete'),
    path('auction/<int:pk>/update/', views.AuctionUpdateView.as_view(), name='auction-update'),
    path('auction/create/', views.AuctionCreateView.as_view(), name='auction-create'),
    path('auction/closed/buy', views.money, name='money'),
]