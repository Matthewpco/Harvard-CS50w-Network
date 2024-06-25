import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.http import JsonResponse
from .models import User, Post, Followers, Likes

class NewPostForm(forms.Form):
    content = forms.CharField(
        label='Content',
        widget=forms.TextInput(attrs={'size': 100})
    )

def edit(request, id):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    # Edit db object and save
    data = json.loads(request.body)
    if data == "":
        return JsonResponse({
            "error": "No Message."
        }, status=400)
    
    try:
        editPost = Post.objects.get(pk=id)
        editPost.content = data["content"]
        editPost.save()
        return JsonResponse({"message": "Post updated successfully.", "data": data["content"]}, status=201)
    except:
        return JsonResponse({
            "error": "No Message."
        }, status=400)

def like(request, id):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    # Edit db object and save
    data = json.loads(request.body)
    if "newValue" not in data:
        return JsonResponse({
            "error": "No Message."
        }, status=400)
    
    try:
        # Get the values needed
        data = data["newValue"]
        currentUser = User.objects.get(pk=request.user.id)
        post = Post.objects.get(pk=id)

        # Check if like already exists
        if Likes.objects.filter(author=currentUser, post=post).exists():
            return JsonResponse({"message": "You have already liked this post"}, status=400)
        
        updatedLike = Likes(author=currentUser, post=post)
        updatedLike.save()
        return JsonResponse({"message": "Likes updated"}, status=201)
    except:
        return JsonResponse({
            "error": "No Message."
        }, status=400)

def unlike(request, id):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    try:
        
        # Get the current user and the post by their ids
        currentUser = User.objects.get(pk=request.user.id)
        post = Post.objects.get(pk=id)

        # Check if a 'Like' object exists for the current user and post then delete it
        if Likes.objects.filter(author=currentUser, post=post).exists():
            updatedLike = Likes.objects.get(author=currentUser, post=post)
            updatedLike.delete()
            return JsonResponse({"message": "You have unliked this post"}, status=201)
        
        # If a 'Like' object does not exist, return an error message
        return JsonResponse({"message": "You cannot unlike a post you have not liked"}, status=400)
    
    except:
        return JsonResponse({
            "error": "No Message."
        }, status=400)


def index(request):
    # Get all posts ordered by oldest
    posts = Post.objects.all().order_by('-timestamp')

    # Filter out posts that current user likes to send to template
    user_likes = Likes.objects.filter(author=request.user).values_list('post', flat=True)

    # Split posts into multiple pages with default paginator
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": posts,
        'page_obj': page_obj,
        "form": NewPostForm(),
        "user_likes": user_likes
    })

def create(request):
    if request.method == "POST":

        # Get the form fields from submission
        content = request.POST["content"]

        # Get logged in user that made request
        currentUser = request.user

        # Make newpost db object and save
        newPost = Post(content=content, author=currentUser)
        newPost.save()

        return HttpResponseRedirect(reverse("index"))

def profile(request, author):

    # Get profile user
    profile_user = User.objects.get(pk=author)

    # Get follows and following for profile user
    follows = Followers.objects.filter(follows=profile_user)
    following = Followers.objects.filter(following=profile_user)

    try:
        # Filter if current user is follower
        requestUserFollows = following.filter(follows=User.objects.get(pk=request.user.id))
        if len(requestUserFollows) > 0:
            isFollower = True
        else:
            isFollower = False
    except:
        isFollower = False

    # Get posts for profile user
    posts = Post.objects.filter(author=profile_user).order_by('-timestamp')

    # Set default paginator settings
    paginator = Paginator(posts, 10) # Show 2 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "posts": posts,
        "profile_user": profile_user,
        "follows": follows,
        "following": following,
        "isFollower": isFollower,
        "page_obj": page_obj
    })

def follow(request):
    # Extract the username of the user to be followed from the POST data
    followRequester = request.POST['followrequester']

    # Retrieve the User object for the current user
    currentUser = User.objects.get(pk=request.user.id)

    # Retrieve the User object for the user to be followed
    followRequesterData = User.objects.get(username=followRequester)

    # Create a new Followers object and save
    f = Followers(follows=currentUser, following=followRequesterData)
    f.save()

    # Get the id of the user to be followed and redirect to their profile
    user_id = followRequesterData.id
    return HttpResponseRedirect(reverse('profile', kwargs={'author': user_id}))

    
def unfollow(request):
    # Extract the username of the user to be followed from the POST data
    followRequester = request.POST['followrequester']

    # Retrieve the User object for the current user
    currentUser = User.objects.get(pk=request.user.id)

    # Retrieve the User object for the user to be followed
    followRequesterData = User.objects.get(username=followRequester)

    # Get the object that matches the current user to profile user and delete
    f = Followers.objects.get(follows=currentUser, following=followRequesterData)
    f.delete()
    
    # Get the id of the user to be followed and redirect to their profile
    user_id = followRequesterData.id
    return HttpResponseRedirect(reverse(profile, kwargs={'author': user_id}))
    
def following(request):
    # Retrieve the User object for the current user
    currentUser = User.objects.get(pk=request.user.id)

    # Get all the follows for the current user and loop through them
    f = Followers.objects.filter(follows=currentUser)
    following_users = [follower.following for follower in f]

    # get posts that are authored by the users that the current user is following
    posts = Post.objects.filter(author__in=following_users).order_by('-timestamp')

    # Setup the default paginator
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts": posts,
        "page_obj": page_obj
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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


