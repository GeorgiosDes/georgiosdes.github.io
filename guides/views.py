import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Game, Guide, New, GuideSection, NewSection, GuideComment, NewComment


def index(request):
    news = New.objects.all().order_by("-date_created")[:2]
    guides = Guide.objects.all().order_by("-date_created")[:5]

    return render(request, "guides/index.html", {
        "news": news,
        "guides": guides
    })


def profile(request):
    return render(request, "guides/profile.html")


@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST["old-password"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Ensure current password is correct
        if not check_password(old_password, request.user.password):
            return render(request, "guides/change_password.html", {
                "message_old_password": "Old password is incorrect.",
                "password": password,
                "confirmation": confirmation
            })
        
        # Ensure password matches confirmation
        elif password != confirmation:
            return render(request, "guides/change_password.html", {
                "message_new_password": "Passwords must match.",
                "current_password": old_password
            })
        
        # Change user password
        else:
            user = User.objects.get(username=request.user)
            user.set_password(password)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "guides/change_password.html")


@login_required
def change_email(request):
    if request.method == "POST":
        old_email = request.POST["old-email"]
        email = request.POST["email"]
        confirmation = request.POST["confirmation"]
        user = User.objects.get(username=request.user)

        # Ensure current email is correct
        if user.email != old_email:
            return render(request, "guides/change_email.html", {
                "message_current_email": "Current email is incorrect",
                "email": email,
                "confirmation": confirmation
            })
        
        # Ensure new email matches confirmation
        elif email != confirmation:
            return render(request, "guides/change_email.html", {
                "message_new_email": "Emails must match.",
                "old_email": old_email
            })
        
        # Change email
        else:
            user.email = email
            user.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "guides/change_email.html")


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
            return render(request, "guides/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "guides/login.html")


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
            return render(request, "guides/register.html", {
                "message_password": "Passwords must match.",
                "username": username,
                "email": email
            })
        
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "guides/register.html", {
                "message_username": "Username is already taken.",
                "email": email,
                "password": password,
                "confirmation": confirmation
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "guides/register.html")
    

def news(request):
    games = []

    news = New.objects.all().order_by("-date_created")[:6]

    for new in news:
        if new.game not in games:
            games.append(new.game)

    return render(request, "guides/news.html", {
        "games": games,
        "news": news
    })


def guides(request):
    games = Game.objects.all().order_by("-id")
    guides = []

    for game in games:
        latest = Guide.objects.filter(game=game).order_by("-date_created")[:5]
        guides.append((game, latest))

    return render(request, "guides/guides.html", {
        "games": games,
        "guides": guides
    })


def show_more(request, type, game_id, page, amount, sort):
    if type == "guide":
        if sort == "latest":
            paginator = Paginator(Guide.objects.filter(game=game_id).order_by("-date_created"), amount)
            try:
                guides = paginator.page(page)
            except PageNotAnInteger:
                guides = paginator.page(1)
            except EmptyPage:
                guides = paginator.page(paginator.num_pages)

            pagination = {
                "has_next": guides.has_next(),
            }

            return JsonResponse({
            "guides": [guide.serialize() for guide in guides],
            "pagination": pagination
            }, safe=False)
        
        elif sort == "oldest":
            paginator = Paginator(Guide.objects.filter(game=game_id), amount)
            try:
                guides = paginator.page(page)
            except PageNotAnInteger:
                guides = paginator.page(1)
            except EmptyPage:
                guides = paginator.page(paginator.num_pages)

            pagination = {
                "has_next": guides.has_next(),
            }

            return JsonResponse({
            "guides": [guide.serialize() for guide in guides],
            "pagination": pagination
            }, safe=False)


@login_required
def create(request, type):
    games = Game.objects.all()
    if request.method == "POST":
        game_id = request.POST["game_id"]
        game = Game.objects.get(id=game_id)
        title = request.POST["title"]
        description = request.POST["description"]
        video_link = request.POST["video-link"]

        if type == "guide":
            guide = Guide(user=request.user, game=game, title=title, description=description, video_link=video_link)
            guide.save()

            count = 0
            while f"section{count}-title" in request.POST:
                section_title = request.POST[f"section{count}-title"]
                section_content = request.POST[f"section{count}-content"]
                section_image = request.FILES.get(f"section{count}-image")

                if section_title and section_content:
                    section = GuideSection(guide=guide, title=section_title, content=section_content, image=section_image)
                    section.save()

                count += 1

            return HttpResponseRedirect(reverse("full_guide", kwargs={"guide_id": guide.id}))

        if type == "news":
            new = New(user=request.user, game=game, title=title, description=description, video_link=video_link)
            new.save()

            count = 0
            while f"section{count}-title" in request.POST:
                section_title = request.POST[f"section{count}-title"]
                section_content = request.POST[f"section{count}-content"]
                section_image = request.FILES.get(f"section{count}-image")

                if section_title and section_content:
                    section = NewSection(new=new, title=section_title, content=section_content, image=section_image)
                    section.save()

                count += 1

            return HttpResponseRedirect(reverse("full_new", kwargs={"new_id": new.id}))
    else:
        user = User.objects.get(username=request.user)
        if user.content_creator == 1:
            return render(request, "guides/create.html", {
                "games": games,
                "type": type
            })
        
        else:
            return HttpResponseRedirect(reverse("profile"))

    

def full_guide(request, guide_id):
    guide = get_object_or_404(Guide, pk=guide_id)
    sections = GuideSection.objects.filter(guide=guide)
    comments = GuideComment.objects.filter(guide=guide).order_by("-date_created")
    return render(request, "guides/full_guide.html", {
        "guide": guide,
        "sections": sections,
        "comments": comments
    })


def full_new(request, new_id):
    new = get_object_or_404(New, pk=new_id)
    sections = NewSection.objects.filter(new=new)
    comments = NewComment.objects.filter(new=new).order_by("-date_created")
    return render(request, "guides/full_new.html", {
        "new": new,
        "sections": sections,
        "comments": comments
    })


def sort_guides(request, sort, game_id):
    game = Game.objects.get(pk=game_id)

    if sort == "latest":
        guides = Guide.objects.filter(game=game_id).order_by("-date_created")
        more = False

        if guides.count() > 10:
            latest = guides[:10]
            more = True
        else:
            latest = guides

        return render(request, "guides/sort_guides.html", {
            "game": game,
            "guides": latest,
            "more": more,
            "sort": sort,
            "order": "Latest &darr;"
        })
    
    if sort == "oldest":
        guides = Guide.objects.filter(game=game_id)
        more = False

        if guides.count() > 10:
            latest = guides[:10]
            more = True
        else:
            latest = guides

        return render(request, "guides/sort_guides.html", {
            "game": game,
            "guides": latest,
            "more": more,
            "sort": sort,
            "order": "Oldest &uarr;"
        })
    

def sort_news(request, sort, game_id):
    game = Game.objects.get(pk=game_id)

    if sort == "latest":
        news = New.objects.filter(game=game_id).order_by("-date_created")[:6]

        return render(request, "guides/sort_news.html", {
            "game": game,
            "news": news
        })
    

def search(request):
    query = request.GET.get("q")
    guides_results = []
    news_results = []

    if query:
        guides_results = Guide.objects.filter(title__contains=query).order_by("-date_created")
        news_results = New.objects.filter(title__contains=query).order_by("-date_created")

    return render(request, "guides/search.html", {
        "guides_results": guides_results,
        "news_results": news_results,
        "query": query
    })


@csrf_exempt
@login_required
def comment(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    data = json.loads(request.body)
    type = data.get("type", "")
    content = data.get("content", "")
    id = data.get("id", "")

    if type == "guide":

        try:
            guide = Guide.objects.get(pk=id)
        except Guide.DoesNotExist:
            return JsonResponse({"error": "Guide does not exist."}, status=404)
        
        add_comment = GuideComment(user=request.user, guide=guide, comment=content)
        add_comment.save()
        return JsonResponse({
            "message": "Commented successfully.",
            "comment": add_comment.comment
            }, status=201)
    
    if type == "new":

        try:
            new = New.objects.get(pk=id)
        except New.DoesNotExist:
            return JsonResponse({"error": "New does not exist."}, status=404)
        
        add_comment = NewComment(user=request.user, new=new, comment=content)
        add_comment.save()
        return JsonResponse({
            "message": "Commented successfully.",
            "comment": add_comment.comment
            }, status=201)