from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms.widgets import DateInput

from .models import Auction, Bid, Profile


class AddBidForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddBidForm, self).__init__(*args, **kwargs)
        self.fields['price'].widget.attrs['readonly'] = True

    class Meta:
        model = Bid
        fields = ['price', 'auction', 'user']
        exclude = ('auction', 'user')
        widgets = {
            'auction': forms.HiddenInput(),
            'user': forms.HiddenInput()
        }


class AddAuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'condition', 'description', 'image', 'price', 'date_expired']
        labels = {
            "price": "Starting Price"
        }


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'dob']
        labels = {
            'dob': ('Date of birth'),
        }
        widgets = {
            'dob': DateInput(attrs={'type': 'date'})
        }
