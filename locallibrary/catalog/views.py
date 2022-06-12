from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views import generic
from django.views.generic import (
    DetailView
)
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.views.generic.edit import FormMixin

from .forms import AddAuctionForm
from .forms import AddBidForm
from .forms import UserRegisterForm, UserUpdateForm, UpdateProfileForm
from .models import Auction, Bid, Comment, Profile


def index(request):
    num_auctions = Auction.objects.all().count()
    num_bids = Bid.objects.all().count()
    num_comments = Comment.objects.all().count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'index.html',
        context={'num_auctions': num_auctions, 'num_bids': num_bids, 'num_comments': num_comments, 'num_visits': num_visits},
    )

def money(request):
    return render(request, 'catalog/money.html')


class AuctionListView(generic.ListView):
    template_name = 'catalog/auction_list.html'
    model = Auction
    paginate_by = 25


class AuctionDetailView(FormMixin, DetailView):
    model = Auction
    form_class = AddBidForm

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        checkAuctions()
        context = super().get_context_data(**kwargs)
        auction = get_object_or_404(Auction, pk=self.kwargs.get('pk'))
        context['bid_list'] = Bid.objects.filter(auction=auction).order_by('date_created')
        if len(context['bid_list']) <= 0:
            price = auction.price + getPercents(auction)
        else:
            price = context['bid_list'].last().price + getPercents(auction)
        context['form'] = AddBidForm(initial={
            'auction': self.object,
            'price': price,
            'user': self.request.user,
        })
        context['comments'] = Comment.objects.filter(auction_id=self.object).order_by('date_created')
        return context

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.POST.get("comment"):
                msg = Comment()
                msg.user = self.request.user
                msg.auction = self.get_object()
                msg.message = self.request.POST.get("comment")
                msg.date_created = timezone.now()
                msg.save()

        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            print("form was valid!")
            return self.form_valid(form)
        else:
            print("form wasn't valid!")
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.auction = self.object
        form.instance.price = self.request.POST.get("price")
        self.object.price = form.instance.price
        self.object.amount_of_bids = self.object.amount_of_bids + 1
        self.object.save()
        form.instance.user = self.request.user
        form.save()
        return super().form_valid(form)


class UserAuctionListView(generic.ListView):
    model = Auction
    template_name = 'catalog/account_auctions.html'
    context_object_name = 'items'
    paginate_by = 5

    def get_queryset(self):
        checkAuctions()
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Auction.objects.filter(owner=user).order_by('-date_created')


class BidDetailView(generic.DetailView):
    model = Auction
    template_name = 'catalog/bid_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        checkAuctions()
        auction = get_object_or_404(Auction, pk=self.kwargs.get('pk'))
        context['bid_list'] = Bid.objects.filter(auction=auction).order_by('date_created')
        return context


def getPercents(auction):
    percents = "1"
    increment = len(str(auction.price)) - 1
    print(increment)
    for a in range(increment - 1):
        percents = percents + "0"
    percents = int(percents)
    return percents


def about(request):
    checkAuctions()
    return render(request, 'catalog/about.html', {'title': 'About'})


class ClosedAuctionsListView(ListView):
    ordering = ['-date_created']
    template_name = "catalog/closed.html"
    paginate_by = 25
    context_object_name = 'items'

    def get_queryset(self):
        checkAuctions()
        return Auction.objects.filter(closed=True)


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'test@yandex.ru'
EMAIL_HOST_PASSWORD = 'password'


def checkAuctions():
    auctions = Auction.objects.all()
    bids = Bid.objects.all()
    valid_auctions = []
    sendMail = False
    for auc in auctions:
        if auc.expired and auc.closed == False:
            auc.closed = True
            last_bid = bids.filter(auction=auc).last()
            if last_bid is not None:
                auc.winnerBid = last_bid
                last_bid.winningBid = True
                last_bid.save()
                sendMail = True
            auc.save()
            if sendMail:
                subject = 'Won auction - ' + str(auc.title)
                message = 'Congratulations on winning the auction titled ' + str(
                    auc.title) + " please pay the user " + str(auc.owner.username) + ", the sum of £" + str(
                    auc.price) + "."

                email_from = EMAIL_HOST_USER
                recipient_list = [last_bid.user.email, ]
                try:
                    send_mail(subject, message, email_from, recipient_list)
                except:
                    pass
        else:
            valid_auctions.append(auc)

    return valid_auctions


# def checkAuctions():
#     auctions = Auction.objects.all()
#     bids = Bid.objects.all()
#     valid_auctions = []
#     sendMail = False
#     for auc in auctions:
#         if auc.expired and auc.closed == False:
#             auc.closed = True
#             last_bid = bids.filter(auction=auc).last()
#             if last_bid is not None:
#                 auc.winnerBid = last_bid
#                 last_bid.winningBid = True
#                 last_bid.save()
#                 sendMail = True
#             auc.save()
#             if sendMail:
#                 subject = 'Won auction - ' + str(auc.title)
#                 message = 'Congratulations on winning the auction titled ' + str(
#                     auc.title) + " please pay the user " + str(auc.owner.username) + ", the sum of $" + str(
#                     auc.price) + "."
#
#                 email_from = EMAIL_HOST_USER
#                 recipient_list = [last_bid.user.email, ]
#                 try:
#                     send_mail(subject, message, email_from, recipient_list)
#                 except:
#                     pass
#         else:
#             valid_auctions.append(auc)
#
#     return valid_auctions


## CREATE
class AuctionCreateView(LoginRequiredMixin, CreateView):
    model = Auction
    form_class = AddAuctionForm

    def form_valid(self, form):
        checkAuctions()
        form.instance.owner = self.request.user
        return super().form_valid(form)


## UPDATE
class AuctionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Auction
    fields = ['title', 'description', 'condition', 'image']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        checkAuctions()
        auction = self.get_object()
        return self.request.user == auction.owner


## DELETE

class AuctionDeleteView(DeleteView):
    model = Auction
    success_url = '/catalog/auction'

    def get_object(self, queryset=None):
        auction = super(AuctionDeleteView, self).get_object()
        if not auction.owner == self.request.user:
            raise Http404
        return auction


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Acccount created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'catalog/register.html', {'form': form})


@login_required
def profile(request):
    User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])
    if request.method == 'POST':
        updateUserForm = UserUpdateForm(request.POST, instance=request.user)
        updateProfileForm = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if updateUserForm.is_valid() and updateProfileForm.is_valid():
            updateUserForm.save()
            updateProfileForm.save()
            messages.success(request, f'Acccount updated!')
            return redirect('profile')
    else:
        updateUserForm = UserUpdateForm(instance=request.user)
        updateProfileForm = UpdateProfileForm(instance=request.user.profile)

    auctions = Auction.objects.filter(closed=True)
    myWins = []
    for aucs in auctions:
        if aucs.winnerBid:
            if aucs.winnerBid.user == request.user:
                myWins.append(aucs)

    context = {
        'updateUserForm': updateUserForm,
        'updateProfileForm': updateProfileForm,
        'myWins': myWins
    }

    return render(request, 'catalog/profile.html', context)
