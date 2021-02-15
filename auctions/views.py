from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Listing, Watchlist, Comment, Bid
from django.contrib.auth.decorators import login_required

class createForm(forms.Form):
    CATEGORIES = (
        ('Fashion', 'Fashion'),
        ('Toys', 'Toys'),
        ('Electronics', 'Electronics'),
        ('Home', 'Home'),
        ('Sports', 'Sports'),
        ('Music', 'Music'),
        ('Others', 'Others')
    )
    title = forms.CharField(label="Title", widget=forms.TextInput(
				attrs={'class': 'form-control'}))
    price = forms.DecimalField(label="Price($)", decimal_places=2, widget=forms.NumberInput(
				attrs={'class': 'form-control'}))
    category = forms.ChoiceField(choices=CATEGORIES, widget=forms.Select(
				attrs={'class': 'form-control'}))
    content = forms.CharField(label="Content", widget=forms.Textarea(attrs={
        'style' : 'width:100%', 'class': 'form-control'}))
    photo = forms.CharField(label="Photo URL (optional)", required=False, widget=forms.TextInput(
				attrs={'class': 'form-control'}))
    #photo = forms.ImageField(label="Photo", required=False)

class commentForm(forms.Form):
    comment = forms.CharField(label="Leave a comment", widget=forms.Textarea(attrs={
    'style' : 'width:100%', 'class': 'form-control'}))

class bidForm(forms.Form):
    price = forms.DecimalField(label="Price($)", decimal_places=2, widget=forms.NumberInput(
				attrs={'class': 'form-control'}))
    

def index(request):
    return render(request, "auctions/index.html",{
        "auctions": Listing.objects.all(),
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

@login_required(login_url='/login') # Check if the user is logged in. If not: Redirect to '/login'
def create(request):
    if request.method == "POST":
        form = createForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            price = form.cleaned_data["price"]
            category = form.cleaned_data["category"]
            content = form.cleaned_data["content"]
            photo = form.cleaned_data["photo"]

            l = Listing(seller=request.user.username, title=title, category=category, description=content, price=price, photo=photo)
            l.save()

            return render(request, "auctions/index.html", {
                "auctions": Listing.objects.all()
            })
        return render(request, "auctions/create.html", {
            "form": form
        })        
    else:
        return render(request, "auctions/create.html", {
            "form": createForm()
        })

def auction(request, auction_id):
    listing_id = Listing.objects.get(id=auction_id)
    current_bids = Bid.objects.filter(listing=listing_id)
    highest_bid = listing_id.price
    for current_bid in current_bids:
        if current_bid.price > highest_bid:
            highest_bid = current_bid.price

    if request.user.is_authenticated:
        return render(request, "auctions/auction.html", {
            "auction": listing_id,
            "logged_in": request.user.is_authenticated,
            "comments": Comment.objects.filter(listing=listing_id),
            "commentForm": commentForm(),
            "bidForm": bidForm(),
            "highest_bid": highest_bid,
            "owner": str(request.user) == str(listing_id.seller),
            "in_watchlist": Watchlist.objects.filter(user=request.user, listing=listing_id)
        })
    else:
        return render(request, "auctions/auction.html", {
        "auction": listing_id,
        "logged_in": request.user.is_authenticated,
        "comments": Comment.objects.filter(listing=listing_id),
        "highest_bid": highest_bid,
        "in_watchlist": False
})

@login_required(login_url='/login')
def addWatchlist(request, auction_id):
    if request.method == "POST":
        # listing_id = request.POST.get("watchlist")
        listing_id = Listing.objects.get(pk=auction_id)
        
        if not Watchlist.objects.filter(user=request.user, listing=listing_id):

            w = Watchlist(user=request.user, listing=listing_id)

            w.save()
            return HttpResponseRedirect(reverse("watchlist"))

    return HttpResponseRedirect(reverse("watchlist"))
 
@login_required(login_url='/login')
def removeWatchlist(request, auction_id):
    if request.method == "POST":
        listing_id = Listing.objects.get(pk=auction_id)
        if (Watchlist.objects.filter(user=request.user, listing=listing_id)):
            Watchlist.objects.filter(user=request.user, listing=listing_id).delete()
        return HttpResponseRedirect(reverse("watchlist"))
    return HttpResponseRedirect(reverse("watchlist"))

@login_required(login_url='/login')
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlists": Watchlist.objects.filter(user=request.user)
    })

