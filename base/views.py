from django.shortcuts import redirect, render
from django.db.models import Q

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from django.http import HttpRequest

from .models import Room, Topic
from .forms import RoomForm

# Create your views here.

def login_page(req: HttpRequest):
    page = 'login'

    if req.user.is_authenticated:
        return redirect('home')

    if req.method == 'POST':
        username = req.POST.get('username')
        password = req.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(req, 'User does not exist')

        user = authenticate(request=req, username=username, password=password)

        if user is not None:
            login(req, user)
            return redirect('home')
        else:
            messages.error(req, 'Username OR password does not exist')

    context = { 'page': page }

    return render(req, 'base/login_register.html', context)

def register_page(req: HttpRequest):
    page = 'register'
    form = UserCreationForm()

    if req.method == 'POST':
        form = UserCreationForm(req.POST)

        if form.is_valid():
            user: User = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            login(req, user)

            return redirect('home')
        else:
            messages.error(req, 'An error occurred during registration')

    context = { 'page': page, 'form': form }

    return render(req, 'base/login_register.html', context)

def logout_action(req: HttpRequest):
    logout(req)
    
    return redirect('home')

def home(req: HttpRequest):
    q = req.GET.get('q') or ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    room_count = rooms.count()

    topics = Topic.objects.all()

    context = { 'rooms': rooms, 'topics': topics, 'room_count': room_count }

    return render(req, 'base/home.html', context)

def room(req, pk):
    room = Room.objects.get(id=pk)
    
    context = { 'room': room }

    return render(req, 'base/room.html', context)

@login_required(login_url='login')
def create_room(req: HttpRequest):
    form = RoomForm()
    context = { 'form': form }

    if req.method == 'POST':
        form = RoomForm(req.POST)
        
        if form.is_valid():
            form.save()

            return redirect('home')

    return render(req, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(req: HttpRequest, pk: str):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if req.user != room.host:
        messages.error(req, 'You don\'t have permition to edit this room')
        return redirect('home')

    if req.method == 'POST':
        form = RoomForm(req.POST, instance=room)

        if form.is_valid():
            form.save()

            return redirect('home')
            
    context = { 'form': form }
    return render(req, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(req: HttpRequest, pk: str):
    room = Room.objects.get(id=pk)

    if req.user != room.host:
        messages.error(req, 'You don\'t have permition to delete this room')
        return redirect('home')

    if req.method == 'POST':
        room.delete()

        return redirect('home')

    return render(req, 'base/delete_confirm.html', { 'obj': room })