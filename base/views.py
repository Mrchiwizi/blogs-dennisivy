from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . models import Room, Topic, Message
from django.db.models import Q
from . forms import RoomForm, MessageUpdateForm
from django.http import HttpResponseRedirect


# Create your views here.
def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Invalid Username')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username Or Password mismatch')

    context = {'page':page}
    return render(request,'base/login_register.html', context)



def logoutUser(request):
    logout(request)
    return redirect('home')



def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'There was a problem registering this user')


    context = {'form':form}
    return render(request, 'base/login_register.html', context)



def home(request):

    # *********CHIWIZI VERSION*********
    # q = ''
    # if request.method == 'GET':
    #     if request.GET.get('q') != None:
    #         print(request.GET.get('q'))
    #         q = request.GET.get('q')
    #     else:
    #         ''
    # else:
        
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    room_count = rooms.count()

    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    topics = Topic.objects.all()

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)



def room(request, pk):
    room = Room.objects.get(id=pk)

    room_messages = room.message_set.all().order_by('-created')

    participants = room.participants.all()

    if request.method == 'POST':
        user = request.user
        body = request.POST.get('body')
        room = room

        message = Message.objects.create(user=user, body=body, room=room)

        room.participants.add(request.user)

        return redirect('room', pk=room.id)

    context = {'room':room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)



@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form':form}
    return render(request, 'base/room_form.html', context)



@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        form = RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")

    context = {'form':form}
    return render(request, 'base/room_form.html', context)



def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect("home")

    context = {'obj':room}
    return render(request, 'base/delete.html',context)



def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj':message})




def editMessage(request, pk):
    roomf = Message.objects.get(id=pk)
    # room = Room.objects.get(id=pk)
    # roomf = room.message(id=pk)
    form = MessageUpdateForm(instance=roomf)

    if request.method == 'POST':
        form = MessageUpdateForm(request.POST, instance=roomf)
        print(request.POST.get('form'))

        if form.is_valid():
            form.save()
            return redirect('room', pk=roomf.room.id)
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            # return redirect(request.META.get('HTTP_REFERER'))

    context = {'form': form}
    return render(request, 'base/edit-room.html', context)




def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {
        'user': user, 
        'rooms':rooms, 
        'room_messages':room_messages, 
        'topics':topics
        }
    return render(request, 'base/profile.html', context)