from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Category
from . import forms
from django.contrib import messages


def index(request, category_id=None):
    if category_id is not None:
        active_listings = Listing.objects.filter(active=True, category=category_id)
    else:
        active_listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "active_listings": active_listings,
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
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


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
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == "GET":
        create_listing_form = forms.Create_listing()
        return render(request, "auctions/create_listing.html", {
            "create_listing_form": create_listing_form,
        })
    elif request.method == "POST":
        form = forms.Create_listing(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            bid = form.cleaned_data["bid"]
            image = form.cleaned_data["image"]
            category_name = form.cleaned_data["category"]

            category, created = Category.objects.get_or_create(category=category_name)
            new_listing = Listing(title=title, description=description, bid=bid, image=image, category=category, user=request.user)
            new_listing.save()
            return HttpResponseRedirect(reverse("auctions:index"))
        

def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {
        "categories": categories,
    })


def watchlist(request):
    listings = Listing.objects.filter(watchlist=request.user)
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
    })


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bid = Bid.objects.filter(listing=listing).order_by("-bid").first()
    bid_count = Bid.objects.filter(listing=listing).count()  # Get the count of bids
    comments = Comment.objects.filter(listing=listing)

    if request.method == "POST":
        if 'add_watchlist' in request.POST:
            listing.watchlist.add(request.user)
            return HttpResponseRedirect(reverse('auctions:listing', args=(listing.id,)))
        if 'remove_watchlist' in request.POST:
            listing.watchlist.remove(request.user)
            return HttpResponseRedirect(reverse('auctions:listing', args=(listing.id,)))
        if 'bid' in request.POST:
            new_bid = request.POST["bid"]
            if new_bid == "":
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bid": bid,
                    "bid_count": bid_count,  # Pass the bid count to the template
                    "message": "You must enter a bid."
                })
            elif float(new_bid) <= float(listing.bid):
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bid": bid,
                    "bid_count": bid_count,  # Pass the bid count to the template
                    "message": "Your bid must be higher than the current highest bid."
                })
            elif bid is None:
                new_bid = Bid(bid=new_bid, user=request.user, listing=listing)
                new_bid.save()
                return HttpResponseRedirect(reverse('auctions:listing', args=(listing.id,)))
            elif float(new_bid) <= float(bid.bid):
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bid": bid,
                    "bid_count": bid_count,  # Pass the bid count to the template
                    "message": "Your bid must be higher than the current highest bid."
                })
        if 'close_listing' in request.POST:
            listing.active = False
            listing.save()
            return HttpResponseRedirect(reverse('auctions:listing', args=(listing.id,)))
        if 'comment' in request.POST:
            new_comment = request.POST["comment"]
            new_comment = Comment(comment=new_comment, user=request.user, listing=listing)
            new_comment.save()
            return HttpResponseRedirect(reverse('auctions:listing', args=(listing.id,)))
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid": bid,
        "bid_count": bid_count,  # Pass the bid count to the template
        "comments": comments,
    })
