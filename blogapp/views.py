from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm
from .forms import CommentForm
from django.contrib import messages
from .forms import UserRegisterForm

# Create your views here.

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blogapp/home.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'blogapp/create_post.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Creates the user
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('/accounts/login/')
    else:
        form = UserRegisterForm()
    return render(request, 'blogapp/signup.html', {'form': form})

def post_detail(request, id):
    post = Post.objects.get(id=id)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post_detail', id=id)
    else:
        form = CommentForm()

    return render(request, 'blogapp/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })
@login_required
def edit_post(request, id):
    post = Post.objects.get(id=id)

    if post.author != request.user:
        return redirect('home')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blogapp/create_post.html', {'form': form})

@login_required
def delete_post(request, id):
    post = Post.objects.get(id=id)

    if post.author == request.user:
        post.delete()

    return redirect('home')

@login_required
def like_post(request, id):
    post = Post.objects.get(id=id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)  # unlike
    else:
        post.likes.add(request.user)  # like

    return redirect('home')