@login_required(login_url='/login')   
def comment(request, auction_id):
    if (request.method == "POST"):
        form = commentForm(request.POST)
        listing_id = Listing.objects.get(pk=auction_id)

        if form.is_valid():
            comment = form.cleaned_data["comment"]

            c = Comment(user=request.user, listing=listing_id, comment=comment)

            c.save()

            return HttpResponseRedirect(reverse("auction", kwargs={'auction_id': auction_id}))
        
        return HttpResponseRedirect(reverse("auction", kwargs={'auction_id': auction_id}))        
    else:
        return HttpResponseRedirect(reverse("auction", kwargs={'auction_id': auction_id}))
        
@login_required(login_url='/login')
def bid(request, auction_id):
    if (request.method == "POST"):
        form = bidForm(request.POST)
        listing_id = Listing.objects.get(pk=auction_id)

        if form.is_valid():
            price = form.cleaned_data["price"]

            # Enter the bid into the database if there is no outstanding bids out there
            if not Bid.objects.filter(listing=listing_id):
                # The bid must be higher than the intial price 
                if not price > listing_id.price:
                    return render(request, "auctions/bidError.html", {
                    "auction": Listing.objects.get(id=auction_id)
                })
                b = Bid(user=request.user, listing=listing_id, price=price)
                b.save()

                return HttpResponseRedirect(reverse("auction", kwargs={'auction_id': auction_id}))
            
            if ( all(price > n.price for n in Bid.objects.filter(listing=listing_id)) and (price > Listing.objects.get(id=auction_id).price)):
                b = Bid(user=request.user, listing=listing_id, price=price)
                b.save()

                return HttpResponseRedirect(reverse("auction", kwargs={'auction_id': auction_id}))
            return render(request, "auctions/bidError.html", {
                "auction": Listing.objects.get(id=auction_id)
            })
        return HttpResponseRedirect(reverse("auction", kwargs={'auction_id': auction_id}))
    else:
        return HttpResponseRedirect(reverse("auction", kwargs={'auction_id': auction_id}))

@login_required(login_url='/login')
def close(request, auction_id):
    if request.method == "POST":
        listing_id = Listing.objects.get(id=auction_id)
        if str(request.user) == str(listing_id.seller):
            current_bids = Bid.objects.filter(listing=listing_id)
            highest_bid = listing_id.price
            for current_bid in current_bids:
                if current_bid.price > highest_bid:
                    highest_bid = current_bid.price
                
            winner = Bid.objects.get(listing=listing_id, price=highest_bid)

            listing_id.delete()
            return render(request, "auctions/winner.html",{
                "winner": winner.user,
                "auction": listing_id
            })
        return HttpResponseRedirect(reverse("auction", kwargs={'auction_id': auction_id}))
    return HttpResponseRedirect(reverse("auction", kwargs={'auction_id': auction_id}))

def category(request, category):
    auctions = Listing.objects.filter(category=category)
    return render(request, "auctions/category.html", {
        "title": category,
        "auctions": auctions
    })

def categories(request):
    Fashion = Listing.objects.filter(category="Fashion")
    Toys = Listing.objects.filter(category="Toys")
    Electronics = Listing.objects.filter(category="Electronics")
    Home = Listing.objects.filter(category="Home")
    Sports = Listing.objects.filter(category="Sports")
    Music = Listing.objects.filter(category="Music")
    Others = Listing.objects.filter(category="Music")

    return render(request, "auctions/categories.html", {
        "Fashion": Fashion,
        "Toys": Toys,
        "Electronics": Electronics,
        "Home": Home,
        "Sports": Sports,
        "Music": Music,
        "Others": Others
    })