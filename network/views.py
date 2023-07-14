import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Community, Like, Comment


def index(request):
    return render(request, "network/index.html")


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)

        # Create a community profile
        community = Community(user=user)
        community.save()
        
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
@login_required
def new_post(request):

    # New posts must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    data = json.loads(request.body)
    content = data.get("content", "")
    username = data.get("username", "")
    post = Post(user=request.user, username=username, content=content)
    post.save()

    return JsonResponse({"message": "Posted Successfully."}, status=201)
    

def load_posts(request, page):
    if request.user.is_authenticated:
        likes = Like.objects.filter(user=request.user).values_list("post__id", flat=True)
    else:
        likes = []

    comments = Comment.objects.values_list("post__id", "comment", "user__username")

    paginator = Paginator(Post.objects.all().order_by("-date_created"), 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    pagination = {
        "current_page": int(page),
        "total_pages": paginator.num_pages,
        "has_previous": posts.has_previous(),
        "has_next": posts.has_next(),
        "previous_page_number": posts.previous_page_number() if posts.has_previous() else None,
        "next_page_number": posts.next_page_number() if posts.has_next() else None
    }
    
    return JsonResponse({
        "posts": [post.serialize() for post in posts],
        "pagination": pagination,
        "likes": list(likes),
        "comments": list(comments)
        }, safe=False)


def load_profile(request, username, page):
    follow = False
    user = get_object_or_404(User, username=username)

    if request.user.is_authenticated:
        community, created = Community.objects.get_or_create(user=request.user)
        follow = user in community.following.all()
        likes = Like.objects.filter(user=request.user).values_list("post__id", flat=True)
    else:
        likes = []

    comments = Comment.objects.values_list("post__id", "comment", "user__username")

    following = user.community.first().following.count()
    followers = user.community.first().followers.count()

    paginator = Paginator(Post.objects.filter(username=username).order_by("-date_created"), 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    pagination = {
        "current_page": int(page),
        "total_pages": paginator.num_pages,
        "has_previous": posts.has_previous(),
        "has_next": posts.has_next(),
        "previous_page_number": posts.previous_page_number() if posts.has_previous() else None,
        "next_page_number": posts.next_page_number() if posts.has_next() else None
    }

    return JsonResponse({
        "posts": [post.serialize() for post in posts],
        "follow": follow,
        "following": following,
        "followers": followers,
        "pagination": pagination,
        "likes": list(likes),
        "comments": list(comments)
    }, safe=False)


@csrf_exempt
@login_required
def load_following(request, page):
    following = request.user.community.first().following.all()
    likes = Like.objects.filter(user=request.user).values_list("post__id", flat=True)

    comments = Comment.objects.values_list("post__id", "comment", "user__username")

    paginator = Paginator(Post.objects.filter(user__in=following).order_by("-date_created"), 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    pagination = {
        "current_page": int(page),
        "total_pages": paginator.num_pages,
        "has_previous": posts.has_previous(),
        "has_next": posts.has_next(),
        "previous_page_number": posts.previous_page_number() if posts.has_previous() else None,
        "next_page_number": posts.next_page_number() if posts.has_next() else None
    }

    return JsonResponse({
        "posts": [post.serialize() for post in posts],
        "pagination": pagination,
        "likes": list(likes),
        "comments": list(comments)
        }, safe=False)


@csrf_exempt
@login_required
def follow_unfollow(request, action):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    data = json.loads(request.body)
    username = data.get("following", "")
    
    if action == "follow":
        following = User.objects.get(username=username)
        community_following = Community.objects.get(user=request.user)
        community_following.following.add(following)

        follower = request.user
        community_follower = Community.objects.get(user=following)
        community_follower.followers.add(follower)

        followers = following.community.first().followers.count()
        return JsonResponse({
            "message": "Followed successfully.",
            "followers": followers,
            "follow": True
            }, status=201)
    
    elif action == "unfollow":
        following = User.objects.get(username=username)
        community_following = Community.objects.get(user=request.user)
        community_following.following.remove(following)

        follower = request.user
        community_follower = Community.objects.get(user=following)
        community_follower.followers.remove(follower)

        followers = following.community.first().followers.count()
        return JsonResponse({
            "message": "Unfollowed successfully.",
            "followers": followers,
            }, status=201)
    
    else:
        return JsonResponse({"error": "Invalid Action."}, status=400)


@csrf_exempt
@login_required
def edit_post(request, post_id):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    data = json.loads(request.body)
    content = data.get("content", "")
    
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post does not exist."}, status=404)
    
    # User can only edit his own posts
    if request.user == post.user:
        post.content = content
        post.edited = True
        post.save()
    else:
        return JsonResponse({"error": "You can only edit your posts."}, status=400)

    return JsonResponse({
        "message": "Post edited successfully.",
        "edited": True
        }, status=201)


@csrf_exempt
@login_required
def like_post(request, action):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    data = json.loads(request.body)
    post = data.get("post_id", "")

    if action == "like":
        post = Post.objects.get(pk=post)
        post.likes += 1
        post.save()
        liked_post, created = Like.objects.get_or_create(user=request.user)
        liked_post.post.add(post)
        return JsonResponse({
            "message": "Liked post successfully.",
            "likes": post.likes,
            "ok": True
            }, status=201)
    
    elif action == 'unlike':
        post = Post.objects.get(pk=post)
        post.likes -= 1
        post.save()
        liked_post = Like.objects.get(user=request.user)
        liked_post.post.remove(post)
        return JsonResponse({
            "message": "Liked post successfully.",
            "likes": post.likes,
            "ok": True
            }, status=201)
    
    else:
        return JsonResponse({"error": "Invalid Action."}, status=400)
    

@csrf_exempt
@login_required
def comment(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    data = json.loads(request.body)
    content = data.get("content", "")
    post_id = data.get("post_id", "")

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post does not exist."}, status=404)
    
    add_comment = Comment(user=request.user, post=post, comment=content)
    add_comment.save()
    return JsonResponse({
        "message": "Commented successfully.",
        "comment": add_comment.comment,
        }, status=201)