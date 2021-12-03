from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post, Follower, Like


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
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


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
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")


def add_post(request):
    print(request)
    if request.method == "POST":
        user = User.objects.get(pk=request.user.id)
        post = Post.objects.create(title=request.POST.get('new_post_title'),
            content=request.POST.get('new_post_content'),
            author=request.user)
        user.posts.add(post)
        return JsonResponse({'valid': 1,
                                'msg': 'success'}, status=201)


def update_post(request):
    if request.method == "POST":
        user = User.objects.get(pk=request.user.id)
        post = Post.objects.get(pk=request.POST['post_id'])
        if post.author == user:
            post.content = request.POST['content']
            post.save()
            return JsonResponse({'valid': 1,
                                    'msg': 'success',
                                    'content': post.content},
                                status=201)
        return JsonResponse({'valid': 0,
                                'msg': 'error',},
                            status=400)


def liking(request):
    if request.method == "POST" and request.user.is_authenticated:
        post = Post.objects.get(id=request.POST.get('post_id'))
        user = User.objects.get(pk=request.user.id)
        like = Like.objects.filter(user=user, post=post)
        if post.author != user:
            if like:
                like.delete()
            else:
                print("test2")
                new_like = Like.objects.create(user=user, post=post)
                post.likes.add(new_like)
            return JsonResponse({'valid': 1,
                                    'likes_number': Like.objects.filter(post=post).count(),
                                    'msg': 'success'}, status=201)
    return JsonResponse({'valid': 0,
                            'msg': 'error'}, status=400)


def get_posts(request):
    page_number = 3
    if request.user.is_authenticated:
        if request.POST.get('filter') == 'user':
            posts = Post.objects.filter(author=request.user).order_by('-id')
        elif request.POST.get('filter') == 'following':
            followings = Follower.objects.filter(follower=request.user)
            following_list = []
            for following in followings:
                following_list.append(following.user)
            posts = Post.objects.filter(author__in=following_list)
        else:
            posts = Post.objects.all().order_by('-id')
        last_page = posts.count() // page_number + 1
        paginator = Paginator(posts, page_number)
        page_number = request.POST.get('page_number')
        page_obj = paginator.get_page(page_number)
        posts_number = posts.count()
        posts = return_data_in_post(page_obj)
        return JsonResponse({'posts': posts,
                                'current_page': page_number,
                                'last_page': last_page, },
                                status=201)
    return JsonResponse({'posts': None},
                                status=400)


def get_profile(request):
    if request.user.is_authenticated:
        # if request.user.id == request.GET.get('profile_id'):
        try:
            profile_user = User.objects.get(pk=request.GET.get('id'))
            followers_count = Follower.objects.filter(user=profile_user).count()
            subscribes_count = Follower.objects.filter(follower=profile_user).count()
            profile_posts = return_data_in_post(Post.objects.filter(author=profile_user.id).order_by('-id'))
            is_follower = Follower.objects.filter(user=profile_user, follower=request.user).exists()

            return render(request, "network/profile.html", {
                'profile_username': profile_user.username,
                'profile_user_id': profile_user.id,
                'followers_count': followers_count,
                'subscribes_count': subscribes_count,
                'profile_posts': profile_posts,
                'is_follower': is_follower,
            })
        except:
            HttpResponseRedirect(reverse('network:login'))
    return HttpResponseRedirect(reverse('network:login'))


def return_data_in_post(default_posts):
    posts = []
    for post in default_posts:
        likes_number =  Like.objects.filter(post=post).count()
        posts.append({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author.username,
            'author_id': post.author.id,
            'modificate_date': post.modificate_date,
            'likes_number': likes_number,
        })
    return posts


def following(request):
    if request.method == "POST" and request.user.is_authenticated:
        follow_user = User.objects.get(id=request.POST.get('follow_user_id'))
        if request.user.id != follow_user.id:
            follower_exist = Follower.objects.filter(user=follow_user, follower=request.user)
            if follower_exist.exists():
                follower_exist.delete()
            else:
                follower = Follower.objects.create(user=follow_user, follower=request.user)
                follow_user.following.add(follower)
            return JsonResponse({'valid': 1,
                                    'followers_count': Follower.objects.filter(user=follow_user).count(),
                                    'msg': 'success'}, status=201)
    return JsonResponse({'valid': 0,
                            'msg': 'error'}, status=400)


def get_following_list(request):
    if request.user.is_authenticated:
        followings = Follower.objects.filter(follower=request.user)
        following_list = []
        for following in followings:
            following_list.append(User.objects.get(id=following.user.id).id)
        return JsonResponse({'valid': 1,
                                'following_list': following_list,
                                'msg': 'success'}, status=201)
    return JsonResponse({'valid': 0,
                            'msg': 'error'}, status=400)