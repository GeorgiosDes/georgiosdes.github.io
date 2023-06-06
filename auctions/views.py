from django import forms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, Listing, Bid, Category, Comment, Watchlist

CATEGORY_CHOICES = [
    ('No Category', 'Choose Category'),
    ('Antiques', 'Antiques'),
    ('Books', 'Books'),
    ('Business & Industrial', 'Business & Industrial'),
    ('Clothing, Shoes & Accessories', 'Clothing, Shoes & Accessories'),
    ('Collectibles', 'Collectibles'),
    ('Computers/Tablets & Networking', 'Computers/Tablets & Networking'),
    ('Consumer Electronics', 'Consumer Electronics'),
    ('Crafts', 'Crafts'),
    ('Dolls & Bears', 'Dolls & Bears'),
    ('Home & Garden', 'Home & Garden'),
    ('Motors', 'Motors'),
    ('Sporting Goods', 'Sporting Goods'),
    ('Toys & Hobbies', 'Toys & Hobbies')
]


class CreateListing(forms.Form):
    title = forms.CharField(max_length=64,label=False,widget=forms.TextInput(attrs={"autofocus": "on", "placeholder": "Product Name", "class": "form-control col-sm-4"}))
    description = forms.CharField(max_length=500,label=False,required=False,widget=forms.Textarea(attrs={"placeholder": "Description", "class": "form-control col-sm-4"}))
    image = forms.URLField(label=False,required=False,widget=forms.URLInput(attrs={"placeholder": "Image URL", "class": "form-control col-sm-4"}))
    category = forms.CharField(label=False,widget=forms.Select(attrs={"class": "form-control col-sm-4"},choices=CATEGORY_CHOICES))
    price = forms.DecimalField(max_value=99999.99,label=False,required=False,widget=forms.NumberInput(attrs={"placeholder": "Starting Price", "class": "form-control col-sm-1"}))


class Comments(forms.Form):
    comment = forms.CharField(max_length=2000,label=False,widget=forms.Textarea(attrs={"placeholder": "Add comment...", "rows": 2, "class": "form-control col-sm-6"}))


class Bids(forms.Form):
    bid = forms.DecimalField(max_value=999999.99,label=False,widget=forms.NumberInput(attrs={"placeholder": "Bid", "class": "form-control col-sm-1"}))


def index(request):
    paginator = Paginator(Listing.objects.filter(active=True).order_by("-date_created"), 3)
    page = request.GET.get("page", 1)
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)
    return render(request, "auctions/index.html", {
        "listings": listings,
        "bids": Bid.objects.filter(id__in=Bid.objects.values("title").annotate(max_id=Max("id")).values("max_id")),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        author = request.user
        category = Category.objects.get(name=request.POST["category"])
        image = request.POST["image"] if request.POST["image"] else "https://content.gobsn.com/i/bodyandfit/no-xplode_Image_01?layer0=$PDP-MOB$"
        price = request.POST["price"] if request.POST["price"] else 0

        # Create new listing
        listing = Listing.objects.create(title=title, description=description, image=image, price=price, category=category, author=author)
        listing.save()

        listing_title = Listing.objects.get(pk=listing.id)
        bid = Bid(bid=price, title=listing_title, user=request.user)
        bid.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {
            "form": CreateListing()
        })
    

def listings(request, id):
    listing = get_object_or_404(Listing, pk=id)
    bid = Bid.objects.filter(title=listing).last()
    bid_counter = Bid.objects.filter(title=listing).count() - 1
    category = listing.category
    comments = Comment.objects.filter(title=listing)
    watchlist = Watchlist.objects.filter(user=request.user, title=listing) if request.user.is_authenticated else None
    return render(request, "auctions/listings.html", {
        "listing": listing,
        "bid": bid,
        "bid_counter": bid_counter,
        "category": category,
        "bids_form": Bids(),
        "comments_form": Comments(),
        "comments": comments,
        "watchlist": watchlist
    })


@login_required(login_url="/login")
def place_bid(request, id):
    listing = get_object_or_404(Listing,pk=id)
    highest_bidder = Bid.objects.filter(title=listing).last()
    bid_counter = Bid.objects.filter(title=listing).count() - 1
    bid = float(request.POST["bid"])

    # Ensure first bid is equal or greater than the starting price
    if bid >= listing.price and bid_counter == 0:
        place_bid = Bid(bid=bid, title=listing, user=request.user)
        place_bid.save()
        watchlist = Watchlist(user=request.user, title=listing)
        watchlist.save()
        success = "Bid was successful"
        return HttpResponseRedirect(reverse("index") + "?message=" + success)
    
    # Ensure every other bid is greater than the previous
    elif bid > listing.price and highest_bidder.user != request.user:
        place_bid = Bid(bid=bid, title=listing, user=request.user)
        place_bid.save()
        watchlist = Watchlist(user=request.user, title=listing)
        watchlist.save()
        success = "Bid was successful"
        return HttpResponseRedirect(reverse("index") + "?message=" + success)
    
    # Ensure you cannot bid again if you are already have the current bid
    elif bid > listing.price and highest_bidder.user == request.user:
        invalid_bid = "You are already the highest bidder"
        return HttpResponseRedirect(reverse("listings", args=[id]) + "?message=" + invalid_bid)
    else:
        invalid_bid = "Bid must be higher than current bid"
        return HttpResponseRedirect(reverse("listings", args=[id]) + "?message=" + invalid_bid)
    

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all().order_by('name')
    })


def category(request, id):
    paginator = Paginator(Listing.objects.filter(category=id), 3)
    page = request.GET.get("page", 1)
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": Category.objects.get(id=id)
    })


def close_bid(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing,pk=id)
        listing.active = False
        listing.save()
        return HttpResponseRedirect(reverse("index"))


def my_listings(request):
    paginator = Paginator(Listing.objects.filter(author=request.user), 3)
    page = request.GET.get("page", 1)
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)
    return render(request, "auctions/my_listings.html", {
        "listings": listings,
        "bids": Bid.objects.filter(id__in=Bid.objects.values("title").annotate(max_id=Max("id")).values("max_id"))
    })


@login_required(login_url="/login")
def comments(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing,pk=id)
        comment = request.POST["comment"]
        add_comment = Comment(user=request.user, title=listing, comment=comment)
        add_comment.save()
        return HttpResponseRedirect(reverse("listings", args=[id]))
    

@login_required(login_url="/login")
def watchlist(request):
    paginator = Paginator(Listing.objects.filter(pk__in=Watchlist.objects.filter(user=request.user).values_list("title")), 3)
    page = request.GET.get("page", 1)
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "bids": Bid.objects.filter(id__in=Bid.objects.values("title").annotate(max_id=Max("id")).values("max_id"))
    })
    

@login_required(login_url="/login")
def watchlist_action(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing,pk=id)
        user = request.user
        watchlist = Watchlist.objects.filter(user=user, title=listing)
        if not watchlist:
            watchlist = Watchlist(user=user, title=listing)
            watchlist.save()
            return HttpResponseRedirect(reverse("listings", args=[id]))
        else:
            watchlist.delete()
            return HttpResponseRedirect(reverse("listings", args=[id]))