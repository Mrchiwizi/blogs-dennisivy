from pydoc_data.topics import topics
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . models import Room, Topic, Message
from django.db.models import Q
from . forms import RoomForm, MessageUpdateForm, UserForm
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

    topics = Topic.objects.all()[0:5]

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)



# search here
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
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     form.save()
        return redirect('home')

    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)



@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        # if form.is_valid():
        #     form.save()
        return redirect("home")

    context = {'form':form, 'topics':topics, 'room':room}
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

    context = {'form': form}
    return render(request, 'base/edit_message.html', context)




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




def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        
        if form.is_valid:
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form':form}
    return render(request, 'base/update-user.html', context)




def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics = Topic.objects.filter(name__icontains=q)

    context = {'topics':topics}
    return render(request, 'base/topics.html', context)



def activityPage(request):
    room_messages = Message.objects.all()

    context = {'room_messages':room_messages}
    return render(request, 'base/activity.html', context)