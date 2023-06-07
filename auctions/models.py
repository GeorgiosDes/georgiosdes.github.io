from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass
    

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Listing(models.Model):
    active = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500,blank=True)
    image = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} - {self.category}"

    
class Bid(models.Model):
    bid = models.DecimalField(max_digits=8, decimal_places=2)
    title = models.ForeignKey(Listing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - ${self.bid} by {self.user}"
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    title = models.ForeignKey(Listing, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} - {self.user} said: {self.comment}"
    

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.title}"