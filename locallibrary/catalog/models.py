from datetime import datetime, timedelta

from PIL import Image
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

CONDITION_CHOICES = [
    ('Новый', 'Новый'),
    ('Состояние нового', 'Состояние нового'),
    ('Состояние отличное', 'Состояние отличное'),
    ('Состояние хорошее', 'Состояние хорошее'),
    ('Состояние удовлетворительное.', 'Состояние удовлетворительное.'),
    ('Отремонтированный', 'Отремонтированный'),
    ('Новый с дефектами', 'Новый с дефектами'),
]


class Auction(models.Model):
    title = models.CharField(max_length=255)
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, default='New')
    description = models.TextField()
    image = models.ImageField(default='default.jpg', upload_to='images_auctions')
    date_created = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date_expired = models.DateTimeField(default=datetime.now() + timedelta(days=7))
    price = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    amount_of_bids = models.IntegerField(default=0)
    closed = models.BooleanField(default=False)
    winnerBid = models.ForeignKey('Bid', blank=True, null=True, on_delete=models.CASCADE, related_name='winner')

    @property
    def expired(self):
        expiry = self.date_expired.replace(tzinfo=None)
        now = timezone.now().replace(tzinfo=None)
        if now > expiry:
            return True
        return False

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('auction-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super(Auction, self).save(*args, **kwargs)
        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Bid(models.Model):
    price = models.IntegerField(default=1)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    winningBid = models.BooleanField(default=False)


class Comment(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date_created = models.DateTimeField()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='images_profiles')
    dob = models.DateField(max_length=8, default=timezone.now)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
